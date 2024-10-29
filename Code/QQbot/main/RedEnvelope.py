import asyncio
import logging
import time
import string
import random
from datetime import datetime
from botpy.message import Message
from botpy.errors import ServerError

from Assist import Assist

logger = logging.getLogger("RedEnvelope")

class RedEnvelope:
    def __init__(self, data, user_data, save_data, admins, data_manager):
        self.data = data
        self.user_data = user_data
        self.save_data = save_data
        self.admins = admins
        self.data_manager = data_manager

    def generate_unique_id(self):
        while True:
            now = datetime.now()
            base_id = now.strftime("%Y%m%d%H%M%S")
            suffix = ''.join(random.choices(string.ascii_lowercase, k=1))
            unique_id = f"{base_id}{suffix}"
            if unique_id not in self.data.get("red_envelopes", {}):
                break
        logger.debug(f"生成唯一红包ID：{unique_id}")
        return unique_id

    async def handle_command(self, message: Message, parts: list, userid: str):
        if not parts:
            await Assist.show_help(message)
            return

        command_methods = {
            'hb': self._handle_hb_command,
            '领取': self._handle_claim_command,
            '撤回': self._handle_revoke_command,
        }

        command = parts[0].lower()
        handler = command_methods.get(command)
        if handler:
            await handler(message, parts, userid)
        else:
            await message.reply(content='❓ 未知指令。请输入 帮助 或 help 查看可用指令。')

    async def _handle_hb_command(self, message: Message, parts: list, userid: str):
        subcommand = parts[1].lower() if len(parts) > 1 else None
        subcommand_methods = {
            '确认': self.confirm_red_envelope,
        }

        if subcommand in subcommand_methods:
            await subcommand_methods[subcommand](message, userid)
        elif len(parts) == 3 and parts[1].startswith('@'):
            await self._initiate_private_red_envelope_with_mention(message, parts, userid)
        else:
            await self._initiate_public_red_envelope_with_amount(message, parts, userid)

    async def _handle_claim_command(self, message: Message, parts: list, userid: str):
        if len(parts) < 2:
            await message.reply(content='❌ 请提供红包的期号。例如：@机器人 领取202410242141p红包')
            return
        envelope_id = parts[1].replace('红包', '').strip()
        await self.claim_red_envelope(message, envelope_id, userid)

    async def _handle_revoke_command(self, message: Message, parts: list, userid: str):
        if len(parts) < 2:
            await message.reply(content='❌ 请提供要撤回的红包期号。例如：@机器人 撤回202410242141p红包')
            return
        envelope_id = parts[1].replace('红包', '').strip()
        await self.revoke_red_envelope(message, envelope_id, userid)

    async def _initiate_private_red_envelope_with_mention(self, message, parts: list, userid: str):
        if not message.mentions:
            await message.reply(content='❌ 请在指令中提及要发送红包的用户。例如：@机器人 hb @用户名 100')
            return
        target_member = message.mentions[0]
        target_userid = str(target_member.id)
        try:
            amount = int(parts[2])
        except (IndexError, ValueError):
            await message.reply(content='❌ 无效的金额，请输入正确的代币数量。例如：@机器人 hb @用户名 100')
            return
        await self.initiate_private_red_envelope(message, target_userid, amount)

    async def _initiate_public_red_envelope_with_amount(self, message: Message, parts: list, userid: str):
        if len(parts) < 3:
            await message.reply(content='❌ 请提供金额和领取人数。例如：@机器人 hb 100 5')
            return
        try:
            amount = int(parts[1])
            recipients = int(parts[2])
        except ValueError:
            await message.reply(content='❌ 无效的参数，请输入正确的金额和领取人数。例如：@机器人 hb 100 5')
            return
        await self.initiate_public_red_envelope(message, amount, recipients, userid)

    async def initiate_public_red_envelope(self, message: Message, amount: int, recipients: int, userid: str):
        if not self._validate_amount_and_recipients(message, amount, recipients):
            return

        internal_id = await self.data_manager.get_or_create_user(userid, message.author.username)
        username = self.data["user_data"][internal_id]['username']
        user_points = self.data["user_data"][internal_id]['points']
        if amount > user_points:
            await message.reply(content=f'❌ 您的代币不足，当前代币：**{user_points}** 个。')
            return

        self._deduct_user_points(internal_id, amount)
        envelope_id = self.generate_unique_id()
        split_amounts = self.split_amount_random(amount, recipients)

        self.data.setdefault("red_envelopes", {})[envelope_id] = {
            'sender_internal_id': internal_id,
            'sender_name': username,
            'total_amount': amount,
            'split_amounts': split_amounts,
            'recipients': [],  # 公开红包不指定接收者
            'claimed': [False] * len(split_amounts),
            'claimed_by': [None] * len(split_amounts),
            'timestamp': int(time.time()),
            'type': 'public',
            'status': 'pending'
        }
        await self.save_data()
        await message.reply(content=f"📦 红包已创建，期号：**{envelope_id}**。请发送 @机器人 hb 确认 以正式发送红包。")
        logger.info(f"创建公开红包，期号：{envelope_id}，金额：{amount}，领取人数：{recipients}")

    async def initiate_private_red_envelope(self, message: Message, target_userid: str, amount: int):
        if not self._validate_amount(message, amount):
            return

        target_internal_id = self.data_manager.data["userid_to_internal"].get(target_userid)
        if not target_internal_id:
            target_internal_id = await self.data_manager.get_or_create_user(target_userid, message.mentions[0].username)
        username = self.user_data[target_internal_id]['username']
        user_points = self.user_data[target_internal_id]['points']
        if amount > user_points:
            await message.reply(content=f'❌ 被发送者的代币不足，当前代币：**{user_points}** 个。')
            return

        self._deduct_user_points(target_internal_id, amount)
        envelope_id = self.generate_unique_id()
        split_amounts = [amount]

        self.data.setdefault("red_envelopes", {})[envelope_id] = {
            'sender_internal_id': target_internal_id,
            'sender_name': username,
            'total_amount': amount,
            'split_amounts': split_amounts,
            'recipients': [target_internal_id],
            'claimed': [False],
            'claimed_by': [None],
            'timestamp': int(time.time()),
            'type': 'private',
            'status': 'pending'
        }
        await self.save_data()
        await message.reply(content=f"📦 私密红包已创建，期号：**{envelope_id}**。请发送 @机器人 hb 确认 以正式发送红包。")
        logger.info(f"创建私密红包，期号：{envelope_id}，金额：{amount}，接收者：{target_internal_id}")

    def _get_user_info(self, internal_id: str):
        username = self.user_data.get(internal_id, {}).get('username', '未知')
        user_points = int(self.user_data.get(internal_id, {}).get('points', 0))
        return internal_id, username, user_points

    def _deduct_user_points(self, internal_id: str, amount: int):
        self.user_data[internal_id]['points'] -= amount
        logger.debug(f"从用户 {internal_id} 扣除了 {amount} 代币。")

    @staticmethod
    def _validate_amount_and_recipients(message: Message, amount: int, recipients: int) -> bool:
        if amount <= 0:
            asyncio.create_task(message.reply(content='❌ 红包金额必须大于0。'))
            return False
        if recipients <= 0:
            asyncio.create_task(message.reply(content='❌ 领取人数必须大于0。'))
            return False
        return True

    @staticmethod
    def _validate_amount(message: Message, amount: int) -> bool:
        if amount <= 0:
            asyncio.create_task(message.reply(content='❌ 红包金额必须大于0。'))
            return False
        return True

    async def confirm_red_envelope(self, message: Message, userid: str):
        internal_id = self.data["userid_to_internal"].get(userid)
        if not internal_id:
            await message.reply(content='❌ 未找到您的用户信息。')
            return

        pending_envelopes = {
            eid: env for eid, env in self.data.get("red_envelopes", {}).items()
            if env['sender_internal_id'] == internal_id and env['status'] == 'pending'
        }
        if not pending_envelopes:
            await message.reply(content='❌ 您当前没有待确认的红包。')
            return
        for envelope_id, envelope in pending_envelopes.items():
            self.data["red_envelopes"][envelope_id]['status'] = 'sent'
            envelope_type = envelope['type']
            amount = envelope['total_amount']
            try:
                if envelope_type == 'public':
                    await message.reply(content=(
                        f"🎁 **公开红包发送成功！** 🎁\n"
                        f"期号：**{envelope_id}**\n"
                        f"金额：**{amount}** 代币\n"
                        f"领取人数：**{len(envelope['split_amounts'])}**\n"
                        f"请用户发送 @机器人 领取{envelope_id}红包 来领取红包。"
                    ))
                elif envelope_type == 'private':
                    target_internal_id = envelope['recipients'][0]
                    target_userid = self.data["internal_to_userid"].get(target_internal_id, "未知")
                    await message.reply(content=(
                        f"🎁 **私密红包发送成功！** 🎁\n"
                        f"期号：**{envelope_id}**\n"
                        f"金额：**{amount}** 代币\n"
                        f"接收者：<@{target_userid}>\n"
                        f"请接收者发送 @机器人 领取{envelope_id}红包 以领取。"
                    ))
            except ServerError:
                await message.reply(content='❌ 发送红包消息时发生错误，请稍后再试。')
                logger.error(f"发送红包 {envelope_id} 时发生错误。")
        await self.save_data()
        logger.info(f"确认并发送了 {len(pending_envelopes)} 个红包。")

    async def claim_red_envelope(self, message: Message, envelope_id: str, userid: str):
        internal_id = self.data["userid_to_internal"].get(userid)
        if not internal_id:
            await message.reply(content='❌ 未找到您的用户信息。')
            return

        envelope = self.data.get("red_envelopes", {}).get(envelope_id)
        if not envelope:
            await message.reply(content='❌ 找不到指定的红包。')
            return
        sender_internal_id = envelope['sender_internal_id']
        envelope_type = envelope.get('type', 'public')
        split_amounts = envelope['split_amounts']
        claimed = envelope['claimed']
        claimed_by = envelope['claimed_by']

        if envelope_type == 'private' and internal_id not in envelope['recipients']:
            await message.reply(content='❌ 您没有权限领取这个红包。')
            return

        if envelope_type == 'public':
            available_indices = [i for i, x in enumerate(claimed) if not x]
            if not available_indices:
                await message.reply(content='❌ 这个红包已经被全部领取。')
                return
            chosen_index = random.choice(available_indices)
        elif envelope_type == 'private':
            chosen_index = 0
            if claimed[chosen_index]:
                await message.reply(content='❌ 您已经领取过这个红包。')
                return
        else:
            await message.reply(content='❌ 未知的红包类型。')
            return

        if internal_id == sender_internal_id:
            await message.reply(content='❌ 您无法领取您自己发送的红包。')
            return

        envelope['claimed'][chosen_index] = True
        envelope['claimed_by'][chosen_index] = internal_id

        amount = split_amounts[chosen_index]
        self.user_data[internal_id]['points'] += amount
        await self.save_data()
        try:
            await message.reply(content=f"🎉 恭喜您成功领取了 **{amount}** 代币红包！\n来自：**{envelope['sender_name']}**")
            logger.info(f"用户 {internal_id} 领取了红包 {envelope_id}，金额：{amount}。")
        except ServerError:
            await message.reply(content='❌ 领取红包时发生错误，请稍后再试。')
            logger.error(f"发送领取红包消息时发生错误，用户 {internal_id}，红包 {envelope_id}。")

    async def revoke_red_envelope(self, message: Message, envelope_id: str, userid: str):
        if userid not in self.admins:
            await message.reply(content='❌ 您没有权限撤回红包。')
            return

        envelope = self.data.get("red_envelopes", {}).get(envelope_id)
        if not envelope:
            await message.reply(content='❌ 找不到指定的红包。')
            return

        if any(envelope['claimed']):
            await message.reply(content='❌ 该红包已被部分领取，无法完全撤回。')
            return

        sender_internal_id = envelope['sender_internal_id']
        sender = self.user_data.get(sender_internal_id)
        if sender:
            sender['points'] += envelope['total_amount']
            del self.data["red_envelopes"][envelope_id]
            await self.save_data()
            try:
                await message.reply(content=f"✅ 您已成功撤回红包 **{envelope_id}**，金额 **{envelope['total_amount']}** 代币已返还。")
                logger.info(f"管理员 {userid} 撤回了红包 {envelope_id}，金额：{envelope['total_amount']}。")
            except ServerError:
                await message.reply(content='❌ 撤回红包时发生错误，请稍后再试。')
                logger.error(f"发送撤回红包消息时发生错误，管理员 {userid}，红包 {envelope_id}。")
        else:
            await message.reply(content='❌ 发送者账户不存在，无法返还代币。')
            logger.error(f"撤回红包失败，发送者 {sender_internal_id} 不存在。")

    @staticmethod
    def split_amount_random(total_amount, recipients):
        if recipients <= 0:
            return []
        amounts = []
        remaining = total_amount
        for i in range(recipients - 1):
            max_amount = remaining - (recipients - i - 1)
            amount = random.randint(1, max_amount)
            amounts.append(amount)
            remaining -= amount
        amounts.append(remaining)
        random.shuffle(amounts)
        logger.debug(f"随机拆分金额：{amounts}")
        return amounts

