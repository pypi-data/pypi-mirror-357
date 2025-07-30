import json
import logging
import os
import platform
from pathlib import Path

import json5
import requests

logger = logging.getLogger(__name__)


class ProxySet:
    def __init__(self):
        pass

    @staticmethod
    def __get_code_settings_path() -> Path:
        system = platform.system()
        if system == "Windows":
            return Path(os.getenv("APPDATA")) / "Trae CN" / "User" / "settings.json"
        elif system == "Darwin":  # macOS
            return Path.home() / "Library" / "Application Support" / "Trae CN" / "User" / "settings.json"
        elif system == "Linux":
            return Path.home() / ".config" / "Trae CN" / "User" / "settings.json"
        else:
            raise OSError("Unsupported OS")

    @staticmethod
    def set_code_proxy(http_proxy: str):
        settings_path = ProxySet.__get_code_settings_path()

        # 确保文件存在
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        if not settings_path.exists():
            settings_path.write_text('{}')

        # 读取并更新配置
        with open(settings_path, "r", encoding="utf-8") as f:
            try:
                settings = json5.load(f)
            except Exception as e:
                logger.error(f"Failed to parse settings file {settings_path}: {e}")
                settings = {}

        logger.debug(f"原始配置 {settings}")

        if http_proxy and http_proxy.strip() and ProxySet.check_proxy(http_proxy):
            # 设置代理
            settings["http.proxy"] = http_proxy
            settings["http.proxyStrictSSL"] = False
            logger.info(f"设置代理为：{http_proxy}")
        else:
            # 清除代理相关设置
            for key in ["http.proxy", "http.proxyStrictSSL"]:
                settings.pop(key, None)
            logger.info("已清除 VS Code 代理配置")

        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
        logger.info(f"proxy 设置已写入到: {settings_path}")

    @staticmethod
    def check_proxy(http_proxy: str,
                    test_url: str = "https://mon.zijieapi.com/monitor_web/settings/browser-settings?bid=trae_cn&store=1",
                    timeout: int = 3) -> bool:
        """
        检查代理是否可用

        Args:
            http_proxy: 代理地址
            test_url: 用于测试的目标地址
            timeout: 请求超时时间（秒）

        Returns:
            True 如果代理可用，否则 False
        """
        proxies = {
            "http": http_proxy,
            "https": http_proxy,
        }
        try:
            resp = requests.get(test_url, proxies=proxies, timeout=timeout, verify=False)
            if resp.status_code == 200:
                logger.info(f"代理{http_proxy}可用，返回IP: {resp.text.strip()}")
                return True
        except Exception as e:
            logger.error(f"代理{http_proxy}不可用: {e}")
        return False
