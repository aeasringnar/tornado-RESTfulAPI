from tornado.web import url
from tornado.web import StaticFileHandler
from base.settings import settings
from apps.users import urls as user_urls
from apps.public import urls as public_urls
from .handler import OtherErrorHandler

urlpatterns = [
    (url("/media/(.*)", StaticFileHandler, {"path": settings["media_path"]}))
]

urlpatterns += user_urls.urlpatterns
urlpatterns += public_urls.urlpatterns
urlpatterns.append(url(".*", OtherErrorHandler))