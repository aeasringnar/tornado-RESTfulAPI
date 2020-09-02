from .decorators import auth_validated, authenticated_async, validated_input_type
from .caches import cache_data
from base.handler import BaseHandler
from base.response import RestResponseMsg
from base.pagination import Pagination
from .logger import logger
import json
from peewee import SQL

class MixinHandler(BaseHandler):
    query_set = None
    schema_class = None
    search_fields = ('username', 'gender')
    filter_fields = ('group_id', 'is_freeze')
    order_by_fields = ('create_time', 'update_time')
    pagination_class = Pagination
    search_query_param = 'search'
    order_query_param = 'order'
    


class ListHandler(MixinHandler):
    # @authenticated_async()
    # @auth_validated
    # @validated_input_type()
    # @cache_data()
    async def get(self, *args, **kwargs):
        self.get_init(*args, **kwargs)
        try:
            if self.pk:
                query = self.query_set.select().where(self.query_set.id==int(self.pk))
                auth = await self.application.objects.execute(query)
                if len(auth) > 0:
                    self.res.update(data = json.loads(self.schema_class().dumps(auth[0])))
            else:
                MY_SQL = ' and '.join('(%s)' % item for item in (self.search_sql, self.filter_sql) if item)
                MY_ORDER_SQL = []
                for item in self.order_keys:
                    print(item)
                    if item[0] == '-':
                        print(11111)
                        MY_ORDER_SQL.append(-getattr(self.query_set, item[1:]))
                    else:
                        MY_ORDER_SQL.append(getattr(self.query_set, item))
                if not MY_ORDER_SQL:
                    MY_ORDER_SQL = [self.query_set.id]
                print('+' * 128)
                print(MY_ORDER_SQL)
                if MY_SQL:
                    query = self.query_set.select().where(SQL(MY_SQL)).order_by(-self.query_set.id).paginate(page=self.page, paginate_by=self.page_size)
                else:
                    query = self.query_set.select().order_by(*MY_ORDER_SQL).paginate(page=self.page, paginate_by=self.page_size)
                objs = await self.application.objects.execute(query)
                total = await self.application.objects.count(self.query_set.select())
                self.res.update(total = total, data = json.loads(self.schema_class(many=True).dumps(objs)))
            self.finish(self.res.data)
            return self.res.data
        except Exception as e:
            logger.error('出现异常：%s' % str(e))
            self.res.update(message = "出现无法预料的异常：{}".format(str(e)), errorCode = 1)
            self.finish(self.res.data)
            return self.res.data
    
    def get_init(self, *args, **kwargs):
        self.res = RestResponseMsg()
        self.request_data = self.request.body.decode('utf-8') if self.request.body else "{}"
        self.page = eval(self.get_query_argument(self.pagination_class().page_query_param, '1'))
        self.page_size = eval(self.get_query_argument(self.pagination_class().page_size_query_param, str(self.pagination_class().page_size)))
        self.search_str = self.get_query_argument(self.search_query_param, '')
        self.order_str = self.get_query_argument(self.order_query_param, '')
        self.new_set = set(self.filter_fields)
        self.filter_keys = self.new_set.intersection(set(self.request.query_arguments.keys()))
        self.pk = kwargs.get('pk')
        self.order_ls = self.order_str.split(',')
        self.order_by_fields = tuple(['-%s' % item for item in self.order_by_fields] + list(self.order_by_fields))
        self.order_keys = list(set(self.order_ls).intersection(set(self.order_by_fields)))
        self.order_keys.sort(key = self.order_ls.index) # 保证多字段排序的顺序
        # 模糊搜索的SQL
        self.search_sql = ' or '.join(["{} like '%%{}%%'".format(item, self.search_str) for item in self.search_fields if self.search_str])
        # 过滤的SQL
        self.filter_sql = ' and '.join(["{} = '{}'".format(item, self.get_query_argument(item)) for item in self.filter_keys])
        # 排序的SQL
        self.order_sql = ' order by ' + ','.join(self.order_keys) if self.order_keys else ''
        print('+' * 128)
        print(self.search_sql)
        print(self.filter_sql)
        print(self.order_sql)
        print(' and '.join('(%s)' % item for item in (self.search_sql, self.filter_sql) if item) + self.order_sql)
        

class RetrieveHandler(object):
    extend_path = True


class CreateHandler(object):
    def post(self, *args, **kwargs):
        @authenticated_async()
        @auth_validated
        @validated_input_type()
        async def post(self, *args, **kwargs):
            res_format = {"message": "ok", "errorCode": 0, "data": {}}
            try:
                # print()
                data = self.request.body.decode('utf-8') if self.request.body else "{}"
                # print(data)
                # un_validata = NewUserSerializer.from_json(json.loads(data))
                pk = kwargs.get('pk')
                if pk:
                    res_format['message'] = '不支持的方法，请检查路由是否正确。'
                    res_format['errorCode'] = 2
                    return self.finish(res_format)
                validataed = AddUserSchema().load(json.loads(data))
                # print(validataed, type(validataed))
                username = validataed.get('username')
                query = User.select().where(User.username==username)
                checks = await self.application.objects.execute(query)
                if checks:
                    res_format['message'] = '该用户名已存在'
                    res_format['errorCode'] = 2
                    return self.finish(res_format)
                await self.application.objects.create(User, **validataed)
                return self.finish(res_format)
            except ValidationError as err:
                return self.finish({"message": str(err.messages), "errorCode": 2, "data": {}})
            except Exception as e:
                logger.error('出现异常：%s' % str(e))
                return self.finish({"message": "出现无法预料的异常：{}".format(str(e)), "errorCode": 1, "data": {}})


class DeleteHandler(object):
    extend_path = True
    def delete(self, *args, **kwargs):
        print('发起删除操作')


class PatchHandler(object):
    def patch(self, *args, **kwargs):
        print('发起局部修改操作')


class PutHandler(object):
    def put(self, *args, **kwargs):
        print('发起修改操作')