import time
import threading
import redis
import os, sys
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,base_path)
from base.settings import REDIS


class RedisLock(object):
    def __init__(self, cache_type):
        self.redis_con = self.get_redis_con()
        sele.cache_type = cache_type

    def get_redis_con(self):
        pool = redis.ConnectionPool(host='127.0.0.1',port=6379)
        redis_con = redis.Redis(connection_pool=pool)
        return redis_con

    def get_lock(self, val):
        while True:
            res = self.redis_con.set('cache_read_write_lock_key', val,nx=True, ex=5)
            if res:
                break
            time.sleep(0.1)

    def del_lock(self, val):
        old_val = self.redis_con.get('cache_read_write_lock_key')
        if old_val == val.encode():
            self.redis_con.delete('cache_read_write_lock_key')
            print('锁释放成功')


SUMS = 0

def test_lock(lock, name, num, val):
    try:
        print('%s 开始工作' % name)
        print('%s 准备获取锁并加锁' % name)
        lock.get_lock(val)
        print('%s 得到锁，继续工作' % name)
        global SUMS
        SUMS += 15
        time.sleep(num)
        print(SUMS)
    except Exception as e:
        print('发生异常：%s' % str(e))
    finally:
        print('%s 操作完成，准备释放锁'%name)
        lock.del_lock(val)


if __name__ == '__main__':
    start_time = time.time()
    r_lock = RedisLock()
    tasks = []
    for num in range(1,4):
        t = threading.Thread(target=test_lock, args=(r_lock, '任务%d'%num,num,'lock%d'%num))
        tasks.append(t)
        t.start()
    [item.join() for item in tasks]
    print('总耗时：', time.time() - start_time)