from tornado.web import RequestHandler
import redis
import time

class BaseHandler(RequestHandler):

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.redis_conn = redis.StrictRedis()
        print('************************************************* 下面是新的一条日志 ***************************************************')
        print('[%s]' % (time.strftime("%Y-%m-%d %H:%M:%S")),request.version,request.remote_ip,request.method,request.uri)
        print('请求IP：', request.remote_ip)
        if request.query:
            print('params参数：', request.query)
        if  self.request.headers.get("Content-Type") and self.request.headers.get("Content-Type").split(';')[0] == 'application/json':
            print('body参数：', request.body.decode())
        # print(dir(request))

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Content-type', 'application/json')
        self.set_header('Access-Control-Allow-Credentials', "true")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, DELETE, PUT, PATCH, OPTIONS')
        self.set_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, Access-Control-Allow-Origin, Access-Control-Allow-Headers, X-Requested-By, Access-Control-Allow-Methods')