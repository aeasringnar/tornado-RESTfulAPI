from tornado.web import url
from apps.users.handler import MobileLoginHandler, AdminLoginHandler, UserInfoHandler, AuthHandler, AdminUserHandler, EchoWebSocket

urlpatterns = [
    # url('/code/', CodeHandler),
    url('/mobilelogin/', MobileLoginHandler),
    url('/adminlogin/', AdminLoginHandler),
    url('/userinfo/', UserInfoHandler),
    url('/adminauth/?(?P<pk>\d*)', AuthHandler),
    url('/adminuser/?(?P<pk>\d*)', AdminUserHandler),
    url('/echo', EchoWebSocket),
]

#################### test sample crud
from utils.router import MyRouter
from apps.users.handler import CRUDhandleTest

router = MyRouter()
router.register('/users/testcrud', CRUDhandleTest)


urlpatterns += router.urlpath