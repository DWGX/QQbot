# Boss.py

import asyncio
import logging
import random
import string
import time

logger = logging.getLogger("Boss")


class Boss:
    def __init__(self, data, user_data, save_data, data_manager):
        self.data = data
        self.user_data = user_data
        self._save_data = save_data
        self.data_manager = data_manager
        self.boss_id = self.data.get("boss_id")

    async def create_boss_account(self):
        if not self.boss_id:
            internal_id = self.data_manager.generate_internal_id()
            self.user_data[internal_id] = {'userid': None, 'username': '默认负责人', 'points': 1000000}
            self.data["boss_id"] = internal_id
            await self._save_data()  # 确保保存是等待的
            self.boss_id = internal_id
            logger.info(f"创建默认负责人账户，ID: {internal_id}")

    async def handle_boss_command(self, userid, action):
        if action == 'become':

            internal_id = await self.data_manager.get_or_create_user(userid, '负责人用户')
            previous_boss = self.boss_id
            self.boss_id = internal_id
            self.data["boss_id"] = internal_id
            await self._save_data()
            logger.info(f"用户 {userid} 成为新的负责人。")
            if previous_boss and previous_boss != internal_id:
                return "✅ 您已成为新的负责人。"
            return "✅ 您已成功成为负责人。"
        elif action == 'leave':
            if self.boss_id and self.data_manager.get_userid(self.boss_id) == userid:
                self.boss_id = None
                self.data["boss_id"] = None
                await self._save_data()
                logger.info(f"用户 {userid} 离开了负责人职位。")
                return "✅ 您已成功离开负责人职位。"
            else:
                return "❌ 您当前不是负责人。"
        else:
            return "❓ 无效的操作。"

    def deduct_boss_points(self, amount):
        if self.boss_id not in self.user_data:
            raise ValueError("负责人账户不存在。")
        if self.user_data[self.boss_id]['points'] < amount:
            raise ValueError("负责人的代币不足。")
        self.user_data[self.boss_id]['points'] -= amount
        self.log_history(self.boss_id, f"扣除 {amount} 代币用于支付奖励", -amount, "system", role='system')
        asyncio.create_task(self._save_data())
        logger.info(f"负责人 {self.boss_id} 扣除 {amount} 代币，当前余额：{self.user_data[self.boss_id]['points']}")

    def add_boss_points(self, amount):
        if self.boss_id not in self.user_data:
            raise ValueError("负责人账户不存在。")
        self.user_data[self.boss_id]['points'] += amount
        self.log_history(self.boss_id, f"增加 {amount} 代币作为负责人收益", amount, "system", role='system')
        asyncio.create_task(self._save_data())
        logger.info(f"负责人 {self.boss_id} 增加 {amount} 代币，当前余额：{self.user_data[self.boss_id]['points']}")

    def log_history(self, user_id, description, points_change, period_number, bet_amount=None, role='system'):
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
        if user_id not in self.data["game_history"]:
            self.data["game_history"][user_id] = []
        self.data["game_history"][user_id].append(history_record)
        asyncio.create_task(self._save_data())
        logger.info(f"负责人游戏历史已更新，用户ID：{user_id}")
