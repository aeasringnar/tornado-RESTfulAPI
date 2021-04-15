import datetime
import logging


def test_job():
    try:
        logging.info('当前时间：%s' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        logging.error('发生异常：%s' % str(e))