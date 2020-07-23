from tornado.web import url
from .handler import UploadFileHandler, GetMobielCodeHandler, TestHandler, RunTaskHandler, GetTaskResultHandler

urlpatterns = [
    url('/public/test/', TestHandler),
    url('/public/uploadfile/', UploadFileHandler),
    url('/public/getcode/', GetMobielCodeHandler),
    url('/public/runtask/', RunTaskHandler),
    url('/public/getresult/', GetTaskResultHandler),
]
