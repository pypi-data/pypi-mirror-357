import os
import unittest

from loguru import logger


class TestOCR(unittest.TestCase):
    """
    ocr.py测试用的代码
    """

    def setUp(self) -> None:
        self.SecretId = os.getenv("SecretId", None)
        self.SecretKey = os.getenv("SecretKey", None)

        self.ak: str = os.getenv('ak', None)
        self.sk = os.getenv('sk', None)

    def test_id_key(self):
        if self.SecretId is None or self.SecretKey is None:
            logger.error('请设置SecretId和SecretKey环境变量')
        else:
            logger.info(f'secretId:{self.SecretId} | secretKey: {self.SecretKey}')
