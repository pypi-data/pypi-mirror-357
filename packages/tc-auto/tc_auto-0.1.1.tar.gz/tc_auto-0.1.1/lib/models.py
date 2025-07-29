import json


class Model(object):

    def __init(self, user=None, uri='/v2/index.php', method='POST', token=None, region=None, profile=None,
               sign_method=None):
        """
        :param user:
        :param uri:
        :param method:
        :param token:
        :param region:
        :param profile:
        :param sign_method:
        :return:
        """
        self.user = user
        self.uri = uri
        self.method = method
        self.token = token
        self.region = region
        self.profile = profile
        self.sign_method = sign_method
        self.init_client_models(**{
            'user': user,
            'uri': uri,
            'method': method,
            'token': token,
            'region': region,
            'profile': profile,
            'sign_method': sign_method
        })

    def init_client_models(self, **kwargs):
        """
        初始化客户端模型
        :param kwargs:
        :return:
        """
        pass

    @staticmethod
    def convert_request(req, **kwargs):
        """
        转换请求参数
        :param req: 请求模型
        :param kwargs: 其他参数
        :return: 转换后的请求模型
        """
        if kwargs:
            req_dict = req._serialize()
            req_dict.UPDATE(kwargs)
            req_json = json.dumps(req_dict)
            req.from_json_string(req_json)
        if 'header' in kwargs:
            req._headers = kwargs['header']
        return req
