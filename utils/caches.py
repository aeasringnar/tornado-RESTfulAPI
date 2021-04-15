from functools import wraps
from .cache_lock import CacheRedisLock
from base.settings import settings
import logging
import asyncio
import json

def cache_data(need_auth = False, cache_time = 60*5):
    '''
    第一版缓存装饰器
    '''
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            try:
                print('+' * 128)
                # print(dir(self.request))
                # print(self.request.method)
                uri_split = '_'.join([item for item in self.request.uri.split('/') if item != ''])
                cache_key = '+'.join([settings['secret_key'], self.request.method, uri_split])
                # cache_lock_key = '+'.join([settings['secret_key'], uri_split, 'lock'])
                # print(cache_lock_key)
                # lock = CacheRedisLock('new_cache_key', 'read')
                print(cache_key)
                data = await self.application.redis.get(cache_key, encoding='utf-8')
                if data:
                    logging.debug('命中缓存')
                    self.finish(json.loads(data))
                else:
                    logging.debug('缓存不存在')
                    res = await func(self, *args, **kwargs)
                    await self.application.redis.set(cache_key, json.dumps(res), expire = cache_time)
                # print(res)
                # print(type(res))
            except Exception as e:
                self.set_status(200)
                logging.error('出现异常：{}'.format(str(e)))
                res = await func(self, *args, **kwargs)
                return res
        return wrapper
    return decorator