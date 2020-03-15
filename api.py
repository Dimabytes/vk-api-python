import lxml.html
import re
import json
import requests
import time


class InvalidPassword(Exception):
    def __init__(self, value): self.value = value
    def __str__(self): return repr(self.value)


class NotValidMethod(Exception):
    def __init__(self, value): self.value = value
    def __str__(self): return repr(self.value)


class BadApiResponse(Exception):
    def __init__(self, value): self.value = value
    def __str__(self): return repr(self.value)


class Api(object):
    def __init__(self, login, password, proxies=None):
        self.login = login
        self.password = password
        self.proxies = proxies
        self.hashes = {}
        self.session = requests.session()
        self.auth()

    def auth(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'DNT': '1'}
        data = self.session.get('https://vk.com/', headers=headers, proxies=self.proxies)
        page = lxml.html.fromstring(data.content)
        form = page.forms[0]
        form.fields['email'] = self.login
        form.fields['pass'] = self.password
        response = self.session.post(form.action, data=form.form_values(), proxies=self.proxies)
        if "onLoginDone" not in response.text:
            raise InvalidPassword("Invalid login/password")
        return

    def method(self, method, v=5.103, **params):
        if method not in self.hashes:
            self._get_hash(method)
        data = {'act': 'a_run_method', 'al': 1,
                'hash': self.hashes[method],
                'method': method,
                'param_v': v}
        for i in params:
            data["param_" + i] = params[i]
        try:
            answer = self.session.post('https://vk.com/dev', data=data, proxies=self.proxies)
            return json.loads(json.loads(answer.text[4:])['payload'][1][0])['response']
        except KeyError:
            raise BadApiResponse(answer.text)
        except requests.exceptions.ConnectionError:
            time.sleep(15)
            raise BadApiResponse("Can't connect to vk")

    def _get_hash(self, method):
        html = self.session.get('https://vk.com/dev/' + method, proxies=self.proxies)
        hash_0 = re.findall('onclick="Dev.methodRun\(\'(.+?)\', this\);', html.text)
        if len(hash_0) == 0:
            raise NotValidMethod("Method is not valid")
        self.hashes[method] = hash_0[0]
