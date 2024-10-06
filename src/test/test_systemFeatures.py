import unittest
from serialInterface import serialInterface
from server import ws_server
import asyncio

__name__ = 'SystemFeaturesTestSuite'

class TestTwoWayComms3_1(unittest.TestCase):
    def example_test(self):
        # Test that the server can send a message to the client
        pass

class TestReliableComms3_2(unittest.TestCase):
    def example_test(self):
        # Test that the server can receive a message from the client
        pass

class TestInstrumentationAcquisition3_3(unittest.TestCase):
    def example_test(self):
        # Test that the server can handle a message from the client
        pass

class TestInstrumentationAutomationControl3_5(unittest.TestCase):
    def example_test(self):
        # Test that the server can handle a message from the client
        pass

class TestControlCommands3_6(unittest.TestCase):
    def __init__(self) -> None:
        self.serial = serialInterface.SerialInterface()
        self.socket = ws_server.WebSocketServer()
        asyncio.run(socket.start())
        self.valves = ['N2OF', 'N2OV', 'N2F', 'RTV', 'NCV', 'ERV', 'MEV']
    
    def UT_MC_001(self):
        pass

    def UT_MC_002(self):
        pass

    def UT_MC_003(self):
        pass

    def UT_MC_004(self):
        pass

    def UT_MC_005(self):
        pass

    def UT_MC_006(self):
        for valve in self.valves:
            self.serial.send(f'MCC,CTRL,{valve},OPEN\n')
            while True:
                message = self.serial.stream.readline().decode()
                if message.endswith('\n'):
                    self.assertNotEqual(message.find(f'{valve},OPEN'), -1)
                    break
            self.serial.send(f'MCC,CTRL,{valve},CLOSE\n')
            while True:
                message = self.serial.stream.readline().decode()
                if message.endswith('\n'):
                    self.assertNotEqual(message.find(f'{valve},CLOSE'), -1)
                    break       

class TestMissionControlBoxOverride3_8(unittest.TestCase):
    def example_test(self):
        # Test that the server can handle a message from the client
        pass

if __name__ == '__main__':
    unittest.main()
