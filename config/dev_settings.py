import peewee_async
import peewee
import aioredis
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


settings = {
    "debug": True,
    "media_path": os.path.join(BASE_DIR, "media"),
    "static_path": os.path.join(BASE_DIR, 'static'),
    "secret_key": "d#aPr8%mssTZgVGy",
    "jwt_expire": 7*24*3600,
    "site_url": "http://127.0.0.1:8080",
    'default_page_size': '10',
    'default_page_param': 'page',
    'redis': {
        'default': {
            'LOCATION': 'redis://127.0.0.1/0'
        }
    }
}


DATABASES = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "123456",
    "database": "tornado_api",
    "port": 3306
}


sync_db = peewee.MySQLDatabase(**DATABASES)
async_db = peewee_async.MySQLDatabase(**DATABASES)


# 文件上传配置
FILE_CHECK = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'zip', 'rar', 'xls', 'xlsx', 'doc', 'docx', 'pptx', 'ppt', 'txt', 'pdf', 'py']
FILE_SIZE = 1024 * 1024 * 64
SERVER_NAME = settings['site_url']


# 微信开发配置
WECHAT_MCHID = '微信支付平台商户号'
WECHAT_KEY = '微信支付平台秘钥'
WECHAT_PAY_NOTIFY_URL = '微信支付异步通知url'
WECHAT_MINI_APPID = '微信小程序appid'  
WECHAT_MINI_SECRET = '微信小程序secret'
WECHAT_APP_APPID = '微信开放平台APP_appid'
WECHAT_APP_SECRET = '微信开放平台APP_secret'
# 微信企业付款相关证书
# CERT_PATH = os.path.join(BASE_DIR, 'utils/cert/apiclient_cert.pem')
# CERT_KEY_PATH = os.path.join(BASE_DIR, 'utils/cert/apiclient_key.pem')


# 支付宝支付
ALIPAY_APPID = '支付宝appid'
# 支付宝商户私钥
PRIVATE_KEY_PATH = os.path.join(BASE_DIR, 'utils/ali_keys/rsa_private_key.pem')
# 支付宝支付公钥
ALIPUB_KEY_PATH = os.path.join(BASE_DIR, 'utils/ali_keys/ali_public_key.text')
ALIPAY_NOTIFY_URL = '支付宝支付异步通知url'


# 阿里短信设置
ALI_KEY = "your key"
ALI_SECRET = 'your secret'
ALI_REGION = 'your region'
ALI_SIGNNAME = 'your signame'
# 登录使用的信息模板
ALI_LOGOIN_CODE = 'your msg tempalte id'


# 极光推送配置
JPUSH_APPKEY = 'your key'
JPUSH_SECRET = 'your secret'


# redis 配置
REDIS = {
    'default': {
        'LOCATION': 'redis://127.0.0.1/0'
    }
}
async def redis_pool(loop):
    return await aioredis.create_redis_pool('redis://localhost', minsize=1, maxsize=10000, encoding='utf8', loop=loop)