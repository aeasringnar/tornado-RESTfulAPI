import os
import logging
from base.settings import settings
log_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs'), 'web.log')

# 创建 logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
# logger.propagate = 0

formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s - %(message)s')

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
consoleHandler.setLevel(logging.DEBUG)
# 创建一个输出到文件的 handler
fileHandler = logging.FileHandler(log_path, mode='w', encoding='utf-8')
fileHandler.setFormatter(formatter)
fileHandler.setLevel(logging.INFO)
if settings['debug']:
    fileHandler.setLevel(logging.DEBUG)
else:
    fileHandler.setLevel(logging.INFO)

if settings['debug']:
    logger.addHandler(consoleHandler) 
logger.addHandler(fileHandler)