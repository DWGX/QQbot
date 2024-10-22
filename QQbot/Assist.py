import logging
from botpy.message import Message
from botpy.errors import ServerError
import asyncio

logger = logging.getLogger("Assist")


class Assist:
    def __init__(self, user_data, game_history, admin_ids, save_data, boss_id):
        self.user_data = user_data
        self.game_history = game_history
        self.admin_ids = admin_ids
        self.save_data = save_data
        self.boss_id = boss_id  # 添加 boss_id 作为参数
        self.client = None

    async def show_help(self, message: Message):
        user_id = str(message.author.id)
        is_admin = user_id in self.admin_ids
        logger.info(f"用户 {user_id} 请求帮助，是否为管理员：{is_admin}")

        help_message_user = (
            "📚 **帮助信息** 📚\n\n"
            "🔹 **倍数说明：**\n"
            "1. 大: x1.97\n"
            "2. 小: x1.97\n"
            "3. 大单: x3.9\n"
            "4. 大双: x3.9\n"
            "5. 小单: x2.9\n"
            "6. 小双: x2.9\n"
            "7. 单个骰子总和 (3 - 18): x5\n\n"

            "🔹 **用户指令：**\n"
            "1. @机器人 Ye 或 @机器人 查看账户\n"
            "   - 查询当前余额。\n"
            "2. @机器人 分析历史\n"
            "   - 查看游戏历史记录和分析。\n"
            "3. @机器人 取消\n"
            "   - 取消当前游戏并返还代币。\n"
            "4. @机器人 ping\n"
            "   - 检查机器人是否在线。\n"
            "5. @机器人 查老板\n"
            "   - 查询当前老板及其余额。\n"
        )

        help_message_admin = (
            "\n🔹 **管理员指令：**\n"
            "1. @机器人 增加点数 <用户ID> <代币>\n"
            "   - 为指定用户增加代币。\n"
            "2. @机器人 设置点数 <用户ID> <代币>\n"
            "   - 设置用户的代币。\n"
            "3. @机器人 我当老板\n"
            "   - 成为当前的老板。\n"
            "4. @机器人 不当老板\n"
            "   - 卸任老板身份。\n"
        )

        help_message = help_message_user
        if is_admin:
            help_message += help_message_admin

        try:
            await message.reply(content=help_message)
            logger.info("成功发送帮助消息。")
        except ServerError as e:
            logger.error(f"发送帮助消息失败: {e}")
            await message.reply(content='抱歉，无法发送帮助信息。请稍后再试。')

    async def show_current_boss(self, message: Message):
        if self.boss_id:
            boss_data = self.user_data.get(self.boss_id, {})
            boss_username = boss_data.get('username', '未知')
            boss_balance = boss_data.get('points', 0)  # 获取老板余额
            await message.reply(
                content=f"👑 当前老板是：**{boss_username}** (ID: {self.boss_id})\n"
                        f"💰 老板余额：**{boss_balance}** 代币"
            )
        else:
            await message.reply(content="当前没有老板。")
        logger.info(f"用户 {message.author.id} 查询了当前老板及其余额。")

    async def analyze_history(self, message: Message):
        user_id = str(message.author.id)
        game_history = self.game_history.get(user_id, [])

        if not game_history:
            await message.reply(content="您还没有任何游戏历史记录。")
            return

        # 只统计玩家的记录，不包括老板的
        player_history = [record for record in game_history if record.get('role') == 'player']

        total_games = len(player_history)
        total_winnings = sum(
            record.get('points_change', 0) for record in player_history if record.get('points_change', 0) > 0)
        total_bet = sum(
            record.get('bet_amount', 0) for record in player_history if '代币' in record.get('description', ''))
        total_profit = total_winnings - total_bet

        win_count = sum(1 for record in player_history if record.get('points_change', 0) > 0)
        lose_count = total_games - win_count

        analysis_message = (
            f"🎲 **游戏历史分析** 🎲\n"
            f"--------------------------------\n"
            f"总次数：{total_games}\n"
            f"胜利次数：{win_count}\n"
            f"失败次数：{lose_count}\n"
            f"总投入：{total_bet}\n"
            f"总获利：{total_winnings}\n"
            f"总利润：{total_profit}\n"
            f"--------------------------------"
        )

        try:
            await message.reply(content=analysis_message)
            logger.info("成功发送游戏历史分析。")
        except ServerError as e:
            logger.error(f"发送分析消息失败: {e}")
            await message.reply(content='抱歉，无法发送分析信息。请稍后再试。')

    async def show_balance(self, message: Message):
        user_id = str(message.author.id)

        if user_id not in self.user_data:
            self.user_data[user_id] = {'username': message.author.username, 'points': 1000}
            asyncio.create_task(self.save_data())
            await message.reply(content='✅ 您还没有账户，已自动创建账户并赋予 **1000** 代币。')
            logger.info(f"已为用户 {user_id} 创建新账户，初始代币：1000")
            return

        balance = self.user_data[user_id].get('points', 0)
        username = self.user_data[user_id].get('username', '未知')
        await message.reply(
            content=f"💰 **余额查询** 💰\n\n"
                    f"👤 用户名：**{username}**\n"
                    f"🔑 用户ID：**{user_id}**\n"
                    f"💵 当前代币：**{balance}** 个。"
        )
        logger.info(f"已显示用户 {user_id} 的余额。")
