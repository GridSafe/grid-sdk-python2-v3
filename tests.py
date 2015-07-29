# coding: utf8

"""


* Copyright (C) 2015 GridSafe, Inc.
"""

import unittest
import random
import string
from cdnzz import CDNZZ, CDNZZException, settings
import time


class TestSDK(unittest.TestCase):
    """SDK单元测试"""
    def setUp(self):
        self.api = CDNZZ("apitest@cdnzz.com", "ae5f9bd020556e3cc0ae4fa24b404456")

    def tearDown(self):
        pass

    def test_fetch_token(self):
        old_auto_auth = self.api.auto_auth
        self.api.auto_auth = False
        token = self.api.fetch_token(-10, "apitest")    # token 立刻过期

        try:
            self.api.list_domain()  # 检查 token 过期
        except CDNZZException as e:
            if e.error == settings.INVALID_TOKEN_ERROR:
                pass
            else:
                raise e
        else:
            raise Exception()
        finally:
            self.api.auto_auth = old_auto_auth

    def test_domain(self):
        domain = "{}.api".format("".join(random.sample(string.lowercase, 8)))
        self.assertEqual(self.api.add_domain(domain)["domain"], domain)

        domains_info = self.api.list_domain()
        for domain_info in domains_info:
            if domain_info["domain"] == domain:
                break
        else:
            raise Exception()

        res = self.api.fetch_verify_info(domain)
        self.assertEqual(res["domain"], domain)
        self.assertIsInstance(res["dns_txt_record"], basestring)

        res = self.api.verify_domain(domain)
        self.assertEqual(res["domain"], domain)

    def test_sub_domain(self):
        domain = "api-test.com"
        sub_host = "".join(random.sample(string.lowercase, 8))
        res = self.api.add_sub_domain(domain, sub_host, "CNAME",
                                      "{}.api-test.com".format(sub_host))
        self.assertEqual(res["host"], sub_host)
        sub_id = res["id"]

        res = self.api.del_sub_domain(domain, sub_id)
        self.assertEqual(res["host"], sub_host)
        self.assertEqual(res["id"], sub_id)

        res = self.api.add_sub_domain(domain, sub_host, "A", "1.1.1.1")
        self.assertEqual(res["host"], sub_host)
        self.assertEqual(res["value"], "1.1.1.1")
        res = self.api.add_sub_domain(domain, sub_host, "A", "2.2.2.2")
        self.assertEqual(res["host"], sub_host)
        self.assertEqual(res["value"], "2.2.2.2")

        res = self.api.list_sub_domain(domain)
        self.assertGreater(len(res), 0)
        sub_id = res[0]["id"]
        sub_host = res[0]["host"]

        res = self.api.modify_sub_domain(domain, sub_id, sub_host, "A", "9.9.9.9")
        for info in self.api.list_sub_domain(domain):
            if info["id"] == sub_id and info["value"] == "9.9.9.9":
                break
        else:
            raise Exception()

        res = self.api.active_sub_domain(domain, sub_id)
        self.assertEqual(res["id"], sub_id)
        self.assertTrue(res["active"])

        res = self.api.inactive_sub_domain(domain, sub_id)
        self.assertEqual(res["id"], sub_id)
        self.assertFalse(res["active"])

    def test_add_preload(self):
        try:
            self.api.add_domain("api-test.com")
            self.api.add_sub_domain("api-test.com", "preload", 'A', '66.66.66.66')
        except:
            pass
        url = "http://preload.api-test.com/logo.png"
        res = self.api.add_preload(url)
        self.assertEqual(res["url"], url)

    def test_purge_cache(self):
        try:
            self.api.add_domain("api-test.com")
            self.api.add_sub_domain("api-test.com", "purge-cache", 'A', '66.66.66.66')
        except:
            pass
        url = "http://purge-cache.api-test.com/logo.png"
        res = self.api.purge_cache(url)
        self.assertEqual(res["url"], url)

    def test_fetch_bandwidth(self):
        domain = "api-test.com"
        try:
            self.api.add_domain(domain)
        except:
            pass

        res = self.api.fetch_bandwidth(domain, 'bandwidth')
        res = self.api.fetch_bandwidth(domain, 'bandwidth', start_day='20150701', end_day='20150710')
        self.assertTrue(len(res) >= 0)

    def test_fetch_traffic(self):
        domain = "api-test.com"
        try:
            self.api.add_domain(domain)
        except:
            pass

        res = self.api.fetch_traffic(domain, 'traffic')
        res = self.api.fetch_traffic(domain, 'traffic', start_day='20150701', end_day='20150710')
        self.assertTrue(len(res) >= 0)


if __name__ == "__main__":
    unittest.main()
