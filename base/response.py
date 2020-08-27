class RestResponseMsg(object):
    """
    封装响应文本
    """

    def __init__(self):
        self.__res_format = {"message": "ok", "errorCode": 0, "data": {}}

    def update(self, **kwargs):
        """
        更新默认响应文本，也可用于追加
        :param key=val: 传入key=value类型的数据
        :return:
        """
        self.__res_format.update(kwargs)

    @property
    def data(self):
        """
        输出响应文本内容
        :return:
        """
        return self.__res_format
