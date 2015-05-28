# coding: utf8

"""


* Copyright (C) 2015 GridSafe, Inc.
"""

import json
import time
import sys

import jwt
import requests

import settings

_SYS_ENCODE = sys.getfilesystemencoding()

class CDNZZException(Exception):
    def __init__(self, msg, code=50000):
        self.code = code
        self.msg = msg
        super(CDNZZException, self).__init__("%s(%d)" % (self.msg.encode(_SYS_ENCODE), self.code))

class RequestFailed(CDNZZException):
    pass


class CDNZZ(object):
    def __init__(self, user, secretkey):
        """

        :param user: 用户 Email
        :param secretkey: 用户 secretkey，可到官网 "个人信息" 页查看
        :return:
        """
        self.user = user
        self.secretkey = secretkey

        self.token = None
        self.token_expires = None

    def _post_request(self, method, **params):
        params["method"] = method
        if "user" not in params:
            params["user"] = self.user
        if "secretkey" not in params:
            if not self._check_token():
                self.fetch_token()
            params["token"] = self.token

        text = requests.post(settings.API_URL, data=params).text
        try:
            d = json.loads(text)
        except ValueError as e:
            raise CDNZZException(e)

        if d["error"] != 0:
            raise RequestFailed(d["msg"], d["error"])
        return d["result"]

    def _check_token(self):
        return bool(self.token and self.token_expires < time.time())

    def fetch_token(self, expires=None):
        params = dict(secretkey=self.secretkey)
        if expires:
            params["token_exp"] = int(time.time() + expires)
        result = self._post_request("FetchToken", **params)
        token = result["token"]
        try:
            payload = jwt.decode(token, self.secretkey)
        except jwt.DecodeError as e:
            raise CDNZZException(e)

        self.token = token
        self.token_expires = payload["exp"]
        return self.token

    def add_domain(self, domain):
        return self._post_request("AddDomain", domain=domain)

    def list_domain(self):
        return self._post_request("ListDomain")

    def fetch_verify_info(self, domain):
        return self._post_request("FetchVerifyInfo", domain=domain)

    def verify_domain(self, domain, verify_type):
        """

        :param domain:
        :param verify_type: "dns" or "file"
        :return:
        """
        return self._post_request("VerifyDomain", domain=domain, verify_type=verify_type)

    def add_sub_domain(self, domain, host, type_, value):
        """

        :param domain:
        :param host: site name, eg: "www"
        :param type_: "CNAME" or "A"
        :param value: DOMAIN or IP
        :return:
        """
        return self._post_request("AddSubDomain", domain=domain,
                                  host=host, type=type_, value=value)

    def del_sub_domain(self, domain, sub_id):
        return self._post_request("DelSubDomain", domain=domain, sub_id=sub_id)

    def list_sub_domain(self, domain):
        return self._post_request("ListSubDomain", domain=domain)

    def modify_sub_domain(self, domain, sub_id, host, type_, value):
        return self._post_request("ModifySubDomain", domain=domain,
                                  sub_id=sub_id, host=host, type=type_, value=value)

    def active_sub_domain(self, domain, sub_id):
        return self._post_request("ActiveSubDomain", domain=domain, sub_id=sub_id)

    def inactive_sub_domain(self, domain, sub_id):
        return self._post_request("InactiveSubDomain", domain=domain, sub_id=sub_id)

    def add_preload(self, url):
        return self._post_request("AddPreload", url=url)

    def purge_cache(self, url):
        return self._post_request("PurgeCache", url=url)

