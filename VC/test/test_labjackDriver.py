import unittest
from ...VC.instrumentation.labjackDriver import LabJackU6Driver

class TestLabJackDriver(unittest.TestCase):
    def test_initialization(self):
        driver = LabJackU6Driver()
        self.assertIsNotNone(driver)
        self.assertIsNotNone(driver.__d)
        self.assertIsNotNone(driver.__logger)
        self.assertIsNotNone(driver.log)
        self.assertIsNotNone(driver.data)
        self.assertEqual(driver.MAX_REQUESTS, 10000)
        self.assertEqual(driver.SCAN_FREQUENCY, 5000)
        self.assertEqual(driver.__missed, 0)
        self.assertEqual(driver.__dataCount, 0)
        self.assertEqual(driver.__packetCount, 0)
        self.assertFalse(driver._finished)