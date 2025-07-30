from typing import Union

import requests

from giga_auto.logger import log

DEFAULT_TIMEOUT = 60


class RequestBase(object):

    def __init__(self, base_url: str = '', expect_code=200):
        """
        :param base_url: The base URL of the API
        """
        self.base_url = base_url.rstrip('/')
        self._session = requests.Session()
        self._session.timeout = DEFAULT_TIMEOUT
        self.expect_code = expect_code

    @log
    def _request(self, method, url, **kwargs):
        if not url.startswith('http'):
            url = f'{self.base_url}{url}' if 'route' in self.base_url else f'{self.base_url}/{url.lstrip("/")}'
        response = self._session.request(method.upper(), url, **kwargs)
        try:
            return response.json()
        except:
            return response

    def request(self, method, url, **kwargs) -> Union[dict, list, str]:
        response = self._request(method, url, **kwargs)
        if 'code' in response and isinstance(response, dict):
            if response['code'] != self.expect_code:
                raise Exception(f"Response error: {response}")
        return response

    def get(self, url, **kwargs) -> Union[dict, list, str]:
        return self.request('GET', url, **kwargs)

    def post(self, url, **kwargs) -> Union[dict, list, str]:
        return self.request('POST', url, **kwargs)

    def put(self, url, **kwargs) -> Union[dict, list, str]:
        return self.request('PUT', url, **kwargs)

    def delete(self, url, **kwargs) -> Union[dict, list, str]:
        return self.request('DELETE', url, **kwargs)

    def patch(self, url, **kwargs) -> Union[dict, list, str]:
        return self.request('PATCH', url, **kwargs)
