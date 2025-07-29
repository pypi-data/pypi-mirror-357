# =================================================================
# == nonebot_plugin_binance/auth.py
# == 说明：用户API密钥的认证和安全管理。
# =================================================================
import json
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken
from typing import Optional, Tuple, Dict
from nonebot import logger

from .config import binance_data_path


class AuthManager:
    def __init__(self, master_key: str):
        self._keys: Dict[str, Dict[str, str]] = {}
        self.data_dir = Path(binance_data_path)
        self.keys_file = self.data_dir / "user_keys.json"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 使用主密钥生成加密套件
        # 注意：主密钥必须是32字节的URL安全base64编码字符串
        try:
            self._cipher = Fernet(master_key.encode())
            logger.info("认证管理器初始化成功。")
        except (ValueError, TypeError):
            logger.critical(
                "`binance_master_key` 无效! 它必须是一个32字节且URL安全的base64编码字符串。"
            )
            logger.critical(
                "您可以使用以下代码生成一个: from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
            )
            # 在这种严重错误下，应该阻止插件继续运行
            raise ValueError("配置文件中的 binance_master_key 无效。")

    def load_keys(self):
        """从文件加载并解密API密钥"""
        if self.keys_file.exists():
            with open(self.keys_file, "r", encoding="utf-8") as f:
                try:
                    encrypted_data = json.load(f)
                    for user_id, encrypted_keys in encrypted_data.items():
                        try:
                            decrypted_api_key = self._cipher.decrypt(
                                encrypted_keys["api_key"].encode()
                            ).decode()
                            decrypted_secret_key = self._cipher.decrypt(
                                encrypted_keys["secret_key"].encode()
                            ).decode()
                            self._keys[user_id] = {
                                "api_key": decrypted_api_key,
                                "secret_key": decrypted_secret_key,
                            }
                        except InvalidToken:
                            logger.warning(
                                f"为用户 {user_id} 解密密钥失败。主密钥可能已更改。"
                            )
                except json.JSONDecodeError:
                    logger.error(f"无法解码 {self.keys_file}，文件可能已损坏。")
            logger.info(f"成功加载 {len(self._keys)} 个用户的API密钥。")

    def _save_keys_to_file(self):
        """加密并保存所有API密钥到文件"""
        encrypted_data = {}
        for user_id, keys in self._keys.items():
            encrypted_data[user_id] = {
                "api_key": self._cipher.encrypt(keys["api_key"].encode()).decode(),
                "secret_key": self._cipher.encrypt(
                    keys["secret_key"].encode()
                ).decode(),
            }
        with open(self.keys_file, "w", encoding="utf-8") as f:
            json.dump(encrypted_data, f, indent=4, ensure_ascii=False)

    def bind_keys(self, user_id: str, api_key: str, secret_key: str):
        """为用户绑定新的API密钥"""
        self._keys[user_id] = {"api_key": api_key, "secret_key": secret_key}
        self._save_keys_to_file()
        logger.info(f"成功为用户 {user_id} 绑定API密钥。")

    def unbind_keys(self, user_id: str) -> bool:
        """为用户解绑API密钥"""
        if user_id in self._keys:
            del self._keys[user_id]
            self._save_keys_to_file()
            logger.info(f"成功为用户 {user_id} 解绑API密钥。")
            return True
        return False

    def get_keys(self, user_id: str) -> Optional[Tuple[str, str]]:
        """获取用户的API密钥"""
        user_data = self._keys.get(user_id)
        if user_data:
            return user_data["api_key"], user_data["secret_key"]
        return None
