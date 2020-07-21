# tornado-RESTfulAPI

基于 tornado 6.X 的 RESTfulAPI 风格的异步项目模板，用于快速构建企业级高性能、高并发的服务端。

## 技术栈

- **框架选择**：基于 tornado 6.X
- **数据模型**：基于 PyMySQL 存储
- **授权验证**：基于 JWT
- **内置功能**：用户系统、异常处理、异步处理、动态权限、接口返回格式化、日志格式化、分页、模糊查询、过滤、排序、缓存、导出等

tornado 提供基础web框架
peewee 提供ORM支持
peewee-async 提供异步的数据库操作
marshmallow 提供数据验证和数据序列化支持  ps: 放弃使用wtforms对数据验证的支持
aioredis 提供异步redis操作
pyjwt 提供权限认证支持

## 快速入门

如需进一步了解，参见 [tornado 文档](https://www.tornadoweb.org/en/stable/index.html)。

### 本地开发

```bash
$ pip install -r requirements.txt # 安装依赖
$ python manage.py migrate # 迁移基本模型
$ python apps/users/tests.py # 创建默认数据
$ python manage.py ruserver 8080 # 运行服务
$ open http://localhost:8000/
```

### 线上部署

1、Linux服务器普通部署

```bash
# 获取帮助：bash sever.sh help 默认启动端口为 8080
bash server.sh start  # 默认启动调试服务，不开启多线程，使用config内dev_settings.py作为配置文件
bash server.sh start prod # 正式部署使用的命令，将根据CPU核数开启多线程，使用config内prod_settings.py作为配置文件
```

2、Docker部署，PS：由于Dockerfile中使用的基础镜像来源于作者自行制作的Python环境，因此需要的同学可以联系作者。

```bash
# 直接运行一下命令即可，会以debug模式运行服务，如果需要prod模式运行，请将Dockerfile中 CMD ["./docker_start.sh", "8080"] 改为 CMD ["./docker_start.sh", "8080", "prod"]
# 注意：docker_start.sh 脚本的第一个参数指定端口，第二个参数指定模式。
docker-compose up -d
```
