import base64, json, re, jwt, datetime, time
from calendar import timegm
# 导入使用缓存的模块
import hashlib
import random
import datetime
import time
import math
import requests
# 导入谷歌验证码相关模块
import pyotp
from base.settings import WECHAT_MINI_APPID, WECHAT_MINI_SECRET, WECHAT_APP_APPID, WECHAT_APP_SECRET


def wechat_mini_login(code):
    '''
    微信小程序登录的方法
    :param code: 微信小程序调用登录的code
    :return : (openid, unionid, session_key)
    '''
    appid = WECHAT_MINI_APPID
    secret = WECHAT_MINI_SECRET
    get_user_url = 'https://api.weixin.qq.com/sns/jscode2session?appid={}&secret={}&js_code={}&grant_type=authorization_code'.format(appid, secret, code)
    response = requests.get(url=get_user_url)
    print('msg：',eval(response.text), type(eval(response.text)))
    response_dic = eval(response.text)
    if response_dic.get('errcode') and response_dic.get('errcode') != 0:
        return {"message": "微信端推送错误：%s,errcode=%s" % (response_dic.get('errmsg'), response_dic.get('errcode')), "errorCode": 1, "data": {}}
    return response_dic.get('openid'), response_dic.get('unionid'), response_dic.get('session_key')


def get_wechat_token():
    '''
    获取微信小程序的access_token
    :return : access_token
    '''
    aappid = WECHAT_MINI_APPID
    secret = WECHAT_MINI_SECRET
    get_user_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'.format(appid, secret)
    response = requests.get(url=get_user_url)
    # print('msg：',eval(response.text), type(eval(response.text)))
    response_dic = eval(response.text)
    if response_dic.get('errcode') and response_dic.get('errcode') != 0:
        return {"message": "微信端推送错误：%s,errcode=%s" % (response_dic.get('errmsg'), response_dic.get('errcode')), "errorCode": 1, "data": {}}
    return response_dic.get('access_token')


def wechat_app_login(code):
    '''
    微信APP登录方法
    :param code: 微信APP调用登录的code
    :return : obj
    '''
    appid = WECHAT_APP_APPID
    secret = WECHAT_APP_SECRET
    get_user_url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid={}&secret={}&code={}&grant_type=authorization_code'.format(appid, secret, code)
    response = requests.get(url=get_user_url)
    print('msg：',eval(response.text), type(eval(response.text)))
    response_dic = eval(response.text)
    if response_dic.get('errcode') and response_dic.get('errcode') != 0:
        return {"message": "微信端推送错误：%s,errcode=%s" % (response_dic.get('errmsg'), response_dic.get('errcode')), "errorCode": 1, "data": {}}
    access_token = response_dic.get('access_token')
    open_id = response_dic.get('openid')
    get_user_info = 'https://api.weixin.qq.com/sns/userinfo?access_token={}&openid={}&lang=zh_CN'.format(access_token, open_id)
    response = requests.get(url=get_user_info)
    print('msg：',eval(response.text), type(eval(response.text)))
    response_dic = json.loads(response.text.encode('iso-8859-1').decode('utf8'))
    print('userinfo：', response_dic)
    if response_dic.get('errcode') and response_dic.get('errcode') != 0:
        return {"message": "微信端推送错误：%s,errcode=%s" % (response_dic.get('errmsg'), response_dic.get('errcode')), "errorCode": 1, "data": {}}
    return response_dic


def create_password(password):
    '''
    生成加密密码
    :param password: 明文密码
    :return : 密文密码
    '''
    h = hashlib.sha256()
    h.update(bytes(password, encoding='utf-8'))
    h_result = h.hexdigest()
    return h_result

def create_code(abc=True):
    '''
    生成随机验证码
    :param abc: 类型，为真时返回带字母的验证码，否则返回不带字母的验证码
    :return : 六位验证码
    '''
    if abc:
        base_str = '0123456789qwerrtyuioplkjhgfdsazxcvbnm'
    else:
        base_str = '0123456789'
    return ''.join([random.choice(base_str) for _ in range(6)])

def create_order(order_type):
    '''
    生成订单编号
    :param order_type: 类型，根据类型生成不同的订单编号
    :return : 32位订单编号
    '''
    now_date_time_str = str(
        datetime.datetime.now().strftime('%Y%m%d%H%M%S%f'))
    base_str = '01234567890123456789'
    random_num = ''.join(random.sample(base_str, 6))
    random_num_two = ''.join(random.sample(base_str, 5))
    order_num = now_date_time_str + str(order_type) + random_num + random_num_two
    return order_num


def getDistance(lat1, lng1, lat2, lng2):
    '''
    计算两经纬度之间的距离
    :param lat1: 纬度1
    :param lng1: 经度1
    :param lat2: 纬度2
    :param lng2: 经度2
    :return : 返回距离单位为公里
    '''
    radLat1 = (lat1 * math.pi / 180.0)
    radLat2 = (lat2 * math.pi / 180.0)
    a = radLat1 - radLat2
    b = (lng1 * math.pi / 180.0) - (lng2 * math.pi / 180.0)
    s = 2 * math.asin(math.sqrt(math.pow(math.sin(a/2), 2) + math.cos(radLat1) * math.cos(radLat2) * math.pow(math.sin(b/2), 2)))
    s = s * 6378.137
    return s