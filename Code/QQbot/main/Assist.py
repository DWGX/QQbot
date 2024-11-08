# Assist.py

import logging
from botpy.errors import ServerError
from botpy.message import Message

logger = logging.getLogger("Assist")


class Assist:
    def __init__(self, user_data, game_history, save_data, boss_id, userid_to_internal):
        self.user_data = user_data
        self.game_history = game_history
        self._save_data = save_data
        self.boss_id = boss_id
        self.userid_to_internal = userid_to_internal
        self.client = None

    def get_internal_id(self, userid: str):
        return self.userid_to_internal.get(userid)

    async def show_current_boss(self, message: Message):
        if self.boss_id and self.boss_id in self.user_data:
            boss_info = self.user_data[self.boss_id]
            boss_name = boss_info.get('username', '未知')
            boss_balance = boss_info.get('points', 0)
            await message.reply(content=f"👑 **当前负责人**: <@{boss_info['userid']}> **{boss_name}**\n💵 **负责人余额**: **{boss_balance}** 代币")
        else:
            await message.reply(content='⚠️ 当前没有负责人。')

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

        player_history = [record for record in game_history if
                          record.get('role') == 'player' and '用于游戏' in record.get('description', '')]

        if not player_history:
            await message.reply(content="您还没有任何游戏活动记录。")
            return

        total_games = len(set(record['period_number'] for record in player_history))
        total_winnings = sum(
            record.get('points_change', 0) for record in game_history if
            record.get('role') == 'player' and record.get('points_change', 0) > 0
        )
        total_bet = sum(
            record.get('bet_amount', 0) for record in player_history
        )
        total_profit = total_winnings - total_bet

        win_count = len({record['period_number'] for record in game_history if
                         record.get('role') == 'player' and record.get('points_change', 0) > 0})
        lose_count = total_games - win_count
        win_rate = (win_count / total_games * 100) if total_games > 0 else 0

        summary_message = (
            f"📜 **游戏历史汇总** 📜\n"
            f"--------------------------------\n"
            f"🎮 总游戏次数：**{total_games}**\n"
            f"🏆 收获次数：**{win_count}**\n"
            f"❌ 失去次数：**{lose_count}**\n"
            f"📊 收获率：**{win_rate:.2f}%**\n"
            f"💰 总投入代币：**{total_bet}**\n"
            f"💸 总收获代币：**{total_winnings}**\n"
            f"📈 总利润：**{total_profit}**\n"
            f"--------------------------------"
        )

        try:
            await message.reply(content=summary_message)
        except ServerError:
            await message.reply(content='❌ 无法发送游戏历史汇总，请稍后再试。')
