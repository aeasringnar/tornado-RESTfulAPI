from .decorators import authvalidated_async, allowall_async, authenticated_async, validated_input_type
from .caches import cache_data
from base.handler import BaseHandler
from base.response import RestResponseMsg
from base.pagination import Pagination
from .logger import logger
import json
from peewee import SQL
from marshmallow import ValidationError

class MixinHandler(BaseHandler):
    query_model = None
    schema_class = None
    search_fields = ('username', 'gender')
    filter_fields = ('group_id', 'is_freeze')
    order_by_fields = ('create_time', 'update_time')
    pagination_class = Pagination
    search_query_param = 'search'
    order_query_param = 'order'

    def get_query_model(self):
        return self.query_model

    @property
    def get_schema_class(self):
        return self.schema_class



class ListHandler(MixinHandler):
    # @authenticated_async()
    # @authvalidated_async()
    # @validated_input_type()
    # @cache_data()
    async def get(self, *args, **kwargs):
        self.get_init(*args, **kwargs)
        try:
            if self.pk:
                query = self.get_query_model().select().where(self.get_query_model().id==int(self.pk))
                auth = await self.application.objects.execute(query)
                if len(auth) > 0:
                    self.res.update(data = json.loads(self.get_schema_class().dumps(auth[0])))
            else:
                MY_SQL = ' and '.join('(%s)' % item for item in (self.search_sql, self.filter_sql) if item)
                MY_ORDER_SQL = []
                for item in self.order_keys:
                    if item[0] == '-':
                        MY_ORDER_SQL.append(-getattr(self.get_query_model(), item[1:]))
                    else:
                        MY_ORDER_SQL.append(getattr(self.get_query_model(), item))
                if not MY_ORDER_SQL:
                    MY_ORDER_SQL = [self.get_query_model().id]
                if MY_SQL:
                    query = self.get_query_model().select().where(SQL(MY_SQL)).order_by(-self.get_query_model().id).paginate(page=self.page, paginate_by=self.page_size)
                else:
                    query = self.get_query_model().select().order_by(*MY_ORDER_SQL).paginate(page=self.page, paginate_by=self.page_size)
                objs = await self.application.objects.execute(query)
                total = await self.application.objects.count(self.get_query_model().select())
                self.res.update(total = total, data = json.loads(self.get_schema_class(many=True).dumps(objs)))
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
        # print('+' * 128)
        # print(self.search_sql)
        # print(self.filter_sql)
        # print(' and '.join('(%s)' % item for item in (self.search_sql, self.filter_sql) if item))
        

class RetrieveHandler(object):
    extend_path = True


class CreateHandler(MixinHandler):
    # @authenticated_async()
    # @authvalidated_async()
    # @validated_input_type()
    async def post(self, *args, **kwargs):
        res_format = {"message": "ok", "errorCode": 0, "data": {}}
        self.res = RestResponseMsg()
        self.request_data = self.request.body.decode('utf-8') if self.request.body else "{}"
        try:
            pk = kwargs.get('pk')
            if pk:
                self.res.update(message = '不支持的方法，请检查路由是否正确。', errorCode = 2)
                self.finish(self.res.data)
                return self.res.data
            validataed = self.get_schema_class().load(json.loads(self.request_data))
            await self.application.objects.create(self.get_query_model(), **validataed)
            return self.finish(res_format)
        except ValidationError as err:
            self.res.update(message = str(err.messages), errorCode = 2)
            self.finish(self.res.data)
            return self.res.data
        except Exception as e:
            logger.error('出现异常：%s' % str(e))
            self.res.update(message = "出现无法预料的异常：{}".format(str(e)), errorCode = 1)
            self.finish(self.res.data)
            return self.res.data


class DeleteHandler(MixinHandler):
    extend_path = True
    # @authenticated_async()
    # @authvalidated_async()
    # @validated_input_type()
    async def delete(self, *args, **kwargs):
        self.res = RestResponseMsg()
        try:
            pk = kwargs.get('pk')
            if not pk:
                self.res.update(message = '路由异常，请携带id。', errorCode = 2)
                self.finish(self.res.data)
                return self.res.data
            query = self.get_query_model().select(self.get_query_model().id).where(self.get_query_model().id == int(pk))
            check_obj = await self.application.objects.execute(query)
            if not check_obj:
                self.res.update(message = '资源不存在。', errorCode = 2)
                self.finish(self.res.data)
                return self.res.data
            await self.application.objects.delete(check_obj[0])
            self.finish(self.res.data)
            return self.res.data
        except Exception as e:
            logger.error('出现异常：%s' % str(e))
            self.res.update(message = "出现无法预料的异常：{}".format(str(e)), errorCode = 1)
            self.finish(self.res.data)
            return self.res.data


class PatchHandler(MixinHandler):
    # @authenticated_async()
    # @authvalidated_async()
    # @validated_input_type()
    async def patch(self, *args, **kwargs):
        self.res = RestResponseMsg()
        self.request_data = self.request.body.decode('utf-8') if self.request.body else "{}"
        try:
            pk = kwargs.get('pk')
            if not pk:
                self.res.update(message = '路由异常，请携带id。', errorCode = 2)
                self.finish(self.res.data)
                return self.res.data
            # print(validataed, type(validataed))
            query = self.get_query_model().select(self.get_query_model().id).where(self.get_query_model().id == int(pk))
            check_obj = await self.application.objects.execute(query)
            if not check_obj:
                self.res.update(message = '资源不存在。', errorCode = 2)
                self.finish(self.res.data)
                return self.res.data
            if not json.loads(self.request_data):
                self.finish(self.res.data)
                return self.res.data
            validataed = self.get_schema_class().load(json.loads(self.request_data))
            [setattr(check_obj[0], key, val) for key,val in validataed.items()]
            await self.application.objects.update(check_obj[0])
            self.finish(self.res.data)
            return self.res.data
        except ValidationError as err:
            self.res.update(message = str(err.messages), errorCode = 2)
            self.finish(self.res.data)
            return self.res.data
        except Exception as e:
            logger.error('出现异常：%s' % str(e))
            self.res.update(message = "出现无法预料的异常：{}".format(str(e)), errorCode = 1)
            self.finish(self.res.data)
            return self.res.data


class PutHandler(object):
    def put(self, *args, **kwargs):
        print('发起修改操作')