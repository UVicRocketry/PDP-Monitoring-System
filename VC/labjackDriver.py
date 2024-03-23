import sys
import traceback
from datetime import datetime as dt
from enum import Enum
import u6
import logbook
from logPhrases import InstrumentationLogPhrases

class InstrumentationCommand(Enum):
    STATUS = "STATUS",
    RESET_SENSOR = "RESET_SENSOR",
    STREAM_SENSORS = "STREAM_SENSORS",
    SAMPLE_SENSORS = "SAMPLE_SENSORS"


class LabJackU6Driver:
    def __init__(self):
        self.__d = u6.U6()
        self.__logger = logbook.Logger("LabJackU6Driver")
        self.log = None

        self.MAX_REQUESTS = 50
        self.SCAN_FREQUENCY = 5000
        self.__missed = 0
        self.__dataCount = 0
        self.__packetCount = 0
        
        self.__configure_log()
        try:
            self.__calibrate()
        except Exception as e:
            self.__logger.error(f"Failed to calibrate: {e}")
            traceback.print_exc(file=sys.stdout)
            sys.exit(1)
        
    
    def __configure_log(self):
        self.log = logbook.FileHandler('instrumentation.log', level='DEBUG', bubble=True)
        self.log.format_string = '{record.time:%Y-%m-%d %H:%M:%S.%f%z} [{record.level_name}] {record.channel}: {record.message}'
        self.log.push_application()

    def __calibrate(self):
        self.__d.getCalibrationData()

    def choose_mode(self, command):
        if command == InstrumentationCommand.STATUS:
            self.log.write("INFO", InstrumentationLogPhrases.STARTING_STATUS_MODE)
            self.__status()
        elif command == InstrumentationCommand.RESET_SENSOR:
            self.log.write("INFO", InstrumentationLogPhrases.STARTING_RESET_SENSOR_MODE)
            self.__reset_sensor()
        elif command == InstrumentationCommand.STREAM_SENSORS:
            self.log.write("INFO", InstrumentationLogPhrases.STARTING_SAMPLE_SENSORS_MODE)
            self.__stream_sensors()
        elif command == InstrumentationCommand.SAMPLE_SENSORS:
            self.log.write("INFO",  InstrumentationLogPhrases.STARTING_SAMPLE_SENSORS_MODE)
            self.__sample_sensors()
    
    def __status(self):
        print("Status")

    def __reset_sensor(self):
        print("Reset Sensor")

    def __stream_sensors(self):
        print("Stream Sensors")
    
    def __sample_sensors(self):
        print("Sample Sensors")
