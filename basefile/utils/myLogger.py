import logging.config
import os


# 读取日志配置文件
logging.config.fileConfig(os.path.join(os.path.dirname(__file__), '../config/log.conf'))
# 创建记录器
tracebackLog = logging.getLogger('traceback_logger')
infoLog      = logging.getLogger('info_logger')
