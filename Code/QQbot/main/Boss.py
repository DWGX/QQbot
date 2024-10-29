import asyncio
import logging

logger = logging.getLogger("Boss")

class Boss:
    def __init__(self, data, user_data, save_data, gambling, data_manager):
        self.data = data
        self.user_data = user_data
        self.save_data = save_data
        self.gambling = gambling
        self.data_manager = data_manager
        self.boss_id = self.data.get('boss_id')

    async def handle_boss_command(self, userid, action):
        internal_id = self.data_manager.data["userid_to_internal"].get(userid)
        if not internal_id:
            return '❌ 未找到您的用户信息。'

        if action == 'become':
            if self.boss_id:
                return '❌ 当前已经有老板了。'
            self.boss_id = internal_id
            self.data['boss_id'] = internal_id
            self.user_data[internal_id]['points'] += 5000
            await self.save_data()
            logger.info(f"用户 {internal_id} 成为老板。")
            return '✅ 您已成功成为老板，获得额外 **5000** 代币。'
        elif action == 'leave':
            if self.boss_id != internal_id:
                return '❌ 您当前不是老板。'
            self.boss_id = None
            self.data['boss_id'] = None
            await self.save_data()
            logger.info(f"用户 {internal_id} 离开老板职位。")
            return '✅ 您已成功离开老板职位。'
        else:
            return '❓ 无效的操作。'

    def deduct_boss_points(self, amount):
        if not self.boss_id or self.boss_id not in self.user_data:
            raise ValueError("老板账户不存在。")
        if self.user_data[self.boss_id]['points'] < amount:
            raise ValueError("老板的代币不足。")
        self.user_data[self.boss_id]['points'] -= amount
        logger.debug(f"从老板账户扣除了 {amount} 代币。")

    def add_boss_points(self, amount):
        if not self.boss_id or self.boss_id not in self.user_data:
            raise ValueError("老板账户不存在。")
        self.user_data[self.boss_id]['points'] += amount
        logger.debug(f"向老板账户添加了 {amount} 代币。")
