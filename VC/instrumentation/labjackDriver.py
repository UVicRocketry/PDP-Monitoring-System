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
import random
from .labjackconfig import SensorCannelMap, GAIN_OFFSETS, default_stream_Config_details

import matplotlib.pyplot as plt

__name__ = "Instrumentation"

class InstrumentationCommand(Enum):
    STATUS = "STATUS",
    RESET_SENSOR = "RESET_SENSOR",
    STREAM_SENSORS = "STREAM_SENSORS",
    SAMPLE_SENSORS = "SAMPLE_SENSORS"

class LabJackU6Driver:
    def __init__(self, test_mode=False):
        self.__test_mode = test_mode
        self.__d = None

        if not self.__test_mode:
            self.__d = u6.U6()
        
        self.__logger = logging.getLogger(__name__)
        self.__log_handler = None
        self.__configure_log()

        # see config.py for more information on the stream configuration details
        self.__streamConfigurationDetails = default_stream_Config_details

        if not self.__test_mode:
            try:
                self.__calibrate()
                pass
            except Exception as e:
                self.__logger.error(f"Failed to calibrate: {e}")
                traceback.print_exc(file=sys.stdout)
                sys.exit(1)
        
            try:
                self.__configure_stream()
                pass
            except Exception as e:
                self.__logger.error(f"Failed to configure stream: {e}")
                traceback.print_exc(file=sys.stdout)
                sys.exit(1)


    def set_stream_config_details(self, 
        resolution_index=0, 
        settling_factor=1, 
        channel_numbers=[],
        channel_options=[],
        scan_frequency=12,
        samples_per_packet=25,
        internal_stream_clock_frequency=1,
        divide_clock_by_256=True,
        scan_interval=1
    ):
        self.__d.streamStop()

        self.__streamConfigurationDetails['ResolutionIndex'] = resolution_index
        self.__streamConfigurationDetails['NumChannels'] = len(channel_numbers)
        self.__streamConfigurationDetails['SettlingFactor'] = settling_factor
        self.__streamConfigurationDetails['ChannelNumbers'] = channel_numbers
        self.__streamConfigurationDetails['ChannelOptions'] = channel_options
        self.__streamConfigurationDetails['ScanFrequency'] = scan_frequency
        self.__streamConfigurationDetails['SamplesPerPacket'] = samples_per_packet
        self.__streamConfigurationDetails['InternalStreamClockFrequency'] = internal_stream_clock_frequency
        self.__streamConfigurationDetails['DivideClockBy256'] = divide_clock_by_256
        self.__streamConfigurationDetails['ScanInterval'] = scan_interval

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
        try:
            self.__d.streamConfig(
                NumChannels     = self.__streamConfigurationDetails["NumChannels"], 
                ChannelNumbers  = self.__streamConfigurationDetails["ChannelNumbers"],   #82 and 68 arent used. delete if broke 
                ChannelOptions  = self.__streamConfigurationDetails["ChannelOptions"], 
                SettlingFactor  = self.__streamConfigurationDetails["SettlingFactor"], 
                ResolutionIndex = self.__streamConfigurationDetails["ResolutionIndex"],
                ScanFrequency   = self.__streamConfigurationDetails["ScanFrequency"],
                # -- OR --
                # SamplesPerPacket = self.__streamConfigurationDetails["SamplesPerPacket"],
                # InternalStreamClockFrequency= self.__streamConfigurationDetails["InternalStreamClockFrequency"],
                # DivideClockBy256= self.__streamConfigurationDetails["DivideClockBy256"],
                # ScanInterval    = self.__streamConfigurationDetails["ScanInterval"]
            )
            self.__logger.info("Stream configured")
        except Exception as e:
            print('failed to initalize stream due to: {e}')
      

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
                    
                    print(f'labjackdriver: {formatted_output_voltage}')
                    await queue.put(formatted_output_voltage)
                    await asyncio.sleep(1)

                except Exception as e:
                    print(f'Failed to process data: {e}')

        except Exception as e:
            try:
                self.__d.streamStop()
            except Exception as e:
                self.__logger.error("Failed to stop stream: %s %s" % (type(e), e))


    def voltageToSensorValues():
        """
        Name: 
            LabJackU6Driver.processVoltages
        """


        return


    async def mock_stream(self, queue: asyncio.LifoQueue):
        while True:
            await queue.put({
                "T_RUN_TANK": round(random.uniform(6,10), 3),
                "T_INJECTOR": round(random.uniform(6,10), 3),
                "T_COMBUSTION_CHAMBER": round(random.uniform(6,10), 3),
                "T_POST_COMBUSTION": round(random.uniform(6,10), 3),
                "P_N2O_FLOW": round(random.uniform(6,10), 3),
                "P_N2_FLOW": round(random.uniform(6,10), 3),
                "P_RUN_TANK": round(random.uniform(6,10), 3),
                "P_INJECTOR": round(random.uniform(6,10), 3),
                "P_COMBUSTION_CHAMBER": round(random.uniform(6,10), 3),
                "L_RUN_TANK": round(random.uniform(6,10), 3),
                "L_TRUST": round(random.uniform(6,10), 3),
                "SHUNT": round(random.uniform(6,10), 3)
            })
            await asyncio.sleep(1)