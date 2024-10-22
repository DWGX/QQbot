import asyncio
import botpy
import logging
import time
import json
import os
import yaml
from botpy.message import Message
from Assist import Assist
from Boss import Boss
from botpy.errors import ServerError

from Gamebling import Gambling

# 配置日志记录，仅输出到控制台
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DwgxBot")


class DwgxBot(botpy.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_command_time = {}
        self.cooldown = {'bet': 5, 'balance': 1, 'other': 3}
        self.config_file = 'config.yaml'
        self.data_file = 'data.json'
        self.data_lock = asyncio.Lock()
        self.admin_ids = ['1062295115427866629']  # 替换为实际管理员ID
        self.load_config()
        self.load_data()

        # 先实例化 Gambling 再传递给 Boss
        self.Gambling = Gambling(
            user_data=self.data['user_data'],
            game_history=self.data['game_history'],
            save_data=self.save_data
        )

        # 实例化 Boss，传递 gambling 实例
        self.Boss = Boss(
            data=self.data,
            user_data=self.data['user_data'],
            admin_ids=self.admin_ids,
            save_data=self.save_data,
            gambling=self.Gambling
        )

        # 实例化 Assist，传递 boss_id
        self.Assist = Assist(
            user_data=self.data['user_data'],
            game_history=self.data['game_history'],  # 修正为 self.data['game_history']
            admin_ids=self.admin_ids,
            save_data=self.save_data,
            boss_id=self.Boss.boss_id
        )
        self.Assist.client = self

        # 初始化老板账户，如果尚未存在
        if self.Boss.boss_id:
            if self.Boss.boss_id not in self.data['user_data']:
                self.data['user_data'][self.Boss.boss_id] = {'username': '老板', 'points': 10000}
                asyncio.create_task(self.save_data())
                logger.info(f"已为老板 {self.Boss.boss_id} 创建账户，初始代币：10000")
            else:
                logger.info(f"老板 {self.Boss.boss_id} 的账户已存在。")

    def load_config(self):
        if not os.path.exists(self.config_file):
            logger.error("配置文件 config.yaml 不存在。请创建并填写 appid 和 secret。")
            exit(1)
        with open(self.config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        self.appid = config.get('appid')
        self.secret = config.get('secret')

        if not self.appid or not self.secret:
            logger.error("配置文件 config.yaml 缺少 appid 或 secret。请填写完整。")
            exit(1)

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                logger.info("数据文件加载成功。")
            except json.JSONDecodeError:
                logger.error(f"{self.data_file} 格式错误，重新初始化。")
                self.data = {"boss_id": None, "user_data": {}, "game_history": {}}
                self.save_data_sync()  # 使用同步保存方法
        else:
            self.data = {"boss_id": None, "user_data": {}, "game_history": {}}
            self.save_data_sync()  # 使用同步保存方法
            logger.info("未找到数据文件，初始化为空。")

    def save_data_sync(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)
            logger.info("数据文件保存成功。")
        except Exception as e:
            logger.exception("保存数据文件时发生错误。")

    async def save_data(self):
        async with self.data_lock:
            try:
                with open(self.data_file, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, ensure_ascii=False, indent=4)
                logger.info("数据文件保存成功。")
            except Exception as e:
                logger.exception("保存数据文件时发生错误。")

    async def on_at_message_create(self, message: Message):
        content = message.content.strip()
        user_id = str(message.author.id)
        bot_mention = f"<@!{self.robot.id}>"

        if content.startswith(bot_mention):
            content = content[len(bot_mention):].strip()
        else:
            return

        if not content:
            await self.Assist.show_help(message)
            return

        parts = content.split()
        if not parts:
            await self.Assist.show_help(message)
            return

        # 定义控制命令列表（包括 'ye' 和 '查看账户'）
        control_commands = [
            '🎲', 'sh', '查老板', '取消', 'help', 'ping',
            '我当老板', '不当老板', '分析历史', 'ye', '查看账户'
        ]

        # 检查是否为控制命令
        if parts[0].lower() in control_commands:
            command = parts[0].lower()

            if command in ['🎲', 'sh'] and user_id in self.Gambling.active_games:
                await self.Gambling.roll_dice_for_game(message, user_id)
                return

            if command == '查老板':
                await self.Assist.show_current_boss(message)
                return

            if command == '取消':
                cancel_status = self.Gambling.cancel_game(user_id)
                if cancel_status == 'started':
                    await message.reply(content='❌ 游戏已经开始，无法取消。')
                elif cancel_status == 'success':
                    await message.reply(content='✅ 您的游戏已成功取消，代币已退还。')
                elif cancel_status == 'not_started':
                    await message.reply(content='⚠️ 您目前没有进行中的游戏可以取消。')
                return

            if command == 'help':
                await self.Assist.show_help(message)
                return

            if command == 'ping':
                await message.reply(content='🏓 Pong!')
                return

            if command == '我当老板':
                response = await self.Boss.handle_boss_command(user_id, message, action='become')
                await message.reply(content=response)
                return

            if command == '不当老板':
                response = await self.Boss.handle_boss_command(user_id, message, action='leave')
                await message.reply(content=response)
                return

            if command == '分析历史':
                await self.Assist.analyze_history(message)
                return

            if command in ['ye', '查看账户']:
                await self.Assist.show_balance(message)
                return

            # 如果是控制命令但不在上面的处理范围
            await message.reply(content='❓ 未知指令。请输入 帮助 或 help 查看可用指令。')
            return

        # 如果不是控制命令，则解析为多重投入
        # 例如：@机器人 大 100 小单 50 ds 200 11 100
        # 解析为 [{'type': '大', 'amount': 100}, {'type': '小单', 'amount': 50}, ...]
        bets = []
        i = 0
        while i < len(parts):
            bet_type = parts[i]
            if i + 1 < len(parts):
                try:
                    bet_amount = int(parts[i + 1])
                    bets.append({'type': bet_type, 'amount': bet_amount})
                    i += 2
                except ValueError:
                    await message.reply(content='❌ 代币数量应为整数。')
                    return
            else:
                await message.reply(content='❌ 代币数量缺失。')
                return

        if not bets:
            await self.Assist.show_help(message)
            return

        # 处理投入命令
        await self.handle_start_game(message, bets)
        return

    async def handle_start_game(self, message: Message, bets: list):
        user_id = str(message.author.id)
        username = message.author.username

        if not self.Boss.boss_id:
            await message.reply(content='❌ 当前没有老板，无法进行游戏。请等待有人成为老板后再试。')
            return

        if user_id not in self.data['user_data']:
            self.data['user_data'][user_id] = {'username': username, 'points': 1000}
            asyncio.create_task(self.save_data())
            logger.info(f"已为用户 {user_id} 创建新账户，初始代币：1000")

        # 计算总投入金额
        total_bet_amount = sum(bet['amount'] for bet in bets)
        user_points = self.data['user_data'][user_id].get('points', 0)

        if total_bet_amount > user_points:
            logger.info(f"用户 {user_id} 代币不足，尝试投入：{total_bet_amount}，当前代币：{user_points}")
            await message.reply(content=f'❌ 您的代币不足，当前代币：**{user_points}** 个。')
            return

        # 预估总潜在奖励
        potential_winnings = sum(
            self.Gambling.get_multiplier_static(bet['type']) * bet['amount'] for bet in bets if
            self.Gambling.get_multiplier_static(bet['type']) > 0
        )

        boss_points = self.data['user_data'][self.Boss.boss_id]['points']
        if potential_winnings > boss_points:
            await message.reply(content='⚠️ 老板的代币不足以支付您的潜在奖励。请联系管理员。')
            return

        # 扣除用户的代币
        self.data['user_data'][user_id]['points'] -= total_bet_amount

        # 生成期号
        period_number = self.Gambling.generate_unique_period_number()

        # 记录每个投入
        for bet in bets:
            self.Gambling.log_history(
                user_id,
                f"{bet['type']} {bet['amount']} 用于游戏",
                -bet['amount'],
                period_number,  # 传递期号
                bet_amount=bet['amount'],
                role='player'
            )
            logger.info(f"用户 {user_id} 代币 {bet['amount']} （冻结）用于 {bet['type']}")

        # 启动游戏
        self.Gambling.active_games[user_id] = {
            'username': username,
            'bets': bets,
            'start_time': time.time(),
            'period_number': period_number,
            'boss': self.Boss,
            'dice_rolls': []
        }
        logger.info(f"游戏已启动，用户ID：{user_id}，期号：{period_number}，总投入：{total_bet_amount}")
        await message.reply(content='🎲 游戏开始！请发送 🎲 来摇骰子。')

    async def show_balance(self, message: Message):
        user_id = str(message.author.id)

        if user_id not in self.data['user_data']:
            self.data['user_data'][user_id] = {'username': message.author.username, 'points': 1000}
            asyncio.create_task(self.save_data())
            await message.reply(content='✅ 您还没有账户，已自动创建账户并赋予 **1000** 代币。')
            logger.info(f"已为用户 {user_id} 创建新账户，初始代币：1000")
            return

        balance = self.data['user_data'][user_id].get('points', 0)
        username = self.data['user_data'][user_id].get('username', '未知')
        await message.reply(
            content=f"💰 **余额查询** 💰\n\n"
                    f"👤 用户名：**{username}**\n"
                    f"🔑 用户ID：**{user_id}**\n"
                    f"💵 当前代币：**{balance}** 个。"
        )
        logger.info(f"已显示用户 {user_id} 的余额。")

    async def on_ready(self):
        logger.info(f"机器人已连接。ID：{self.robot.id}")


if __name__ == "__main__":
    try:
        if not os.path.exists('config.yaml'):
            logger.error("配置文件 config.yaml 不存在。请创建并填写 appid 和 secret。")
            exit(1)
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        appid = config.get('appid')
        secret = config.get('secret')

        if not appid or not secret:
            logger.error("配置文件 config.yaml 缺少 appid 或 secret。请填写完整。")
            exit(1)

        intents = botpy.Intents(public_guild_messages=True)
        client = DwgxBot(intents=intents)
        logger.info("机器人启动中...")
        client.run(appid=appid, secret=secret)
    except Exception as e:
        logger.exception("机器人启动时发生错误。")
