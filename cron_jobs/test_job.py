import datetime
from utils.logger import logger


def test_job():
    try:
        logger.info('当前时间：%s' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        logger.error('发生异常：%s' % str(e))