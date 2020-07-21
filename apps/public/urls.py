from tornado.web import url
from .handler import UploadFileHandler, GetMobielCodeHandler, TestHandler

urlpatterns = [
    url('/public/test/', TestHandler),
    url('/public/uploadfile/', UploadFileHandler),
    url('/public/getcode/', GetMobielCodeHandler),
]
