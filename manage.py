import tornado
from tornado import ioloop
from tornado.httpserver import HTTPServer, TCPServer
import os, sys
from tornado import web
from peewee_async import Manager
from base.urls import urlpatterns
from base.settings import settings, async_db, redis_pool
from utils.db_manage import run_create, run_update
from utils.logger import logger
import signal
from multiprocessing import cpu_count
import asyncio
 
def signal_handler(signal,frame):
    # print('\n bye bye')
    sys.exit()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))


if __name__ == '__main__':
    signal.signal(signal.SIGINT,signal_handler)
    try:
        if len(sys.argv) < 2:
            print("""缺少选项！
支持的选项：
runserver 运行服务，需要指定地址(选填)&端口。示例：runserver 8080、runserver 0.0.0.0:8080
migrate 生成表(迁移表)
update 修改表迁移""")
        elif sys.argv[1] == 'create':
            run_create()
        elif sys.argv[1] == 'update':
            run_update()
        elif sys.argv[1] == 'runserver':
            if len(sys.argv) != 3:
                raise ValueError('runserver选项参数错误！')
            if ':' in sys.argv[2]:
                host, port = sys.argv[2].split(':')
            else:
                port = sys.argv[2]
                host = '127.0.0.1'
            app = web.Application(
                urlpatterns,
                **settings
            )
            async_db.set_allow_sync(False)
            app.objects = Manager(async_db)
            loop = asyncio.get_event_loop()
            # app.redis = RedisPool(loop=loop).get_conn()
            app.redis = loop.run_until_complete(redis_pool(loop))
            logger.info("""[%s]Wellcome...
Starting development server at http://%s:%s/       
Quit the server with CTRL+C.""" % (('debug' if settings['debug'] else 'line'), host, port))
            server = HTTPServer(app)
            server.listen(int(port),host)
            if not settings['debug']:
                # 多进程 运行
                server.start(cpu_count() - 1)
            ioloop.IOLoop.current().start()
        else:
            print("""参数异常！
支持的选项：
runserver 运行服务，需要指定地址(选填)&端口。示例：runserver 8080、runserver 0.0.0.0:8080
migrate 生成表(迁移表)
update 修改表迁移""")
    except Exception as e:
        logger.error('发生异常：%s' % str(e))
        
