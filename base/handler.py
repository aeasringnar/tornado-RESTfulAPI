from tornado.web import RequestHandler
from utils.logger import logger
import redis
import time
import traceback

class BaseHandler(RequestHandler):

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.redis_conn = redis.StrictRedis()
        logger.info('************************************************* 下面是新的一条日志 ***************************************************')
        logger.info(' '.join([request.version, request.remote_ip, request.method, request.uri]))
        logger.info('请求IP：' + request.remote_ip)
        if request.query:
            logger.debug('params参数：' + request.query)
        if  self.request.headers.get("Content-Type") and self.request.headers.get("Content-Type").split(';')[0] == 'application/json':
            logger.debug('body参数：' + request.body.decode())
            
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Content-type', 'application/json')
        self.set_header('Access-Control-Allow-Credentials', "true")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, DELETE, PUT, PATCH, OPTIONS')
        self.set_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, Access-Control-Allow-Origin, Access-Control-Allow-Headers, X-Requested-By, Access-Control-Allow-Methods')

    def write_error(self, status_code, **kwargs):
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            for line in traceback.format_exception(*kwargs["exc_info"]):
                self.write(line)
            self.finish({"message":  self._reason, "errorCode": 2, "data": {}})
        else:
            self.finish({"message":  self._reason, "errorCode": 2, "data": {}})


class OtherErrorHandler(RequestHandler):

    async def get(self, *args, **kwargs):
        self.set_status(404)
        return self.finish({"message": "路径或资源不存在", "errorCode": 2, "data": {}})
            
    def write_error(self, status_code, **kwargs):
        self.set_header("Content-Type", "application/json")
        self.finish({"message":  self._reason, "errorCode": 2, "data": {}})