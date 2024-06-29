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

class SensorCannelMap(Enum):
    T_RUN_TANK = "AIN48",
    T_INJECTOR = "AIN49",
    T_COMBUSTION_CHAMBER = "AIN50",
    T_POST_COMBUSTION = "AIN51",
    P_N2O_FLOW = "AIN64",
    P_N2_FLOW = "AIN65",
    P_RUN_TANK = "AIN66",
    P_INJECTOR = "AIN67",
    P_COMBUSTION_CHAMBER = "AIN68",
    L_RUN_TANK = "AIN80",
    L_TRUST = "AIN81",
    SHUNT = "AIN82"

class LabJackU6Driver:
    def __init__(self):
        self.__d = u6.U6()

        self._logger = logging.getLogger(__name__)
        self.__log_handler = None
        self.__configure_log()
    
        self.data = Queue.Queue()

        self.MAX_REQUESTS = 10000
        self.SCAN_FREQUENCY = 5000
        self.__missed = 0
        self.__dataCount = 0
        self.__packetCount = 0
    
        self._finished = False
        
        self.__configure_log()

        try:
            self.__calibrate()
        except Exception as e:
            self.__logger.error(f"Failed to calibrate: {e}")
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
        self._logger.addHandler(self.__log_handler)
        self._logger.setLevel(logging.INFO)
        self._logger.info("Instrumentation Logger configured")
    

    def __calibrate(self):
        self.__d.getCalibrationData()


    def choose_mode(self, command):
        if command == InstrumentationCommand.STATUS:
            #self.__logger.info(InstrumentationLogPhrases.STARTING_STATUS_MODE)
            self.__status()
        elif command == InstrumentationCommand.RESET_SENSOR:
            #self.__logger.info(InstrumentationLogPhrases.STARTING_RESET_SENSOR_MODE)
            self.__reset_sensor()
        elif command == InstrumentationCommand.STREAM_SENSORS:
            #self.__logger.info(InstrumentationLogPhrases.STARTING_SAMPLE_SENSORS_MODE)
            self.__stream()
        elif command == InstrumentationCommand.SAMPLE_SENSORS:
            #self.__logger.info(InstrumentationLogPhrases.STARTING_SAMPLE_SENSORS_MODE)
            self.__sample_sensors()


    def __status(self):
        print("Status")


    def __reset_sensor(self):
        print("Reset Sensor")


    def start_stream(self):
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
        resulotion_index = 3 # (auto) 0 - 8 ()
        num_channels = 12 # must match the size of 
        scan_frequency = 500

        self.__d.streamConfig(
            NumChannels=num_channels, 
            ChannelNumbers=channel_numbers,   #82 and 68 arent used. delete if broke 
            ChannelOptions=channel_options, 
            SettlingFactor=settling_factor, 
            ResolutionIndex=resulotion_index, 
            ScanFrequency=scan_frequency
        )
        self.__stream()


    def __stream(self):
        """
        Name:
            LabJackU6Driver.__stream() -> None
        Desc:
            Starts streaming sensor data from the LabJack U6 device and processes it.
        """
        self.stream_thread = threading.Thread(target=self.__stream_sensors)
        self.stream_thread.start()
        while True:
            try:
                result = self.data.get(True, 1)
                output_voltage = self.__d.processStreamData(result['result'])
                print(f"Output Voltage: {output_voltage}")
            except Queue.Empty:
                if self._finished:
                    #self.__logger.info(InstrumentationLogPhrases.STREAMING_FINISHED)
                    break
                else:
                    #self.__logger.info(InstrumentationLogPhrases.QUEUE_EMPTY_ENDING_STREAM)
                    self._finished = True
                pass
            except Exception as e:
                self.__logger.error("Exception: %s %s" % (type(e), e))
                self._finished = True
                break

        self.stream_thread.join()


    def __stream_sensors(self):
        """
        Name:
            LabJackU6Driver.__stream_sensors() -> None
        Desc:
            Streams sensor data from the LabJack U6 device and puts it into the data queue for processing.
        """
        self._finished = False

        start = dt.now()
        try:
            self.__d.streamStart()
            while not self._finished:
                returnDict = next(self.__d.streamData(convert=False))

                if returnDict is None:
                    #self.__logger.error(InstrumentationLogPhrases.FAILED_TO_STREAM)
                    continue

                self.data.put_nowait(deepcopy(returnDict))

                self.__missed += returnDict['missed']
                self.__dataCount += 1

                if self.__dataCount >= self.MAX_REQUESTS:
                    self._finished = True
                
                # self.__d.streamStop()    
                stop = dt.now()

        except Exception as e:
            try:
                self.__d.streamStop()
            except Exception as e:
                self.__logger.error("Failed to stop stream: %s %s" % (type(e), e))
            
            self._finished = True


    def __sample_sensors(self):
        print("Sample Sensors")

driver = LabJackU6Driver()
driver.start_stream()
