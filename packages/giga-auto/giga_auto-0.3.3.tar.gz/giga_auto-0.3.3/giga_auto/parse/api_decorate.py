import functools
from functools import wraps

from configs import settings


def api_decorate(url, method='get'):
    """
    装饰api数据，组装配置的路径与api函数里的数据，请求接口
    """

    def _decorate(func):
        func.api_url = url
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            data = func(self, *args, **kwargs) or {}
            data['url'] = url
            data['method'] = method
            response = self._request(**data)
            return response
        return wrapper
    return _decorate


get_api = functools.partial(api_decorate, method='GET')
post_api = functools.partial(api_decorate, method='POST')
delete_api = functools.partial(api_decorate, method='DELETE')
put_api = functools.partial(api_decorate, method='PUT')


def retry_login(times=2):
    def decorator(func):
        @wraps(func)
        def wrapper(self,*args, **kwargs):
            for i in range(times):
                try:
                    result = func(self,*args, **kwargs)
                except Exception as e:
                    self.kwargs['retry_login']=False
                    raise e
                if result==settings.UNAUTHORIZED: # 认证失败重登一次
                    self.kwargs['retry_login']=True
                else:
                    self.kwargs['retry_login'] = False
                    return result
            return None
        return wrapper
    return decorator
