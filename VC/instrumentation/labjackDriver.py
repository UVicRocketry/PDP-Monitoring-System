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

        '''
        **streamConfig deatils:**
        
        For information from labjack check out section 5.2.12 of the user manual for the U6 in the docs section of this repo

        - `NumChannels` int: number of channel to sample
        - `ResolutionIndes` int: Resolution index of samples (0-8)
        - `ChannelNumbers' []: which channels to sample
        - `ChannelOptions` []: Set bit 7 for differential reading.
            ChannelOption Byte details: 
                bit 4&5 (GainIndex): 0(b00)=x1, 1(b01)=x10, 2(b10)=x100, 3(b11)=x1000
                bit 7 (differentail): differential mode
    
        -- Set Either: --

        sample rate (Hz) = ScanFrequency * NumChannels

        - `ScanFrequency`: The frequency in Hz to scan the channel list

        -- OR --

        The actual frequency is equal to: frequency=clock/ScanInterval

        - `SamplePerPacket`: how many samples to make per packet
        - `InternalStreamClockFrequency` int: 1 = 4Mhz or 0 = 48Mhz
        - `DivideClockBy256` boolean: If true then deivide clock by 256
        - `ScanInterval` int: How often to scan

        There are two options for frequency:

        either set ScanFrequency _or_ sampleperpacket, internalstreamClockFrequency, divideClockBy256, and ScanInterval
        
        '''
        self.__streamConfigurationDetails = {
            # The number of channels (normally two channel per sensor one positive and one negative)
            "NumChannels": 12,
            # positive channels
            "ChannelNumbers": [48, 49, 50, 51, 64, 65, 66, 67, 68, 80, 81, 82],
            # 
            "ChannelOptions": [0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A],
            #
            "SettlingFactor": 1,
            #
            "ResolutionIndex": 0,
            #
            "ScanFrequency": 12,
            #
            "SamplesPerPacket": 25,
            #
            "InternalStreamClockFrequency": 0,
            #
            "DivideClockBy256": True,
            #
            "ScanInterval": 1
        }

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


    def set_stream_config_details(self, 
        resolution_index=0, 
        settling_factor=1, 
        channel_numbers=[],
        channel_options=[]
    ):
        self.__streamConfigurationDetails['ResolutionIndex'] = resolution_index
        # self.__streamConfigurationDetails['NumChannels'] = 


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

    async def voltageToSensorValues():
        """
        Name: 
            LabJackU6Driver.processVoltages
        """