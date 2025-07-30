import logging
import platform
import subprocess
import sys
from pathlib import Path

import ctypes
from cryptography.hazmat.primitives import hashes

logger = logging.getLogger(__name__)


class CertInstaller:
    def __init__(self, cert_file: str):
        """
        初始化对象
        :param cert_file: 证书文件
        """
        self.cert_path = Path(Path(__file__).parent.resolve() / cert_file)
        if not self.cert_path.exists():
            logger.info(f"证书文件不存在: {self.cert_path}")
            sys.exit(1)
        self.fingerprint = self.get_cert_fingerprint()

    @staticmethod
    def is_admin_windows() -> bool:
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception as e:
            logger.error(e)
            return False

    def run_as_admin_windows_and(self):
        script = sys.argv[0]
        args = " ".join([f'"{arg}"' for arg in sys.argv[1:] if arg != "--elevated"])
        cmd = f'"{script}" --elevated {args}'
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, cmd, None, 1)
        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",  # 以管理员权限运行
            "certutil.exe",  # 要执行的程序
            f'-addstore -f Root "{self.cert_path}"',  # 参数字符串
            None,  # 默认目录
            1  # 正常显示窗口
        )

    def get_cert_fingerprint(self) -> str:
        """
        计算证书的SHA1指纹，便于比对是否已安装
        :return: 证书指纹
        """
        from cryptography import x509
        from cryptography.hazmat.backends import default_backend
        cert_data = self.cert_path.read_bytes()
        cert = x509.load_pem_x509_certificate(cert_data, default_backend())
        fingerprint_bytes = cert.fingerprint(hashes.SHA1())
        return fingerprint_bytes.hex().upper()

    def is_cert_installed_windows(self) -> bool:
        """
        Windows判断证书是否安装
        :return: 是否已安装
        """
        try:
            output = subprocess.check_output(
                ['certutil', '-store', 'Root'], text=True, stderr=subprocess.DEVNULL)
            # certutil 输出里会有指纹信息（类似Fingerprint=xx:xx:xx）
            return self.fingerprint in output.replace(":", "").upper()
        except Exception as e:
            logger.error(e)
            return False

    def install_cert_windows(self):
        logger.info("在 Windows 中安装证书...")
        if CertInstaller.is_admin_windows():
            subprocess.run(
                ['certutil', '-addstore', '-f', 'Root', str(self.cert_path)],
                shell=True, check=True)
        else:
            logger.info("当前无管理员权限，请求 UAC 提升...")
            self.run_as_admin_windows_and()
        logger.info("证书已安装到 Windows 根证书库。")

    def is_cert_installed_macos(self) -> bool:
        """macOS 判断是否安装，略简单，只检测证书名"""
        try:
            output = subprocess.check_output(
                ['security', 'find-certificate', '-a', '-p', '/Library/Keychains/System.keychain'],
                text=True, stderr=subprocess.DEVNULL)
            return self.fingerprint in output.replace(":", "").upper()
        except Exception as e:
            logger.error(e)
            return False

    def install_cert_macos(self):
        logger.info("在 macOS 中安装证书（需要管理员权限）...")
        subprocess.run([
            'sudo', 'security', 'add-trusted-cert', '-d', '-r', 'trustRoot',
            '-k', '/Library/Keychains/System.keychain',
            str(self.cert_path)
        ], check=True)
        logger.info("证书已安装到 macOS 系统钥匙串。")

    def is_cert_installed_linux(self) -> bool:
        """Linux 判断是否已安装（Debian/Ubuntu）"""
        try:
            output = subprocess.check_output(
                ['sha1sum', '/usr/local/share/ca-certificates/mitmproxy-ca.crt'],
                text=True, stderr=subprocess.DEVNULL)
            return self.fingerprint.lower() in output.lower()
        except Exception as e:
            logger.error(e)
            return False

    def install_cert_linux(self):
        logger.info("在 Linux 中安装证书（需要管理员权限）...")
        dst = '/usr/local/share/ca-certificates/mitmproxy-ca.crt'
        subprocess.run(['sudo', 'cp', str(self.cert_path), dst], check=True)
        subprocess.run(['sudo', 'update-ca-certificates'], check=True)
        logger.info("证书已安装并更新。")

    def is_cert_installed(self) -> bool:
        """
        检测证书是否安装
        :return: 是否已安装
        """
        system = platform.system()
        check_install_map = {
            "Windows": self.is_cert_installed_windows,
            "Darwin": self.is_cert_installed_macos,
            "Linux": self.is_cert_installed_linux
        }
        check_install_func = check_install_map.get(system)
        if check_install_func:
            return check_install_func()
        else:
            return False

    def install_cert(self) -> bool:
        """
        根据操作系统自动安装证书，已安装则跳过。
        Returns:
            bool: 安装是否成功或已安装
        """
        if self.is_cert_installed():
            logger.info("证书已安装，跳过安装。")
            return True

        system = platform.system()
        install_map = {
            "Windows": self.install_cert_windows,
            "Darwin": self.install_cert_macos,
            "Linux": self.install_cert_linux
        }

        install_func = install_map.get(system)
        if install_func:
            install_func()
            return self.is_cert_installed()
        else:
            logger.warning(f"不支持当前操作系统：{system}，请手动安装证书。")
            return False

    @staticmethod
    def install() -> bool:
        """
        安装证书
        :return: 是否成功安装
        """
        return CertInstaller("cert/mitmproxy-ca-cert.pem").install_cert()
