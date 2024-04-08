import sys
import traceback
from datetime import datetime as dt
from enum import Enum
import u6
import logging
from .InstrumentationLogPhrases import InstrumentationLogPhrases
import queue as Queue
from copy import deepcopy
import threading

__name__ = "Instrumentation"

class InstrumentationCommand(Enum):
    STATUS = "STATUS",
    RESET_SENSOR = "RESET_SENSOR",
    STREAM_SENSORS = "STREAM_SENSORS",
    SAMPLE_SENSORS = "SAMPLE_SENSORS"


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
            self.__logger.info(InstrumentationLogPhrases.STARTING_STATUS_MODE)
            self.__status()
        elif command == InstrumentationCommand.RESET_SENSOR:
            self.__logger.info(InstrumentationLogPhrases.STARTING_RESET_SENSOR_MODE)
            self.__reset_sensor()
        elif command == InstrumentationCommand.STREAM_SENSORS:
            self.__logger.info(InstrumentationLogPhrases.STARTING_SAMPLE_SENSORS_MODE)
            self.__stream()
        elif command == InstrumentationCommand.SAMPLE_SENSORS:
            self.__logger.info(InstrumentationLogPhrases.STARTING_SAMPLE_SENSORS_MODE)
            self.__sample_sensors()


    def __status(self):
        print("Status")


    def __reset_sensor(self):
        print("Reset Sensor")


    def start_stream(self, max_requests):
        """
        Name:
            LabJackU6Driver.start_stream(max_requests: int) -> None
        Desc:
            Public entry point that starts streaming sensor data from the LabJack U6 device.
        Args:
            max_requests: The maximum number of requests to make before stopping the stream.
        """
        self.__d.streamConfig(
            NumChannels=1, 
            ChannelNumbers=[0], 
            ChannelOptions=[0], 
            SettlingFactor=1, 
            ResolutionIndex=1, 
            ScanFrequency=self.SCAN_FREQUENCY
        )
        self.MAX_REQUESTS = max_requests
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
                    self.__logger.info(InstrumentationLogPhrases.STREAMING_FINISHED)
                    break
                else:
                    self.__logger.info(InstrumentationLogPhrases.QUEUE_EMPTY_ENDING_STREAM)
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
                    self.__logger.error(InstrumentationLogPhrases.FAILED_TO_STREAM)
                    continue

                self.data.put_nowait(deepcopy(returnDict))

                self.__missed += returnDict['missed']
                self.__dataCount += 1

                if self.__dataCount >= self.MAX_REQUESTS:
                    self._finished = True
                
                self.__d.streamStop()    
                stop = dt.now()

        except Exception as e:
            try:
                self.__d.streamStop()
            except Exception as e:
                self.__logger.error("Failed to stop stream: %s %s" % (type(e), e))
            
            self._finished = True


    def __sample_sensors(self):
        print("Sample Sensors")