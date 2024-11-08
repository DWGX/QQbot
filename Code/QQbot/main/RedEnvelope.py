# RedEnvelope.py

import asyncio
import logging
import random
import re
from datetime import datetime
from botpy.message import Message
from botpy.errors import ServerError

logger = logging.getLogger("RedEnvelope")


class RedEnvelope:
    def __init__(self, data, user_data, save_data, admins, data_manager):
        self.data = data
        self.user_data = user_data
        self._save_data = save_data
        self.admins = admins
        self.data_manager = data_manager
        self.red_envelopes = self.data.get("red_envelopes", {})

    async def handle_command(self, message: Message, parts: list, userid: str):
        if not parts:
            await message.reply(content='❓ 未知红包指令。')
            return

        command = parts[0].lower()

        if command == 'hb':
            if len(parts) == 3 and parts[1].isdigit() and parts[2].isdigit():

                try:
                    amount = int(parts[1])
                    num = int(parts[2])
                    if amount <= 0 or num <= 0:
                        raise ValueError
                    await self.send_public_red_envelope(message, userid, amount, num)
                except ValueError:
                    await message.reply(content='❌ 无效的金额或领取人数。请使用格式：@机器人 hb <金额> <领取人数>')
            elif len(parts) == 3 and parts[1].startswith('@'):

                try:
                    target_user_mention = parts[1]
                    amount = int(parts[2])
                    if amount <= 0:
                        raise ValueError
                    await self.send_private_red_envelope(message, userid, target_user_mention, amount)
                except ValueError:
                    await message.reply(content='❌ 无效的金额。请使用格式：@机器人 hb @用户名 <金额>')
            elif len(parts) == 2 and parts[1].lower() == '确认':

                await self.confirm_send_red_envelope(message, userid)
            else:
                await message.reply(content='❓ 未知红包指令。')
        elif command == '领取':
            if len(parts) == 2:
                period_number = parts[1].replace('红包', '').strip()
                await self.receive_red_envelope(message, userid, period_number)
            else:
                await message.reply(content='❌ 请提供要领取的红包期号。例如：@机器人 领取202410242141p红包')
        elif command == '撤回':
            if len(parts) == 2:
                period_number = parts[1].replace('红包', '').strip()
                await self.withdraw_red_envelope(message, userid, period_number)
            else:
                await message.reply(content='❌ 请提供要撤回的红包期号。例如：@机器人 撤回202410242141p红包')
        else:
            await message.reply(content='❓ 未知红包指令。')

    async def send_public_red_envelope(self, message: Message, userid: str, amount: int, num: int):

        internal_id = await self.data_manager.get_or_create_user(userid, message.author.username)
        user_points = self.user_data[internal_id]['points']
        if user_points < amount:
            await message.reply(content=f'❌ 您的代币不足，当前代币：**{user_points}**。')
            return

        self.user_data[internal_id]['points'] -= amount
        await self._save_data()

        envelopes = self.divide_amount(amount, num)

        period_number = self.generate_unique_period_number()

        self.red_envelopes[period_number] = {
            'type': 'public',
            'amount': amount,
            'remaining': envelopes.copy(),
            'received': {},
            'sender_id': internal_id
        }
        await self._save_data()

        envelope_message = (
            f"🎁 **公开红包已发送！** 🎁\n"
            f"总金额：**{amount}** 代币\n"
            f"领取人数：**{num}**\n"
            f"期号：**{period_number}**\n"
            f"请尽快领取红包！"
        )
        try:
            await message.reply(content=envelope_message)
            logger.info(f"用户 {internal_id} 发送公开红包，期号：{period_number}，金额：{amount}，人数：{num}")
        except ServerError:
            await message.reply(content='❌ 无法发送红包信息，请稍后再试。')

    async def send_private_red_envelope(self, message: Message, userid: str, target_user_mention: str, amount: int):

        internal_id = await self.data_manager.get_or_create_user(userid, message.author.username)
        user_points = self.user_data[internal_id]['points']
        if user_points < amount:
            await message.reply(content=f'❌ 您的代币不足，当前代币：**{user_points}**。')
            return

        self.user_data[internal_id]['points'] -= amount
        await self._save_data()

        envelopes = [amount]

        period_number = self.generate_unique_period_number()

        self.red_envelopes[period_number] = {
            'type': 'private',
            'amount': amount,
            'remaining': envelopes.copy(),
            'received': {},
            'sender_id': internal_id,
            'target': target_user_mention
        }
        await self._save_data()

        envelope_message = (
            f"🎁 **私密红包已发送！** 🎁\n"
            f"总金额：**{amount}** 代币\n"
            f"目标用户：**{target_user_mention}**\n"
            f"期号：**{period_number}**\n"
            f"请尽快领取红包！"
        )
        try:
            await message.reply(content=envelope_message)
            logger.info(f"用户 {internal_id} 发送私密红包，期号：{period_number}，金额：{amount}，目标：{target_user_mention}")
        except ServerError:
            await message.reply(content='❌ 无法发送红包信息，请稍后再试。')

    async def confirm_send_red_envelope(self, message: Message, userid: str):

        await message.reply(content='🔔 **确认发送红包功能尚未实现。**')

    async def receive_red_envelope(self, message: Message, userid: str, period_number: str):

        envelope = self.red_envelopes.get(period_number)
        if not envelope:
            await message.reply(content='❌ 未找到指定期号的红包。')
            return

        if envelope['type'] == 'private':

            target_user = envelope.get('target')
            if not target_user or target_user not in message.mentions:
                await message.reply(content='❌ 您无权领取此私密红包。')
                return

        if envelope['remaining']:
            amount = envelope['remaining'].pop()

            internal_id = await self.data_manager.get_or_create_user(userid, message.author.username)
            self.user_data[internal_id]['points'] += amount
            envelope['received'][internal_id] = envelope['received'].get(internal_id, 0) + amount
            await self._save_data()
            await message.reply(content=f"🎉 您已成功领取 **{amount}** 代币！")
            logger.info(f"用户 {internal_id} 领取红包，期号：{period_number}，金额：{amount}")
        else:
            await message.reply(content='❌ 此红包已被全部领取完毕。')

    async def withdraw_red_envelope(self, message: Message, userid: str, period_number: str):

        if userid not in self.admins:
            await message.reply(content='❌ 您没有权限撤回红包。')
            return

        envelope = self.red_envelopes.get(period_number)
        if not envelope:
            await message.reply(content='❌ 未找到指定期号的红包。')
            return

        remaining = envelope.get('remaining', [])
        total_refund = sum(remaining)
        sender_id = envelope.get('sender_id')
        if sender_id and sender_id in self.user_data:
            self.user_data[sender_id]['points'] += total_refund
            logger.info(f"撤回红包，返还用户 {sender_id} {total_refund} 代币。")
            await self._save_data()
            await message.reply(content=f"✅ 红包 {period_number} 已被撤回，已返还 **{total_refund}** 代币给发送者。")
        else:
            await message.reply(content='❌ 发送者账户不存在，无法返还代币。')

    def generate_unique_period_number(self):
        while True:
            date_time = datetime.now().strftime("%Y%m%d%H%M%S")
            random_str = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=4))
            unique_id = f"{date_time}{random_str}"
            if unique_id not in self.red_envelopes:
                break
        logger.debug(f"生成唯一期号：{unique_id}")
        return unique_id

    def divide_amount(self, amount, num):
        if num <= 0:
            return []
        base = amount // num
        envelopes = [base] * num
        remainder = amount % num
        for i in range(remainder):
            envelopes[i] += 1
        random.shuffle(envelopes)
        return envelopes
