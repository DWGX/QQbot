import logging

logger = logging.getLogger("DwgxBot")
logging.basicConfig(level=logging.INFO)


import asyncio
import os
import re
import time
import yaml
import logging
import botpy
from botpy.message import Message
from botpy.errors import ServerError
from DataManager import DataManager
from Assist import Assist
from Boss import Boss
from Gambling import Gambling
from RedEnvelope import RedEnvelope

logger = logging.getLogger("DwgxBot")
logging.basicConfig(level=logging.INFO)


class DwgxBot(botpy.Client):
    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
        self.data_manager = DataManager()
        self.data = self.data_manager.data
        self.user_data = self.data['user_data']

        self.Boss = Boss(
            data=self.data,
            user_data=self.user_data,
            save_data=self.data_manager.save_data,
            gambling=None,
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

        if self.Boss.boss_id:
            if self.Boss.boss_id not in self.user_data:
                asyncio.create_task(self.create_boss_account())

        self.user_dice_commands = {}

    async def create_boss_account(self):
        try:
            async with self.data_manager.data_lock:
                internal_id = self.Boss.boss_id
                if internal_id and internal_id not in self.user_data:
                    self.user_data[internal_id] = {
                        'userid': internal_id,
                        'username': '老板',
                        'points': 10000
                    }
                    self.data["internal_to_userid"][internal_id] = internal_id
                    self.data["userid_to_internal"][internal_id] = internal_id
                    await self.data_manager.save_data()
                    logger.info(f"已为老板 {internal_id} 创建账户，初始代币：10000")
                else:
                    logger.warning(f"老板账户 {internal_id} 已存在。")
        except Exception as e:
            logger.exception(f"创建老板账户时出错: {e}")

    @staticmethod
    def parse_bets(content):
        pattern = re.compile(
            r"\b(ds|xs|dd|da|xd|xiao|x|大双|小双|大单|小单|大|小|1[0-8]|[3-9])\s*(\d+)\b",
            re.IGNORECASE
        )

        matches = pattern.findall(content)
        bets = []
        for bet_type, bet_amount in matches:
            try:
                bet_amount = int(bet_amount)
                if bet_amount <= 0:
                    continue
                bets.append({'type': bet_type.lower(), 'amount': bet_amount})
            except ValueError:
                continue
        return bets

    async def on_at_message_create(self, message: Message):
        content = message.content.strip()
        userid = str(message.author.id)
        username = message.author.username
        internal_id = await self.data_manager.get_or_create_user(userid, username)
        bot_mention = f"<@!{self.robot.id}>"
        if content.startswith(bot_mention):
            content = content[len(bot_mention):].strip()
        else:
            return
        if not content:
            await self.Assist.show_help(message)
            return
        control_commands = [
            '🎲', 'sh', '查看老板', 'boss', '取消', 'qx', '帮助', 'help',
            '我当老板', '不当老板', 'ye', '查看账户', '复读',
            'hb', '领取', '撤回', 'sh3', '🎲3'
        ]

        parts = content.split()
        if parts and parts[0].lower() in [cmd.lower() for cmd in control_commands]:
            command = parts[0].lower()
            if command in ['hb', '领取', '撤回']:
                await self.RedEnvelope.handle_command(message, parts, userid)
                return
            if command in ['help', '帮助']:
                await self.Assist.show_help(message)
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
            await message.reply(content='❓ 未知指令。请输入 帮助 或 help 查看可用指令。')
            return
        bets = self.parse_bets(content)
        if not bets:
            await message.reply(content='❓ 未知指令。请输入 帮助 或 help 查看可用指令。')
            return
        await self.handle_start_game(message, bets, internal_id)

    async def handle_start_game(self, message: Message, bets: list, internal_id: str):
        username = message.author.username
        if not self.Boss.boss_id:
            await message.reply(content='❌ 当前没有老板，无法进行游戏。请等待有人成为老板后再试。')
            return

        async with self.data_manager.data_lock:
            if internal_id not in self.user_data:
                self.user_data[internal_id] = {
                    'userid': self.data["internal_to_userid"][internal_id],
                    'username': username,
                    'points': 1000
                }
                await self.data_manager.save_data()

            user_points = int(self.user_data[internal_id].get('points', 0))
            total_bet_amount = sum(bet['amount'] for bet in bets)
            if total_bet_amount > user_points:
                await message.reply(content=f'❌ 您的代币不足，当前代币：**{user_points}** 个。')
                return


            self.user_data[internal_id]['points'] -= total_bet_amount

            potential_winnings = sum(
                self.Gambling.get_multiplier(bet['type'], 18) * bet['amount'] for bet in bets
                if self.Gambling.get_multiplier(bet['type'], 18) > 0
            )
            boss_points = int(self.user_data[self.Boss.boss_id].get('points', 0))
            if potential_winnings > boss_points:
                await message.reply(content='⚠️ 老板的代币不足以支付您的潜在奖励。请联系管理员。')
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
                f"🎯 游戏开始！请发送 🎲 或 sh 来摇骰子。发送 🎲3 或 sh3 来摇三次骰子。"
            )
            if len(confirmation_message) > 2000:
                await message.reply(content='❌ 确认消息过长，无法发送。请减少投入数量。')
                return
            try:
                await message.reply(content=confirmation_message)
            except ServerError:
                await message.reply(content='❌ 无法发送确认消息，请稍后再试。')
            logger.info(f"用户 {internal_id} 开始游戏，期号：{period_number}，总投注：{total_bet_amount} 代币。")

    async def handle_dice_command(self, message: Message, userid: str, parts: list):
        internal_id = self.data_manager.data["userid_to_internal"].get(userid)
        if not internal_id:
            await message.reply(content='❌ 未找到您的用户信息。')
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

        await self.Gambling.roll_dice_for_game(message, internal_id, num_dice=num_dice)

    async def roll_three_dice(self, message: Message, internal_id: str):
        game = self.Gambling.active_games.get(internal_id)
        if not game:
            await message.reply(content='❌ 未找到进行中的游戏。')
            return
        if len(game['dice_rolls']) >= 3:
            await message.reply(content='❌ 您已经摇过所有的骰子了。')
            return

        for _ in range(3 - len(game['dice_rolls'])):
            number = self.Gambling.roll_dice()[0]
            game['dice_rolls'].append(number)
            dice_emoji = self.Gambling.DICE_EMOJI[number]
            try:
                await message.reply(content=f"🎲 自动骰子结果：【{dice_emoji}】")
            except ServerError:
                await message.reply(content='❌ 发送骰子结果时发生错误，请稍后再试。')
                return
        asyncio.create_task(self.Gambling.save_data())
        await self.Gambling.process_game_result(message, internal_id, game)
        logger.info(f"用户 {internal_id} 自动摇骰子至3次，处理游戏结果。")

if __name__ == "__main__":
    try:
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
        intents = botpy.Intents(public_guild_messages=True)
        client = DwgxBot(config=config, intents=intents)
        client.run(appid, secret)
    except Exception as e:
        logger.exception("启动机器人时发生异常：")
