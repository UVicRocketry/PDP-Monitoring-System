from enum import Enum

__name__ = "serialCommandTypes"

SOURCE_TAG = "VC"

class Valves(Enum):
    N2OF    = "N2OF"
    N2OV    = "N2OV"
    N2F     = "N2F"
    RTV     = "RTV"
    NCV     = "NCV"
    ERV     = "ERV"
    IGPRIME = "IGPRIME"
    IGFIRE  = "IGFIRE"
    MEV     = "MEV"

class DataTypes(Enum):
    CTRL    = "CTRL"
    ABORT   = "ABORT"
    UNABORT = "UNABORT"
    ACK     = "ACK"
    STATUS  = "STATUS"
    CONNECT = "CONNECT"
    SUMMARY = "SUMMARY"

class DataLabels(Enum):
    N2OF        = "N2OF"
    N2OV        = "N2OV"
    N2F         = "N2F"
    RTV         = "RTV"
    NCV         = "NCV"
    ERV         = "ERV"
    IGPRIME     = "IGPRIME"
    IGFIRE      = "IGFIRE"
    MEV         = "MEV"
    STARTUP     = "STARTUP"
    ARMED       = "ARMED"
    DISARMED    = "DISARMED"
    LISTENING   = "LISTENING"
    CALIB       = "CALIB"

class DataValues(Enum):
    OPEN   = "OPEN"
    CLOSE  = "CLOSE"
