# Gambling.py

import asyncio
import logging
import random
import re
import time
from datetime import datetime
from botpy.message import Message
from botpy.errors import ServerError

logger = logging.getLogger("Gambling")


class Gambling:
    def __init__(self, user_data, game_history, save_data, boss=None):
        self.user_data = user_data
        self.game_history = game_history
        self._save_data = save_data
        self.active_games = {}
        self.boss = boss
        self.DICE_EMOJI = {
            1: '🎲1️⃣',
            2: '🎲2️⃣',
            3: '🎲3️⃣',
            4: '🎲4️⃣',
            5: '🎲5️⃣',
            6: '🎲6️⃣'
        }

        self.bet_multipliers = {
            '双': 2.9,
            '单': 2.9,
            '大': 1.97,
            '小': 1.97,
            '3': 6.9,
            '4': 6.9,
            '5': 6.9,
            '6': 6.9,
            '7': 6.9,
            '8': 6.9,
            '9': 6.9,
            '10': 6.9,
            '11': 6.9,
            '12': 6.9,
            '13': 6.9,
            '14': 6.9,
            '15': 6.9,
            '16': 6.9,
            '17': 6.9,
            '18': 6.9
        }

    def log_history(self, user_id, description, points_change, period_number, bet_amount=None, role='player'):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        history_record = {
            'time': timestamp,
            'description': description,
            'points_change': points_change,
            'new_balance': self.user_data[user_id]['points'],
            'role': role,
            'period_number': period_number
        }
        if bet_amount is not None:
            history_record['bet_amount'] = bet_amount
        if user_id not in self.game_history:
            self.game_history[user_id] = []
        self.game_history[user_id].append(history_record)
        asyncio.create_task(self._save_data())
        logger.info(f"游戏历史已更新，用户ID：{user_id}")

    def generate_unique_period_number(self):
        while True:
            date_time = datetime.now().strftime("%Y%m%d%H%M%S")
            random_str = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=4))
            unique_id = f"{date_time}{random_str}"
            if unique_id not in self.game_history.get("period_numbers", set()):
                break
        self.game_history.setdefault("period_numbers", set()).add(unique_id)
        logger.debug(f"生成唯一期号：{unique_id}")
        return unique_id

    async def roll_dice_for_game(self, message: Message, user_id, num_dice=1):
        game = self.active_games.get(user_id)
        if not game:
            await message.reply(content='❌ 未找到进行中的游戏。')
            logger.warning(f"未找到用户 {user_id} 的进行中游戏。")
            return
        remaining_dice = 3 - len(game['dice_rolls'])
        if remaining_dice <= 0:
            await message.reply(content='❌ 您已经摇过所有的骰子了。')
            logger.warning(f"用户 {user_id} 尝试多次摇骰子。")
            return
        num_dice = min(num_dice, remaining_dice)
        numbers = self.roll_dice(num_dice)
        for number in numbers:
            game['dice_rolls'].append(number)
            dice_emoji = self.DICE_EMOJI[number]
            try:
                await message.reply(content=f"🎲 第{len(game['dice_rolls'])}个骰子结果：【{dice_emoji}】")
            except ServerError:
                await message.reply(content='❌ 发送骰子结果时发生错误，请稍后再试。')
                return
            logger.info(f"用户 {user_id} 摇骰子第{len(game['dice_rolls'])}个结果：{number}")
        asyncio.create_task(self._save_data())
        if len(game['dice_rolls']) == 3:
            await self.process_game_result(message, user_id, game)

    async def process_game_result(self, message: Message, user_id, game):
        try:
            numbers = game['dice_rolls']
            total = sum(numbers)
            bets = game['bets']
            total_winnings = 0
            details = []
            boss = game.get('boss')
            logger.info(f"处理游戏结果，用户ID：{user_id}, 骰子总和：{total}")

            for bet in bets:
                bet_type = bet['type']
                bet_amount = bet['amount']
                multiplier = self.get_multiplier(bet_type, total)

                logger.info(f"用户 {user_id} 投入类型：{bet_type}, 投入金额：{bet_amount}, 倍数：{multiplier}")

                if multiplier > 0:
                    winnings = int(bet_amount * multiplier)
                    self.user_data[user_id]['points'] += winnings
                    self.log_history(user_id, f"{bet_type} 🎉 收获游戏，奖励 {winnings} 代币", winnings, game['period_number'],
                                     bet_amount=bet_amount, role='player')
                    details.append(
                        f"✅ **{self.map_bet_type_display(bet['type'])}**: 投入 **{bet['amount']}** 代币，收获 **{winnings}** 💰代币")

                    if boss and boss.boss_id != user_id:
                        try:
                            boss.deduct_boss_points(winnings)
                            self.log_history(boss.boss_id, f'玩家 {user_id} 🎉 收获游戏，扣除负责人 {winnings} 代币', -winnings,
                                             game['period_number'], role='boss')
                            details.append(f"🔻 **负责人**: 扣除 **{winnings}** 💰代币")
                        except ValueError as e:
                            logger.error(f"扣除负责人 {boss.boss_id} 代币失败：{e}")
                            await message.reply(content='⚠️ 负责人的代币不足以支付您的奖励。')
                            self.user_data[user_id]['points'] -= winnings
                            self.user_data[user_id]['points'] += bet_amount
                            self.log_history(user_id, f'因负责人余额不足，返还 {bet_amount} 代币', bet_amount,
                                             game['period_number'], role='player')
                            details.append(f"🔄 **返还**: {bet_amount} 💰代币")
                else:
                    details.append(f"❌ **{self.map_bet_type_display(bet_type)}**: 投入 **{bet_amount}** 代币，未收获")
                    if boss and boss.boss_id != user_id:
                        boss.add_boss_points(bet_amount)
                        self.log_history(boss.boss_id, f'玩家 {user_id} ❌ 失去游戏，负责人获得 {bet_amount} 代币', bet_amount,
                                         game['period_number'], role='boss')
                        details.append(f"💹 **负责人**: 获得 **{bet_amount}** 💰代币")

            emoji_numbers = [self.DICE_EMOJI[n] for n in numbers]
            # 开始构建游戏结果信息
            analysis_message = (
                f"🎲 **游戏结果** 🎲\n"
                f"--------------------------------\n"
                f"结果：**{'、'.join(emoji_numbers)}**\n"
                f"总和：**{self.number_to_emoji(total)}**\n\n"
                f"结果详情：\n"
            )

            # 将"代币"替换为表情并将数字转换为表情
            for detail in details:
                detail = (
                    detail.replace('收获', '🎉')
                    .replace('未收获', '❌')
                    .replace('代币', '💰')  # 将 "代币" 替换为表情或符号
                )
                # 将所有数字转换为 Emoji
                detail = re.sub(r'\d+', lambda x: self.number_to_emoji(int(x.group())), detail)
                analysis_message += detail + '\n'

            # 添加期号信息
            analysis_message += (
                f"期号： **{game['period_number']}**\n"
                f"--------------------------------\n"
            )

            # 控制消息长度，避免超出限制
            if len(analysis_message) > 2000:
                analysis_message = analysis_message[:1997] + '...'

            try:
                await message.reply(content=analysis_message)
                logger.info(f"已发送游戏结果给用户 {user_id}")
            except ServerError as e:
                logger.error(f"发送游戏结果失败：{e}")
                await message.reply(content='⚠️ 无法发送结果，请稍后重试。')

            self.active_games.pop(user_id, None)
            asyncio.create_task(self._save_data())

        except Exception as e:
            logger.exception(f"处理游戏结果时发生错误：{e}")
            await message.reply(content='⚠️ 处理游戏结果时发生错误，请联系管理员。')
            self.active_games.pop(user_id, None)

    def map_bet_type_display(self, bet_type):
        mapping = {
            '双': '双',
            '单': '单',
            '大': '大',
            '小': '小',
            '3': '3️⃣',
            '4': '4️⃣',
            '5': '5️⃣',
            '6': '6️⃣',
            '7': '7️⃣',
            '8': '8️⃣',
            '9': '9️⃣',
            '10': '🔟',
            '11': '1️⃣1️⃣',
            '12': '1️⃣2️⃣',
            '13': '1️⃣3️⃣',
            '14': '1️⃣4️⃣',
            '15': '1️⃣5️⃣',
            '16': '1️⃣6️⃣',
            '17': '1️⃣7️⃣',
            '18': '1️⃣8️⃣',
        }
        return mapping.get(bet_type, bet_type)

    def number_to_emoji(self, number):
        number_emojis = {
            3: '3️⃣',
            4: '4️⃣',
            5: '5️⃣',
            6: '6️⃣',
            7: '7️⃣',
            8: '8️⃣',
            9: '9️⃣',
            10: '🔟',
            11: '1️⃣1️⃣',
            12: '1️⃣2️⃣',
            13: '1️⃣3️⃣',
            14: '1️⃣4️⃣',
            15: '1️⃣5️⃣',
            16: '1️⃣6️⃣',
            17: '1️⃣7️⃣',
            18: '1️⃣8️⃣'
        }
        return number_emojis.get(number, str(number))

    def roll_dice(self, num_dice=1):
        return [random.randint(1, 6) for _ in range(num_dice)]

    def get_multiplier(self, bet_type, total):
        bet_type_map = {
            '双': '双',
            '单': '单',
            '大': '大',
            '小': '小',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '13': '13',
            '14': '14',
            '15': '15',
            '16': '16',
            '17': '17',
            '18': '18',
        }
        mapped_bet_type = bet_type_map.get(bet_type, bet_type)

        if mapped_bet_type in ['大', '小', '双', '单']:
            if self.is_bet_success(mapped_bet_type, total):
                return self.bet_multipliers.get(mapped_bet_type, 0)
            else:
                return 0
        else:
            try:
                bet_sum = int(mapped_bet_type)
                if total == bet_sum:
                    return self.bet_multipliers.get(mapped_bet_type, 0)
                else:
                    return 0
            except ValueError:
                return 0

    def is_bet_success(self, bet_type, total):
        if bet_type == '大':  # 大
            return 11 <= total <= 18
        elif bet_type == '小':  # 小
            return 3 <= total <= 10
        elif bet_type == '双':  # 双
            return 3 <= total <= 18 and total % 2 == 0
        elif bet_type == '单':  # 单
            return 3 <= total <= 18 and total % 2 != 0
        return False

    def cancel_game(self, user_id):
        if user_id in self.active_games:
            game = self.active_games[user_id]
            if len(game['dice_rolls']) > 0:
                logger.info(f"用户 {user_id} 尝试取消已开始的游戏。")
                return 'started'

            total_refund = sum(bet['amount'] for bet in game['bets'])
            self.user_data[user_id]['points'] += total_refund
            for bet in game['bets']:
                self.log_history(user_id, f'取消游戏，返还 {bet["amount"]} 代币', bet['amount'], game['period_number'],
                                 bet_amount=bet['amount'], role='player')
                logger.info(f"用户 {user_id} 成功取消游戏，返还 {bet['amount']} 代币")
            asyncio.create_task(self._save_data())
            self.active_games.pop(user_id, None)
            return 'success'
        logger.info(f"用户 {user_id} 尝试取消不存在的游戏")
        return 'not_started'

    def _deduct_user_points(self, user_id, amount):
        if user_id not in self.user_data:
            raise ValueError("用户不存在。")
        if self.user_data[user_id]['points'] < amount:
            raise ValueError("您的代币不足以进行投入。")
        self.user_data[user_id]['points'] -= amount
        self.log_history(user_id, f"扣除 {amount} 代币用于游戏", -amount, "system", role='system')
        asyncio.create_task(self._save_data())
        logger.info(f"用户 {user_id} 扣除 {amount} 代币，当前余额：{self.user_data[user_id]['points']}")

    def _add_user_points(self, user_id, amount):
        if user_id not in self.user_data:
            raise ValueError("用户不存在。")
        self.user_data[user_id]['points'] += amount
        self.log_history(user_id, f"增加 {amount} 代币", amount, "system", role='system')
        asyncio.create_task(self._save_data())
        logger.info(f"用户 {user_id} 增加 {amount} 代币，当前余额：{self.user_data[user_id]['points']}")
