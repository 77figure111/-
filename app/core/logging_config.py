#日志配置文件
import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    """
    配置全局日志。
    只初始化一次，避免重复添加 handler。
    """
    root_logger = logging.getLogger()

    if root_logger.handlers:
        root_logger.setLevel(level)
        return

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)