from .decorators import auth_validated, authenticated_async, validated_input_type
from .caches import cache_data
from base.handler import BaseHandler
from .logger import logger
import json

class MixinHandler(BaseHandler):
    query_set = None
    schema_class = None
    search_fields = ('name', 'age')
    filter_fields = ('group', 'status')
    order_by_fields = ('create_time', 'update_time')


class ListHandler(MixinHandler):
    # @authenticated_async()
    # @auth_validated
    # @validated_input_type()
    # @cache_data()
    async def get(self, *args, **kwargs):
        res_format = {"message": "ok", "errorCode": 0, "data": {}}
        search_ls = ['auth_type']
        filter_ls = ['auth_type']
        try:
            data = self.request.body.decode('utf-8') if self.request.body else "{}"
            page = eval(self.get_query_argument(self.settings['default_page_param'], '1'))
            page_size = eval(self.get_query_argument('page_size', self.settings['default_page_size']))
            search_str = self.get_query_argument('search', '')
            pk = kwargs.get('pk')
            if pk:
                query = self.query_set.select().where(self.query_set.id==int(pk))
                auth = await self.application.objects.execute(query)
                if len(auth) > 0:
                    res_format['data'] = json.loads(self.schema_class().dumps(auth[0]))
            else:
                query = self.query_set.select().order_by(-self.query_set.id).paginate(page=page, paginate_by=page_size)
                objs = await self.application.objects.execute(query)
                total = await self.application.objects.count(self.query_set.select())
                res_format['total'] = total
                res_format['data'] = json.loads(self.schema_class(many=True).dumps(objs))
            self.finish(res_format)
            return res_format
        except Exception as e:
            logger.error('出现异常：%s' % str(e))
            return self.finish({"message": "出现无法预料的异常：{}".format(str(e)), "errorCode": 1, "data": {}})


class RetrieveHandler(object):
    extend_path = True


class CreateHandler(object):
    def post(self, *args, **kwargs):
        print('发起创建操作')


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