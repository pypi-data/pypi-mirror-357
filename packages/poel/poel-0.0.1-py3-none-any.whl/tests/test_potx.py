import os
import unittest

import poel
from poel.api.ocr import SmartStructuralOCRV2, SmartStructuralPro
from poel.api.ocr2excel import RET2excel


class TestTencent(unittest.TestCase):

    def setUp(self):
        self.SecretId = os.getenv("SecretId", None)
        self.SecretKey = os.getenv("SecretKey", None)

        self.ak = os.getenv('ak', None)
        self.sk = os.getenv('sk', None)

    def test_SmartStructuralOCRV2(self):
        r = SmartStructuralOCRV2(id=self.SecretId, key=self.SecretKey,
                                 img_path=r'./test_files/程序员晚枫的手写发票.png')
        print(r)

    def test_SmartStructuralPro(self):
        r = SmartStructuralPro(id=self.SecretId, key=self.SecretKey,
                               img_path=r'./test_files/Snipaste_2025-01-18_14-51-10.jpg')
        print(r)

    def test_doc(self):
        print(poel.__doc__)

    def test_RET2excel(self):
        RET2excel(img_path=r'D:\test\py310\poocr_test\train\imgs', id=self.SecretId, key=self.SecretKey)
