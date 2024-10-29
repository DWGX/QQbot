import logging

from botpy.errors import ServerError
from botpy.message import Message

logger = logging.getLogger("Assist")

class Assist:
    def __init__(self, user_data, game_history, save_data, boss_id, userid_to_internal):
        self.user_data = user_data
        self.game_history = game_history
        self.save_data = save_data
        self.boss_id = boss_id
        self.userid_to_internal = userid_to_internal
        self.client = None

    def get_internal_id(self, userid: str):
        return self.userid_to_internal.get(userid)

    @staticmethod
    async def show_help(message: Message):
        help_message = (
            "🔹 **红包指令说明：**\n"
            "1. @机器人 hb <金额> <领取人数>\n"
            "   - 发送一个指定金额的公开红包，指定领取人数。例如：@机器人 hb 100 5\n"
            "2. @机器人 hb @用户名 <金额>\n"
            "   - 发送一个指定金额的私密红包给指定用户。例如：@机器人 hb @用户 100\n"
            "3. @机器人 hb 确认\n"
            "   - 确认发送红包。\n"
            "4. @机器人 领取<期号>红包\n"
            "   - 领取指定期号的红包。例如：@机器人 领取202410242141p红包\n"
            "5. @机器人 撤回<期号>红包\n"
            "   - 撤回指定期号的红包（仅管理员）。例如：@机器人 撤回202410242141p红包\n"
            "\n🔹 **其他指令说明：**\n"
            "1. @机器人 sh 或 @机器人 🎲\n"
            "   - 摇一次骰子（手动模式）。\n"
            "2. @机器人 sh3 或 @机器人 🎲3\n"
            "   - 自动摇三次骰子并发送结果。\n"
            "3. @机器人 取消\n"
            "   - 取消当前进行中的游戏。\n"
            "4. @机器人 我当老板\n"
            "   - 成为老板。\n"
            "5. @机器人 不当老板\n"
            "   - 离开老板职位。\n"
            "6. @机器人 查看老板 或 @机器人 boss\n"
            "   - 查看当前老板。\n"
            "7. @机器人 ye 或 @机器人 查看账户\n"
            "   - 查看您的账户余额和历史记录。\n"
            "8. @机器人 复读 <内容>\n"
            "   - 让机器人重复指定的内容。\n"
        )
        try:
            await message.reply(content=help_message)
        except ServerError:
            await message.reply(content='❌ 无法发送帮助信息，请稍后再试。')

    async def show_current_boss(self, message: Message):
        if self.boss_id and self.boss_id in self.user_data:
            boss_info = self.user_data[self.boss_id]
            boss_name = boss_info.get('username', '未知')
            boss_balance = boss_info.get('points', 0)
            await message.reply(content=f"👑 **当前老板**: <@{boss_info['userid']}> **{boss_name}**\n💵 **老板余额**: **{boss_balance}** 代币")
        else:
            await message.reply(content='⚠️ 当前没有老板。')

    async def show_balance(self, message: Message, userid: str):
        internal_id = self.get_internal_id(userid)
        if not internal_id:
            await message.reply(content='⚠️ 未找到您的账户信息。')
            return

        user = self.user_data.get(internal_id)
        if user:
            username = user.get('username', '未知')
            balance = user.get('points', 0)
            await message.reply(content=(
                f"💰 **账户信息**:\n"
                f"👤 用户名：**{username}**\n"
                f"💵 余额：**{balance}** 代币\n"
                f"🆔 用户 ID： **{internal_id}**"
            ))
        else:
            await message.reply(content='⚠️ 未找到您的账户信息。')

    async def analyze_history(self, message: Message):

        internal_id = self.get_internal_id(str(message.author.id))

        if not internal_id:
            await message.reply(content="⚠️ 未找到您的账户信息。")
            return


        game_history = self.game_history.get(internal_id, [])

        if not game_history:
            await message.reply(content="您还没有任何游戏活动记录。")
            return


        player_history = [record for record in game_history if record.get('role') == 'player']

        if not player_history:
            await message.reply(content="您还没有任何游戏活动记录。")
            return


        total_games = len(player_history)
        total_winnings = sum(
            record.get('points_change', 0) for record in player_history if record.get('points_change', 0) > 0
        )
        total_bet = sum(
            record.get('bet_amount', 0) for record in player_history if '代币' in record.get('description', '')
        )
        total_profit = total_winnings - total_bet

        win_count = sum(1 for record in player_history if record.get('points_change', 0) > 0)
        lose_count = total_games - win_count
        win_rate = (win_count / total_games * 100) if total_games > 0 else 0


        summary_message = (
            f"📜 **游戏历史汇总** 📜\n"
            f"--------------------------------\n"
            f"🎮 总游戏次数：**{total_games}**\n"
            f"🏆 胜利次数：**{win_count}**\n"
            f"❌ 失败次数：**{lose_count}**\n"
            f"📊 胜率：**{win_rate:.2f}%**\n"
            f"💰 总投入代币：**{total_bet}**\n"
            f"💸 总获利代币：**{total_winnings}**\n"
            f"📈 总利润：**{total_profit}**\n"
            f"--------------------------------"
        )

        try:
            await message.reply(content=summary_message)
        except ServerError:
            await message.reply(content='❌ 无法发送游戏历史汇总，请稍后再试。')

