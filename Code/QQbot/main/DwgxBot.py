# main.py

import logging
import asyncio
import os
import time
import signal

import yaml
import botpy
from botpy.message import Message
from botpy.errors import ServerError

from DataManager import DataManager
from Assist import Assist
from Boss import Boss
from Gambling import Gambling
from RedEnvelope import RedEnvelope

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dwgxbot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DwgxBot")


class DwgxBot(botpy.Client):
    def __init__(self, config, data_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
        self.data_manager = data_manager
        self.data = self.data_manager.data
        self.user_data = self.data['user_data']

        # 初始化各个模块
        self.Boss = Boss(
            data=self.data,
            user_data=self.user_data,
            save_data=self.data_manager.save_data,
            data_manager=self.data_manager
        )

        self.Gambling = Gambling(
            user_data=self.user_data,
            game_history=self.data['game_history'],
            save_data=self.data_manager.save_data,
            boss=self.Boss
        )

        self.Boss.gambling = self.Gambling

        self.Assist = Assist(
            user_data=self.user_data,
            game_history=self.data['game_history'],
            save_data=self.data_manager.save_data,
            boss_id=self.Boss.boss_id,
            userid_to_internal=self.data["userid_to_internal"]
        )
        self.Assist.client = self

        self.RedEnvelope = RedEnvelope(
            data=self.data,
            user_data=self.user_data,
            save_data=self.data_manager.save_data,
            admins=self.config.get('admins', []),
            data_manager=self.data_manager
        )

        # 确保负责人账户存在
        if self.Boss.boss_id:
            if self.Boss.boss_id not in self.user_data:
                asyncio.create_task(self.Boss.create_boss_account())

        self.bot_user = None

    async def on_ready(self):
        try:
            self.bot_user = await self.api.me()
            logger.info(f"机器人 ID: {self.bot_user['id']}")
        except Exception as e:
            logger.exception(f"获取机器人信息时出错: {e}")

    async def on_at_message_create(self, message: Message):
        logger.info(f"收到来自用户 {message.author.id} 的消息: {message.content}")

        content = message.content.strip()
        userid = str(message.author.id)
        username = message.author.username

        # 自动创建或获取用户
        internal_id = await self.data_manager.get_or_create_user(userid, username)
        logger.info(f"为用户 {username} ({userid}) 创建或获取账户，internal_id: {internal_id}")

        # 检查并获取机器人的用户信息
        if not self.bot_user:
            try:
                self.bot_user = await self.api.me()
                logger.info(f"机器人 ID: {self.bot_user['id']}")
            except Exception as e:
                logger.exception(f"获取机器人信息时出错: {e}")
                await message.reply(content='❌ 无法获取机器人的信息，请稍后再试。')
                return

        bot_mention = f"<@!{self.bot_user['id']}>"

        if content.startswith(bot_mention):
            content = content[len(bot_mention):].strip()
        else:
            return

        if not content:
            rules_url = "https://dwgx.top/rules.html"  # 修改为实际的URL
            await message.reply(content=f"📜 **游戏指南**: [点击这里查看指南]({rules_url})")
            return

        control_commands = [
            '🎲', 'sh', '查看老板', 'boss', '取消', 'qx',
            '我当老板', '不当老板', 'ye', '查看账户', '复读',
            'hb', '领取', '撤回', 'sh3', '🎲3', '规则'
        ]
        # 注意：已将 '双' 和 '单' 从控制命令中移除，以便它们作为投入类型被解析

        parts = content.split()
        if parts and parts[0].lower() in [cmd.lower() for cmd in control_commands]:
            command = parts[0].lower()
            logger.info(f"处理命令: {command}")
            if command in ['hb', '领取', '撤回']:
                await self.RedEnvelope.handle_command(message, parts, userid)
                return
            if command in ['🎲', 'sh', 'sh3', '🎲3']:
                await self.handle_dice_command(message, userid, parts)
                return
            if command in ['取消', 'qx']:
                cancel_status = self.Gambling.cancel_game(internal_id)
                if cancel_status == 'started':
                    await message.reply(content='❌ 游戏已经开始，无法取消。')
                elif cancel_status == 'success':
                    await message.reply(content='✅ 您的游戏已成功取消，代币已退还。')
                elif cancel_status == 'not_started':
                    await message.reply(content='⚠️ 您目前没有进行中的游戏可以取消。')
                return
            if command == '我当老板':
                response = await self.Boss.handle_boss_command(userid, 'become')
                await message.reply(content=response)
                return
            if command == '不当老板':
                response = await self.Boss.handle_boss_command(userid, 'leave')
                await message.reply(content=response)
                return
            if command in ['查看老板', 'boss']:
                await self.Assist.show_current_boss(message)
                return
            if command in ['ye', '查看账户']:
                # 确保用户账户存在或自动创建
                # internal_id 已在前面创建
                logger.info(f"用户 {internal_id} 请求查看账户余额。")
                # 检查余额
                await self.Assist.show_balance(message, userid)
                await self.Assist.analyze_history(message)
                return

            if command == '复读':
                if len(parts) < 2:
                    await message.reply(content='❌ 请提供要复读的内容。例如：@机器人 复读 你好！')
                    return
                repeat_message = content[len('复读'):].strip()
                if not repeat_message:
                    await message.reply(content='❌ 请提供要复读的内容。例如：@机器人 复读 你好！')
                    return
                try:
                    await message.reply(content=repeat_message)
                except ServerError:
                    await message.reply(content='❌ 无法发送复读消息，请稍后再试。')
                return
            if command == '规则':
                rules_url = "https://dwgx.top/rules.html"  # 修改为实际的URL
                await message.reply(content=f"📜 **游戏指南**: [点击这里查看指南]({rules_url})")
                return
            # 不再发送帮助信息
            await message.reply(content='❓ 未知指令。请输入 “规则” 查看游戏指南。')
            return

        # 解析投入命令，包括 '双' 和 '单' 以及数字参与格式
        bets = self.parse_bets(content)
        if not bets:
            await message.reply(content='❓ 未知指令。请输入 “规则” 查看游戏指南。')
            return
        await self.handle_start_game(message, bets, internal_id)

    def parse_bets(self, content: str):
        import re

        # 使用纯文本定义投入类型
        bet_types = {
            '双': '双',
            '单': '单',
            's': '双',
            'dan': '单',
            'da': '大',
            'x': '小',
            '大': '大',
            '小': '小',
        }

        # 正则表达式识别 '双', '单' 和 '数字y金额' 格式，如 "双100"、"单200"、"7y300"
        pattern = re.compile(
            r"(?P<type>双|单|大|小|s|dan|da|x|(?P<number>[3-9]|1[0-8]))(?:y)?(?P<amount>\d+)",
            re.IGNORECASE
        )

        matches = pattern.findall(content)
        bets = []
        valid_bet_types = {'双', '单', '大', '小', '3', '4', '5', '6', '7', '8', '9', '10',
                          '11', '12', '13', '14', '15', '16', '17', '18'}

        for match in matches:
            bet_type_raw, number, bet_amount_str = match
            if number:
                # 处理数字投入
                bet_type = number
            else:
                bet_type = bet_types.get(bet_type_raw.lower(), bet_type_raw)

            if bet_type not in valid_bet_types:
                logger.warning(f"无效的投入类型：{bet_type}")
                continue  # 跳过无效的投入类型

            try:
                bet_amount = int(bet_amount_str)
                if bet_amount <= 0:
                    logger.warning(f"无效的投入金额：{bet_amount}")
                    continue
                bets.append({'type': bet_type, 'amount': bet_amount})
            except ValueError:
                logger.warning(f"无法解析的投入金额：{bet_amount_str}")
                continue
        logger.info(f"解析投入: {bets}")
        return bets

    async def handle_start_game(self, message: Message, bets: list, internal_id: str):
        logger.info(f"用户 {internal_id} 开始游戏，投入: {bets}")
        username = message.author.username
        userid = str(message.author.id)
        # 创建或获取用户账户
        # internal_id 已在 on_at_message_create 中创建

        MAX_BET_PER_USER = 1000000 # 设置一个合理的最大投入金额

        total_bet_amount = sum(bet['amount'] for bet in bets)

        if total_bet_amount > MAX_BET_PER_USER:
            await message.reply(content=f'❌ 您的总投入金额超过了最大限制：**{MAX_BET_PER_USER}** 代币。')
            return

        if internal_id in self.Gambling.active_games:
            await message.reply(content='⚠️ 您已经有一个进行中的游戏，请完成或取消当前游戏后再开始新游戏。')
            return

        if not self.Boss.boss_id:
            await message.reply(content='❌ 当前没有负责人，无法进行游戏。请等待有人成为负责人后再试。')
            return

        async with self.data_manager.data_lock:
            user_points = int(self.user_data[internal_id].get('points', 0))
            if total_bet_amount > user_points:
                await message.reply(content=f'❌ 您的代币不足，当前代币：**{user_points}** 个。')
                return

            try:
                self.Gambling._deduct_user_points(internal_id, total_bet_amount)
                logger.info(f"扣除用户 {internal_id} 的 {total_bet_amount} 代币，剩余代币：{self.user_data[internal_id]['points']}")
            except ValueError as e:
                await message.reply(content=f'❌ {str(e)}')
                return

            potential_winnings = sum(
                self.Gambling.get_multiplier(bet['type'], 18) * bet['amount'] for bet in bets
                if self.Gambling.get_multiplier(bet['type'], 18) > 0
            )
            boss_points = int(self.user_data.get(self.Boss.boss_id, {}).get('points', 0))
            if potential_winnings > boss_points:
                await message.reply(content='⚠️ 负责人代币不足以支付您的潜在奖励。请联系管理员。')

                self.Gambling._add_user_points(internal_id, total_bet_amount)
                logger.info(f"返还用户 {internal_id} 的 {total_bet_amount} 代币，当前代币：{self.user_data[internal_id]['points']}")
                return

            period_number = self.Gambling.generate_unique_period_number()
            for bet in bets:
                self.Gambling.log_history(
                    internal_id,
                    f"{bet['type']} {bet['amount']} 用于游戏",
                    -bet['amount'],
                    period_number,
                    bet_amount=bet['amount'],
                    role='player'
                )
            self.Gambling.active_games[internal_id] = {
                'username': username,
                'bets': bets,
                'start_time': time.time(),
                'period_number': period_number,
                'boss': self.Boss,
                'dice_rolls': []
            }
            bet_details = "\n".join(
                [f"• **{self.Gambling.map_bet_type_display(bet['type'])}**: 投入 **{bet['amount']}** 代币" for bet in
                 bets]
            )
            confirmation_message = (
                f"🎲 **投入确认** 🎲\n"
                f"--------------------------------\n"
                f"{bet_details}\n"
                f"--------------------------------\n"
                f"💵 **剩余余额**: **{user_points - total_bet_amount}** 代币\n"
                f"--------------------------------\n"
                f"🎯 游戏开始！请发送 `sh` 来摇骰子。发送 `sh3` 来摇三次骰子。"
            )
            if len(confirmation_message) > 2000:
                await message.reply(content='❌ 确认消息过长，无法发送。请减少投入数量。')
                return
            try:
                await message.reply(content=confirmation_message)
            except ServerError:
                await message.reply(content='❌ 无法发送确认消息，请稍后再试。')
            logger.info(f"用户 {internal_id} 开始游戏，期号：{period_number}，总投入：{total_bet_amount} 代币。")

    async def handle_dice_command(self, message: Message, userid: str, parts: list):
        logger.info(f"用户 {userid} 发起摇骰子命令: {parts}")
        # 创建或获取用户账户
        internal_id = await self.data_manager.get_or_create_user(userid, message.author.username)
        if not internal_id:
            await message.reply(content='❌ 无法创建或获取您的用户信息。')
            return

        command = parts[0].lower()
        num_dice = 1

        if command in ['sh3', '🎲3']:
            num_dice = 3
        elif len(parts) > 1 and parts[1].isdigit():
            num_dice = int(parts[1])
        elif command in ['sh', '🎲']:
            num_dice = 1

        if num_dice <= 0:
            await message.reply(content='❌ 摇骰子次数必须大于0。')
            return
        if num_dice > 3:
            await message.reply(content='❌ 最多只能摇3次骰子。')
            return

        game = self.Gambling.active_games.get(internal_id)
        if not game:
            await message.reply(content='❌ 未找到进行中的游戏。')
            return

        remaining_dice = 3 - len(game['dice_rolls'])
        if num_dice > remaining_dice:
            await message.reply(content=f'❌ 您只能摇 {remaining_dice} 次骰子。')
            return

        await self.Gambling.roll_dice_for_game(message, internal_id, num_dice=num_dice)


async def main():
    if not os.path.exists('config.yaml'):
        logger.error("配置文件 config.yaml 不存在。")
        exit(1)
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    appid = config.get('appid')
    secret = config.get('secret')
    if not appid or not secret:
        logger.error("配置文件中缺少 appid 或 secret。")
        exit(1)

    # 初始化数据管理器
    data_manager = DataManager()

    # 创建 DwgxBot 实例并传入 data_manager
    intents = botpy.Intents(public_guild_messages=True)
    client = DwgxBot(config=config, data_manager=data_manager, intents=intents)

    # 创建一个事件，用于等待关闭信号
    stop_event = asyncio.Event()

    # 定义关闭信号的处理器
    def shutdown():
        logger.info("接收到关闭信号，正在关闭机器人...")
        stop_event.set()

    # 注册信号处理器
    loop = asyncio.get_running_loop()
    for s in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(s, shutdown)
        except NotImplementedError:
            # 某些平台（如Windows）可能不支持
            pass

    # 启动机器人
    start_task = asyncio.create_task(client.start(appid, secret))

    # 等待关闭信号
    await stop_event.wait()

    # 优雅关闭机器人
    await client.close()
    logger.info("机器人已关闭。")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("程序被用户中断。")
    except Exception as e:
        logger.exception("启动机器人时发生异常：")
