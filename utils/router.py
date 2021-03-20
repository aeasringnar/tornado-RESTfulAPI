import os
import time
from tornado.web import url


class MyRouter(object):
    urls = []
    def register(self, path, handle):
        if hasattr(handle, 'extend_path'):
            self.urls.append(url(path + '/?(?P<pk>\d*)', handle))
        else:
            self.urls.append(url(path + '/', handle))

    @property
    def urlpath(self):
        return self.urls


if __name__ == '__main__':
    router = MyRouter()
    router.register('test', PostDelHandler)
    router.register('app/user', UserHandler)
    print(router.urlpath)