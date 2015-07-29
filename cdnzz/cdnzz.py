# coding: utf8

"""


* Copyright (C) 2015 GridSafe, Inc.
"""

import json
import time
import sys

import requests

import settings

_SYS_ENCODE = sys.getfilesystemencoding()

class CDNZZException(Exception):
    def __init__(self, msg, error=50000, result=None):
        self.error = error
        self.msg = msg
        self.result = result
        super(CDNZZException, self).__init__("%s(%d)" % (
            self.msg.encode(_SYS_ENCODE), self.error))


class CDNZZRequestError(CDNZZException):
    pass


class CDNZZ(object):
    def __init__(self, user, secretkey, auto_auth=True):
        """

        :param user: 用户 Email
        :param secretkey: 用户 secretkey，可到官网 "个人信息" 页查看
        :param auto_auth: 开启自动认证, 若开启则会自动获取 token 并在 token 过期时重新获取
        :return:
        """
        self.user = user
        self.secretkey = secretkey
        self.auto_auth = auto_auth

        self.token = ""
        self.token_expires = 0

    def __do_post_request(self, method, **params):
        params["method"] = method
        if "user" not in params:
            params["user"] = self.user
        if "secretkey" not in params:
            if self.auto_auth and not self._check_token():
                self.fetch_token()
            params["token"] = self.token

        text = requests.post(settings.API_URL, data=params,
                             headers={"User-Agent": settings.USER_AGENT}).text
        try:
            d = json.loads(text)
        except ValueError as e:
            raise CDNZZException(str(e))

        if d["error"] != 0:
            raise CDNZZRequestError(d["msg"], d["error"])
        return d["result"]

    def post_request(self, method, **params):
        for k in params.keys():
            if params[k] is None:
                params.pop(k)
        try:
            rv = self.__do_post_request(method, **params)
        except CDNZZRequestError as e:
            # 如果开启了 auto_auth, 当出现 token 错误时尝试重新获取 token 后再次提交请求
            if self.auto_auth and e.error == settings.INVALID_TOKEN_ERROR:
                self.fetch_token()
                rv = self.__do_post_request(method, **params)
            else:
                raise e
        return rv

    def _check_token(self):
        return bool(self.token and 0 < self.token_expires < time.time())

    def fetch_token(self, expires=None, name=None):
        """

        :param expires: token 有效时长， 不设置时由服务端控制(默认 10分钟)
        :param name: token 的名字, 用于区分不同的 token 用途
        :return:
        """
        params = dict(secretkey=self.secretkey)
        if expires is not None:
            params["exp"] = int(time.time() + expires)
        if name is not None:
            params["name"] = name
        result = self.post_request("FetchToken", **params)
        self.token = result["token"]
        self.token_expires = result["payload"]["exp"]
        return self.token

    def add_domain(self, domain):
        return self.post_request("AddDomain", domain=domain)

    def list_domain(self):
        return self.post_request("ListDomain")

    def fetch_verify_info(self, domain):
        return self.post_request("FetchVerifyInfo", domain=domain)

    def verify_domain(self, domain):
        """请求验证域名并返回域名验证信息

        :param domain:
        :return:
        """
        return self.post_request("VerifyDomain", domain=domain)

    def add_sub_domain(self, domain, host, type_, value):
        """

        :param domain:
        :param host: site name, eg: "www"
        :param type_: "CNAME" or "A"
        :param value: "DOMAIN" or "IP"
        :return:
        """
        return self.post_request("AddSubDomain", domain=domain,
                                 host=host, type=type_, value=value)

    def del_sub_domain(self, domain, sub_id):
        return self.post_request("DelSubDomain", domain=domain, sub_id=sub_id)

    def list_sub_domain(self, domain):
        return self.post_request("ListSubDomain", domain=domain)

    def modify_sub_domain(self, domain, sub_id, host, type_, value):
        return self.post_request("ModifySubDomain", domain=domain,
                                 sub_id=sub_id, host=host, type=type_, value=value)

    def active_sub_domain(self, domain, sub_id):
        return self.post_request("ActiveSubDomain", domain=domain, sub_id=sub_id)

    def inactive_sub_domain(self, domain, sub_id):
        return self.post_request("InactiveSubDomain", domain=domain, sub_id=sub_id)

    def add_preload(self, url):
        return self.post_request("AddPreload", url=url)

    def purge_cache(self, url):
        return self.post_request("PurgeCache", url=url)

    def fetch_bandwidth(self, domain, sub_name, start_day=None, end_day=None):
        return self.post_request("FetchBandwidth", domain=domain, sub_name=sub_name,
                                 start_day=start_day, end_day=end_day)

    def fetch_traffic(self, domain, sub_name, start_day=None, end_day=None):
        return self.post_request("FetchTraffic", domain=domain, sub_name=sub_name,
                                 start_day=start_day, end_day=end_day)
