#日志配置文件
import logging
import sys

#定义一个日志配置函数，level：日志级别，默认是 INFO（普通信息）
def setup_logging(level: int = logging.INFO) -> None:
    """
    配置全局日志。
    只初始化一次，避免重复添加 handler。
    """
    #获取根日志器（rootlogger）。所有日志默认都会从这里输出，配置它 = 配置全局日志
    root_logger = logging.getLogger()
    #防止重复添加日志处理器
    #如果已有根日志器已经有 handler，就只更新日志级别，然后直接返回
    if root_logger.handlers:
        root_logger.setLevel(level)
        return
    #设置格式（时间-日志级别-日志器名称-日志内容）eg：2025-12-29 15:30:00 | INFO | root | 服务启动成功
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    #创建控制台输出处理器，日志输出到控制台
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    #设置全局日志级别
    root_logger.setLevel(level)
    #把控制台处理器添加到根日志器
    root_logger.addHandler(console_handler)