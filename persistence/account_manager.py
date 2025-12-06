"""
账号管理：注册、登录、战绩存储
"""
import json
import os
import hashlib
import secrets
from typing import Dict, List, Optional
from ..exceptions import FileOperationException


class AccountManager:
    """简单的本地账号管理器"""

    def __init__(self, filepath: str = "accounts.json"):
        self.filepath = filepath
        self._accounts = self._load_accounts()

    def _load_accounts(self) -> Dict[str, Dict]:
        if not os.path.exists(self.filepath):
            return {}
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            raise FileOperationException(f"读取账号文件失败: {e}")

    def _save_accounts(self):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self._accounts, f, ensure_ascii=False, indent=2)
        except OSError as e:
            raise FileOperationException(f"保存账号文件失败: {e}")

    def _hash_password(self, password: str, salt: str) -> str:
        return hashlib.sha256(f"{password}{salt}".encode("utf-8")).hexdigest()

    def register(self, username: str, password: str) -> Dict:
        if username in self._accounts:
            raise FileOperationException("用户已存在")
        salt = secrets.token_hex(8)
        password_hash = self._hash_password(password, salt)
        self._accounts[username] = {
            "password": password_hash,
            "salt": salt,
            "stats": {"games": 0, "wins": 0},
            "history": [],
        }
        self._save_accounts()
        return self.get_profile(username)

    def login(self, username: str, password: str) -> Dict:
        if username not in self._accounts:
            raise FileOperationException("用户不存在")
        record = self._accounts[username]
        if record["password"] != self._hash_password(password, record["salt"]):
            raise FileOperationException("密码错误")
        return self.get_profile(username)

    def get_profile(self, username: str) -> Dict:
        record = self._accounts.get(username)
        if not record:
            raise FileOperationException("用户不存在")
        return {
            "username": username,
            "stats": record.get("stats", {"games": 0, "wins": 0}),
        }

    def update_stats(self, username: str, win: bool):
        if username not in self._accounts:
            return
        stats = self._accounts[username].setdefault("stats", {"games": 0, "wins": 0})
        stats["games"] = stats.get("games", 0) + 1
        if win:
            stats["wins"] = stats.get("wins", 0) + 1
        self._save_accounts()

    def add_history(self, username: str, entry: Dict):
        record = self._accounts.get(username)
        if not record:
            return
        history: List[Dict] = record.setdefault("history", [])
        history.append(entry)
        self._save_accounts()

    def get_history(self, username: str) -> List[Dict]:
        record = self._accounts.get(username)
        if not record:
            raise FileOperationException("用户不存在")
        return record.get("history", [])
