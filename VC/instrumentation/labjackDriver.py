import sys
import traceback
from datetime import datetime as dt
from enum import Enum
import u6
import logging
# from .InstrumentationLogPhrases import InstrumentationLogPhrases
import queue as Queue
from copy import deepcopy
import threading
import asyncio

import matplotlib.pyplot as plt

__name__ = "Instrumentation"

class InstrumentationCommand(Enum):
    STATUS = "STATUS",
    RESET_SENSOR = "RESET_SENSOR",
    STREAM_SENSORS = "STREAM_SENSORS",
    SAMPLE_SENSORS = "SAMPLE_SENSORS"

SensorCannelMap = {
    "AIN48": "T_RUN_TANK",
    "AIN49": "T_INJECTOR",
    "AIN50": "T_COMBUSTION_CHAMBER",
    "AIN51": "T_POST_COMBUSTION",
    "AIN64": "P_N2O_FLOW",
    "AIN65": "P_N2_FLOW",
    "AIN66": "P_RUN_TANK",
    "AIN67": "P_INJECTOR",
    "AIN68": "P_COMBUSTION_CHAMBER",
    "AIN80": "L_RUN_TANK",
    "AIN81": "L_TRUST",
    "AIN82": "SHUNT"
}


class LabJackU6Driver:
    def __init__(self):
        self.__d = u6.U6()

        self.__logger = logging.getLogger(__name__)
        self.__log_handler = None
        self.__configure_log()
    
        self.data = Queue.Queue()
        self.SCAN_FREQUENCY = 50

        self.__configure_log()
       
        try:
            self.__calibrate()
        except Exception as e:
            self.__logger.error(f"Failed to calibrate: {e}")
            traceback.print_exc(file=sys.stdout)
            sys.exit(1)
        
        try:
            self.__configure_stream()
        except Exception as e:
            self.__logger.error(f"Failed to configure stream: {e}")
            traceback.print_exc(file=sys.stdout)
            sys.exit(1)
    
    def __configure_log(self):
        '''
        Name:
            LabJackU6Driver.__configure_log() -> None
        Desc:
            Configures the log file
        '''
        self.__log_handler = logging.FileHandler('instrumentation.log', mode='w')
        formatter = logging.Formatter('[%(name)s] %(asctime)s [%(levelname)s]: %(message)s')
        self.__log_handler.setFormatter(formatter)
        self.__logger.addHandler(self.__log_handler)
        self.__logger.setLevel(logging.INFO)
        self.__logger.info("Instrumentation Logger configured")
    

    def __calibrate(self):
        self.__d.getCalibrationData()


    def __configure_stream(self):
        """
        Name:
            LabJackU6Driver.start_stream(max_requests: int) -> None
        Desc:
            Public entry point that starts streaming sensor data from the LabJack U6 device.
        Args:
            max_requests: The maximum number of requests to make before stopping the stream.
        """
        negative_channel_pairs = [56, 57, 58, 59, 72, 73, 74, 75, 76, 88, 89, 90] # anything referred to refernce/ground
        positive_channel_pairs = [48, 49, 50, 51, 64, 65, 66, 67, 68, 80, 81, 82] # anything referred to signal
        channel_numbers = positive_channel_pairs
        channel_options = [0xA, 0xA, 0xA, 0xA, 0xA, 0xA, 0xA, 0xA, 0xA, 0xA, 0xA, 0xA]
        settling_factor = 1 # 
        resolution_index = 5 # (auto) 0 - 8 ()
        num_channels = 12 # must match the size of 
        scan_frequency = 50

        self.__d.streamConfig(
            NumChannels=num_channels, 
            ChannelNumbers=channel_numbers,   #82 and 68 arent used. delete if broke 
            ChannelOptions=channel_options, 
            SettlingFactor=settling_factor, 
            ResolutionIndex=resolution_index, 
            ScanFrequency=scan_frequency
        )
        self.__logger.info("Stream configured")


    async def stream(self, queue: asyncio.LifoQueue):
        """
        Name:
            LabJackU6Driver.__stream() -> None
        Desc:
            Starts streaming sensor data from the LabJack U6 device and processes it.
        """
        try:
            self.__d.streamStart()
            while True:
                returnDict = next(self.__d.streamData(convert=False))
                if returnDict is None:
                    self.__logger.error(InstrumentationLogPhrases.FAILED_TO_STREAM)
    
                try:
                    output_voltage = self.__d.processStreamData(returnDict['result']) 
                    formatted_output_voltage = {}
                    self.__logger.info(str(output_voltage))
                    for key in output_voltage:
                        #take the average of the output voltage
                        averaged = sum(output_voltage[key]) / len(output_voltage[key])
                        formatted_output_voltage[SensorCannelMap[key]] = averaged
                    await queue.put(formatted_output_voltage)
                    await asyncio.sleep(0)
                except Exception as e:
                    print(f'Failed to process data: {e}')

        except Exception as e:
            try:
                self.__d.streamStop()
            except Exception as e:
                self.__logger.error("Failed to stop stream: %s %s" % (type(e), e))

    async def processVoltages():
        pass