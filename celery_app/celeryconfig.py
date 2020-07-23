from celery.schedules import crontab
from datetime import timedelta
from kombu import Queue
from kombu import Exchange

# 设置任务接受的类型，默认是{'json'}
accept_content = ['json']

# 请任务接受后存储时的类型
result_accept_content = ['json']

# 时间格式化为中国的标准
timezone = "Asia/Shanghai"

# 结果序列化为json格式 默认值json从4.0开始（之前为pickle）。
result_serializer = 'json'

# 指定borker为redis 如果指定rabbitmq broker_url = 'amqp://guest:guest@localhost:5672//'
broker_url = "redis://127.0.0.1/0"

# 指定存储结果的地方，支持使用rpc、数据库、redis等等，具体可参考文档 # result_backend = 'db+mysql://scott:tiger@localhost/foo' # mysql 作为后端数据库
result_backend = "redis://127.0.0.1/1"

# 设置任务过期时间 默认是一天，为None或0 表示永不过期
result_expires = 60 * 60 * 24

# 设置worker并发数，默认是cpu核心数
worker_concurrency = 12

# 设置每个worker最大任务数
worker_max_tasks_per_child = 100

# 指定任务队列，使不同的任务在不同的队列中被执行 如果配置，在启动celery时需要增加 -Q add 多个示例 -Q add,mul
# 示例：celery -A celery_app worker -Q add -l info -P eventlet(在Windows下启动worker，它将只消费add队列中的消息，也就是只执行add任务)
# 示例：celery -A celery_app worker -Q add,mul -l info(在Linux下启动worker，它将只消费add和mul队列中的消息，也就是只执行add和mul任务)
task_routes = {
    'celery_app.tasks.add': {'queue': 'add'},
    'celery_app.tasks.mul': {'queue': 'mul'},
    'celery_app.tasks.xsum': {'queue': 'xsum'},
    }
# 指定任务的位置
imports = (
    'celery_app.tasks',
    'apps.users.tasks',
)
# 后台运行worker示例：