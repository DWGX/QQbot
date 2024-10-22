import asyncio
import logging

logger = logging.getLogger("Boss")


class Boss:
    def __init__(self, data, user_data, admin_ids, save_data, gambling, boss_id=None):
        self.data = data  # 引用整个 data
        self.user_data = user_data
        self.admin_ids = admin_ids
        self.save_data = save_data
        self.gambling = gambling  # 确保参数名与实例一致
        self.boss_id = data.get("boss_id")

    async def handle_boss_command(self, user_id, message, action):
        if action == 'become':
            if self.boss_id:
                return '⚠️ 已经有老板了，您不能成为老板。'
            self.set_boss(user_id)
            # 初始化老板的账户，如果尚未存在
            if user_id not in self.user_data:
                self.user_data[user_id] = {'username': '老板', 'points': 10000}
                asyncio.create_task(self.save_data())  # 异步保存
                logger.info(f"已为老板 {user_id} 创建账户，初始代币：10000")
            boss_balance = self.user_data[user_id].get('points', 0)
            return f"🎉 你现在是老板！当前余额：**{boss_balance}** 代。"
        elif action == 'leave':
            if self.gambling.active_games:
                return '⚠️ 当前仍有进行中的游戏，无法卸任老板。'
            if self.boss_id != user_id:
                return '❌ 您当前不是老板，无需卸任。'
            self.leave_boss()
            return '✅ 您已成功卸任老板。'
        else:
            return '❓ 未知的操作。'

    def set_boss(self, user_id):
        self.boss_id = user_id
        self.data["boss_id"] = user_id  # 更新 data['boss_id']
        asyncio.create_task(self.save_data())  # 异步保存
        logger.info(f"老板已设置为用户 {user_id}")

    def leave_boss(self):
        self.boss_id = None
        self.data["boss_id"] = None  # 清空 data['boss_id']
        asyncio.create_task(self.save_data())  # 异步保存
        logger.info("老板身份已被卸任。")

    def add_boss_points(self, points, period_number='N/A'):
        if not self.boss_id:
            raise ValueError("⚠️ 当前没有老板。")
        if self.boss_id not in self.user_data:
            self.user_data[self.boss_id] = {'username': '老板', 'points': 0}
        self.user_data[self.boss_id]['points'] += points
        self.gambling.log_history(
            self.boss_id,
            f'赢得游戏，奖励 {points} 代币',
            points,
            period_number=period_number,  # 传递期号
            role='boss'
        )
        asyncio.create_task(self.save_data())  # 异步保存
        logger.info(f"已为老板 {self.boss_id} 增加 {points} 代币。")

    def deduct_boss_points(self, points, period_number):
        if not self.boss_id:
            raise ValueError("⚠️ 当前没有老板。")
        if self.boss_id not in self.user_data:
            raise ValueError("⚠️ 老板账户不存在。")
        if self.user_data[self.boss_id]['points'] < points:
            raise ValueError("⚠️ 老板的代币不足。")
        self.user_data[self.boss_id]['points'] -= points
        self.gambling.log_history(
            self.boss_id,
            f'扣除 {points} 代币用于支付',
            -points,
            period_number=period_number,  # 传递期号
            role='boss'
        )
        asyncio.create_task(self.save_data())  # 异步保存
        logger.info(f"已从老板 {self.boss_id} 扣除 {points} 代币。")
