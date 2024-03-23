from enum import Enum

class InstrumentationLogPhrases(Enum):
    STARTING_STATUS_MODE = "Starting Status mode",
    STARTING_RESET_SENSOR_MODE = "Starting Reset Sensor mode",
    STARTING_STREAM_SENSORS_MODE = "Starting Stream Sensors mode",
    STARTING_SAMPLE_SENSORS_MODE = "Starting Sample Sensors mode",
    STATUS = "Status",
    RESET_SENSOR = "Reset Sensor",
    STREAM_SENSORS = "Stream Sensors",
    SAMPLE_SENSORS = "Sample Sensors"

class ControlsLogPhrases(Enum):
    CONNECTED_TO_MCC = "Connected to MCC",
    UNABLE_TO_CONNECT_TO_DEVICE = "Unable to connect to device, no response",
    CLOSED_CONNECTION = "Closed Connection",
    FAILED_TO_CLOSE_CONNECTION = "Failed to close connection"