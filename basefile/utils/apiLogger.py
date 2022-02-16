# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# handler 输出到控制台
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# 创建 logging format
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)

logger.addHandler(ch)


if __name__ == '__main__':
    try:
        open("/home/lynnlidan/hello.log", 'rb')
    except (SystemExit, KeyboardInterrupt):
        raise

    except Exception as e:
        logger.error("failed to open file, ", exc_info=True)