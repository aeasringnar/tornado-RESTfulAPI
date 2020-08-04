import datetime
from utils.logger import logger


def test_job():
    try:
        print('当前时间：', datetime.datetime.now())
    except Exception as e:
        logger.error('发生异常：%s' % str(e))