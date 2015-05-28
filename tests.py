# coding: utf8

"""


* Copyright (C) 2015 GridSafe, Inc.
"""

import unittest
import random
import string
from cdnzz import CDNZZ, CDNZZException


class TestSDK(unittest.TestCase):
    """SDK单元测试
    """
    def setUp(self):
        # 测试需要相应的账号信息，请根据您的账号信息设置下面的参数
        # 分别为 用户email， 用户 secretkey
        self.api = CDNZZ("apitest@cdnzz.com", "3388b365b1eab03dfd68c578c8fee5fb")

    def tearDown(self):
        pass

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
        self.assertIsInstance(res["html_file_name"], basestring)
        self.assertIsInstance(res["html_file_content"], basestring)

        res = self.api.verify_domain(domain, "dns")
        self.assertEqual(res["domain"], domain)
        res = self.api.verify_domain(domain, "file")
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
        url = "http://api-test.com/logo.png"
        res = self.api.add_preload(url)
        self.assertEqual(res["url"], url)

    def test_purge_cache(self):
        url = "http://api-test.com/logo.png"
        res = self.api.purge_cache(url)
        self.assertEqual(res["url"], url)


if __name__ == "__main__":
    unittest.main()
