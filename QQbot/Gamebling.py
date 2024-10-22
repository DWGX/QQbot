import asyncio
import time
import random
import logging
from datetime import datetime

logger = logging.getLogger("Gambling")


class Gambling:
    def __init__(self, user_data, game_history, save_data):
        self.user_data = user_data
        self.game_history = game_history
        self.save_data = save_data
        self.active_games = {}
        self.DICE_EMOJI = {
            1: '🎲1️⃣',
            2: '🎲2️⃣',
            3: '🎲3️⃣',
            4: '🎲4️⃣',
            5: '🎲5️⃣',
            6: '🎲6️⃣'
        }
        # 定义各类投入的倍率
        self.bet_multipliers = {
            '大': 1.97,
            'da': 1.97,
            '小': 1.97,
            'xiao': 1.97,
            'x': 1.97,  # 新增 'x' 作为 '小' 的别名
            '大单': 3.9,
            'dd': 3.9,
            '大双': 3.9,
            'ds': 3.9,
            '小单': 2.9,
            'xd': 2.9,
            '小双': 2.9,
            'xs': 2.9,
            # 具体总和的倍率
            '3': 5.0,
            '4': 3.0,
            '5': 3.0,
            '6': 3.0,
            '7': 2.0,
            '8': 3.0,
            '9': 3.0,
            '10': 3.0,
            '11': 4.0,
            '12': 3.0,
            '13': 4.0,
            '14': 3.0,
            '15': 4.0,
            '16': 3.0,
            '17': 4.0,
            '18': 3.0
        }

    def log_history(self, user_id, description, points_change, period_number, bet_amount=None, role='player'):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        history_record = {
            'time': timestamp,
            'description': description,
            'points_change': points_change,
            'new_balance': self.user_data[user_id]['points'],
            'role': role,
            'period_number': period_number  # 添加期号
        }
        if bet_amount is not None:
            history_record['bet_amount'] = bet_amount
        if user_id not in self.game_history:
            self.game_history[user_id] = []
        self.game_history[user_id].append(history_record)
        asyncio.create_task(self.save_data())  # 异步保存
        logger.info(f"游戏历史已更新，用户ID：{user_id}")

    def generate_unique_period_number(self):
        date_time = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=4))
        return f"{date_time}{random_str}"

    def start_game(self, user_id, username, bets, boss=None):
        if user_id not in self.user_data:
            self.user_data[user_id] = {'username': username, 'points': 1000}
            asyncio.create_task(self.save_data())
            logger.info(f"已为用户 {user_id} 创建新账户，初始代币：1000")
        total_bet_amount = sum(bet['amount'] for bet in bets)
        if boss and boss.boss_id != user_id:
            if self.user_data[user_id]['points'] < total_bet_amount:
                logger.info(
                    f"用户 {user_id} 代币不足，尝试投入：{total_bet_amount}，当前代币：{self.user_data[user_id]['points']}")
                raise ValueError("您的代币不足以进行投入。")
            self.user_data[user_id]['points'] -= total_bet_amount
            period_number = self.generate_unique_period_number()  # 生成期号
            for bet in bets:
                self.log_history(user_id, f"{bet['type']} {bet['amount']} 用于游戏", -bet['amount'], period_number,
                                 bet_amount=bet['amount'], role='player')
                logger.info(f"用户 {user_id} 代币 {bet['amount']} （冻结）用于 {bet['type']}")

        period_number = self.generate_unique_period_number()
        self.active_games[user_id] = {
            'username': username,
            'bets': bets,
            'start_time': time.time(),
            'period_number': period_number,
            'boss': boss,
            'dice_rolls': []
        }
        logger.info(f"游戏已启动，用户ID：{user_id}，期号：{period_number}，总投入：{total_bet_amount}")

    async def roll_dice_for_game(self, message, user_id):
        game = self.active_games.get(user_id)
        if not game:
            await message.reply(content='❌ 未找到进行中的游戏。')
            logger.warning(f"未找到用户 {user_id} 的进行中游戏。")
            return
        if len(game['dice_rolls']) >= 3:
            await message.reply(content='❌ 您已经摇过所有的骰子了。')
            logger.warning(f"用户 {user_id} 尝试多次摇骰子。")
            return
        number = self.roll_dice()[0]
        game['dice_rolls'].append(number)
        dice_emoji = self.DICE_EMOJI[number]
        asyncio.create_task(self.save_data())  # 异步保存
        await message.reply(content=f"🎲 第{len(game['dice_rolls'])}个骰子结果：【{dice_emoji}】")
        logger.info(f"用户 {user_id} 摇骰子第{len(game['dice_rolls'])}个结果：{number}")
        if len(game['dice_rolls']) == 3:
            await self.process_game_result(message, user_id, game)

    async def process_game_result(self, message, user_id, game):
        numbers = game['dice_rolls']
        total = sum(numbers)
        bets = game['bets']
        total_winnings = 0
        details = []

        logger.info(f"处理游戏结果，用户ID：{user_id}, 骰子总和：{total}")

        for bet in bets:
            bet_type = bet['type']
            bet_amount = bet['amount']
            multiplier = self.get_multiplier(bet_type, total)

            logger.info(f"用户 {user_id} 投注类型：{bet_type}, 投注金额：{bet_amount}, 倍数：{multiplier}")

            if multiplier > 0:
                winnings = int(bet_amount * multiplier)
                total_winnings += winnings
                self.user_data[user_id]['points'] += winnings
                self.log_history(user_id, f"{bet_type} 赢得游戏，奖励 {winnings} 代币", winnings, game['period_number'],
                                 role='player')
                details.append(
                    f"✅ **{self.map_bet_type_display(bet_type)}**: 投入 **{bet_amount}** 代币，赢得 **{winnings}** 代币")

                boss = game.get('boss')
                if boss and boss.boss_id != user_id:
                    try:
                        boss.deduct_boss_points(winnings, game['period_number'])  # 传递期号
                        self.log_history(boss.boss_id, f'玩家 {user_id} 赢得游戏，扣除老板 {winnings} 代币', -winnings,
                                         game['period_number'], role='boss')
                        details.append(f"🔻 **老板**: 扣除 **{winnings}** 代币")
                    except ValueError as e:
                        logger.error(f"扣除老板 {boss.boss_id} 代币失败：{e}")
                        await message.reply(content='⚠️ 老板的代币不足以支付您的奖励。')
                        self.user_data[user_id]['points'] += bet_amount  # 返还
                        self.log_history(user_id, f'因老板余额不足，返还 {bet_amount} 代币', bet_amount,
                                         game['period_number'], role='player')
                        details.append(f"🔄 **返还**: {bet_amount} 代币")
            else:
                details.append(f"❌ **{self.map_bet_type_display(bet_type)}**: 投入 **{bet_amount}** 代币，未中奖")

                boss = game.get('boss')
                if boss and boss.boss_id != user_id:
                    boss.add_boss_points(bet_amount)
                    self.log_history(boss.boss_id, f'玩家 {user_id} 输掉游戏，老板获得 {bet_amount} 代币', bet_amount,
                                     game['period_number'], role='boss')
                    details.append(f"💹 **老板**: 获得 **{bet_amount}** 代币")

        # 构建结果消息
        emoji_numbers = [self.DICE_EMOJI[n] for n in numbers]
        analysis_message = (
            f"🎲 **游戏结果** 🎲\n"
            f"--------------------------------\n"
            f"结果：**{'、'.join(emoji_numbers)}**\n"
            f"总和：**{total}**\n\n"
            f"{'\n'.join(details)}\n"
            f"期号： {game['period_number']}\n"
            f"--------------------------------"
        )

        try:
            await message.reply(content=analysis_message)
            logger.info(f"已发送游戏结果给用户 {user_id}")
        except Exception as e:
            logger.error(f"发送游戏结果失败：{e}")
            await message.reply(content='抱歉，无法发送游戏结果。请稍后再试。')

        # 游戏完成后移除该用户的游戏状态
        self.active_games.pop(user_id, None)

    def map_bet_type_display(self, bet_type):
        mapping = {
            'da': '大',
            '大': '大',
            'x': '小',  # 新增 'x' 映射
            'xiao': '小',
            '小': '小',
            'dd': '大单',
            '大单': '大单',
            'ds': '大双',
            '大双': '大双',
            'xd': '小单',
            '小单': '小单',
            'xs': '小双',
            '小双': '小双',
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
        return mapping.get(bet_type, bet_type)

    def roll_dice(self):
        return [random.randint(1, 6) for _ in range(1)]

    def judge_result(self, total):
        return '大' if total >= 11 else '小'

    def get_multiplier_static(self, bet_type):
        return self.bet_multipliers.get(bet_type, 0)

    def get_multiplier(self, bet_type, total):
        # 映射缩写到完整类型
        bet_type_map = {
            'da': '大',
            'x': '小',  # 新增 'x' 映射
            'xiao': '小',
            'dd': '大单',
            'ds': '大双',
            'xd': '小单',
            'xs': '小双',
        }
        mapped_bet_type = bet_type_map.get(bet_type, bet_type)

        if mapped_bet_type in ['大', '小', '大单', '大双', '小单', '小双']:
            return self.bet_multipliers.get(mapped_bet_type, 0) if self.is_bet_win(mapped_bet_type, total) else 0
        else:
            # 具体总和投入
            try:
                bet_sum = int(mapped_bet_type)
                return self.bet_multipliers.get(str(bet_sum), 0) if total == bet_sum else 0
            except ValueError:
                return 0

    def is_bet_win(self, bet_type, total):
        if bet_type == '大':
            return total >= 11
        elif bet_type == '小':
            return total <= 10
        elif bet_type == '大单':
            return total >= 11 and total % 2 != 0
        elif bet_type == '大双':
            return total >= 11 and total % 2 == 0
        elif bet_type == '小单':
            return total <= 10 and total % 2 != 0
        elif bet_type == '小双':
            return total <= 10 and total % 2 == 0
        return False

    def cancel_game(self, user_id):
        if user_id in self.active_games:
            game = self.active_games[user_id]
            if len(game['dice_rolls']) > 0:
                logger.info(f"用户 {user_id} 尝试取消已开始的游戏。")
                return 'started'
            # 返还所有投入
            total_refund = sum(bet['amount'] for bet in game['bets'])
            self.user_data[user_id]['points'] += total_refund
            for bet in game['bets']:
                self.log_history(user_id, f'取消游戏，返还 {bet["amount"]} 代币', bet['amount'], game['period_number'],
                                 bet_amount=bet['amount'], role='player')
                logger.info(f"用户 {user_id} 成功取消游戏，返还 {bet['amount']} 代币")
            asyncio.create_task(self.save_data())  # 异步保存
            self.active_games.pop(user_id, None)
            return 'success'
        logger.info(f"用户 {user_id} 尝试取消不存在的游戏")
        return 'not_started'
