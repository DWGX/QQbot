# DataManager.py

import json
import os
import yaml
import asyncio
import logging
import string
import random

logger = logging.getLogger("DataManager")


def replace_sets(obj):
    if isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, dict):
        return {k: replace_sets(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_sets(item) for item in obj]
    else:
        return obj


class DataManager:
    def __init__(self, config_file='config.yaml', data_file='data.json'):
        self.config_file = config_file
        self.data_file = data_file
        self.data = None
        self.data_lock = asyncio.Lock()
        self.load_config()
        self.load_data()

    def load_config(self):
        if not os.path.exists(self.config_file):
            logger.error(f"配置文件 {self.config_file} 不存在。请创建并填写 appid 和 secret。")
            exit(1)
        with open(self.config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        self.appid = config.get('appid')
        self.secret = config.get('secret')
        if not self.appid or not self.secret:
            logger.error(f"配置文件 {self.config_file} 缺少 appid 或 secret。请填写完整。")
            exit(1)

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                self.data.setdefault("boss_id", None)
                self.data.setdefault("user_data", {})
                self.data.setdefault("game_history", {})
                self.data.setdefault("red_envelopes", {})
                self.data["game_history"].setdefault("period_numbers", set())
                self.data.setdefault("internal_to_userid", {})
                self.data.setdefault("userid_to_internal", {})

                if isinstance(self.data["game_history"].get("period_numbers"), list):
                    self.data["game_history"]["period_numbers"] = set(self.data["game_history"]["period_numbers"])
                logger.info("数据文件加载成功。")
            except json.JSONDecodeError:
                logger.error(f"{self.data_file} 格式错误，重新初始化。")
                self.data = {
                    "boss_id": None,
                    "user_data": {},
                    "game_history": {
                        "period_numbers": set()
                    },
                    "red_envelopes": {},
                    "internal_to_userid": {},
                    "userid_to_internal": {}
                }
                # 同步保存初始化数据
                self._sync_save_data()
        else:
            self.data = {
                "boss_id": None,
                "user_data": {},
                "game_history": {
                    "period_numbers": set()
                },
                "red_envelopes": {},
                "internal_to_userid": {},
                "userid_to_internal": {}
            }
            self._sync_save_data()
            logger.info("未找到数据文件，初始化为空。")

    def _sync_save_data(self):
        data_copy = replace_sets(self.data.copy())
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data_copy, f, ensure_ascii=False, indent=4)
        logger.info("数据文件同步保存成功。")

    async def save_data(self):
        async with self.data_lock:
            try:
                data_copy = replace_sets(self.data.copy())
                with open(self.data_file, 'w', encoding='utf-8') as f:
                    json.dump(data_copy, f, ensure_ascii=False, indent=4)
                logger.info("数据文件保存成功。")
            except Exception:
                logger.exception("保存数据文件时发生错误。")

    async def get_or_create_user(self, userid, username):
        async with self.data_lock:
            if userid not in self.data.get("userid_to_internal", {}):
                internal_id = self.generate_internal_id()
                self.data["user_data"][internal_id] = {'userid': userid, 'username': username, 'points': 1000}
                self.data["internal_to_userid"][internal_id] = userid
                self.data["userid_to_internal"][userid] = internal_id
                await self.save_data()
                logger.info(f"创建新用户 {internal_id} - {username} (User ID: {userid})，初始代币：1000")
            return self.data["userid_to_internal"][userid]

    def get_username(self, internal_id):
        return self.data.get("user_data", {}).get(internal_id, {}).get("username", "未知")

    def get_userid(self, internal_id):
        return self.data.get("user_data", {}).get(internal_id, {}).get("userid", "未知")

    def generate_internal_id(self):
        while True:
            internal_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            if internal_id not in self.data.get("user_data", {}):
                return internal_id
