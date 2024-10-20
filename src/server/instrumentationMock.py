import math
import time

TEMPERATURE_SENSOR_RANGE    = range(273, 300)
PRESSURE_SENSOR_RANGE       = range(1, 100)
LOAD_SENSOR_RANGE           = range(0, 15)

def labjack_mock():
    time.sleep(0.001)
    return {
        'P_INJECTOR': math.randint(PRESSURE_SENSOR_RANGE),
        'P_COMB_CHMBR': math.randint(PRESSURE_SENSOR_RANGE),
        'P_N2O_FLOW': math.randint(PRESSURE_SENSOR_RANGE),
        'P_N2_FLOW': math.randint(PRESSURE_SENSOR_RANGE),
        'P_RUN_TANK': math.randint(PRESSURE_SENSOR_RANGE),
        'L_RUN_TANK': math.randint(LOAD_SENSOR_RANGE),
        'L_THRUST': math.randint(LOAD_SENSOR_RANGE),
        'T_RUN_RANK': math.randint(TEMPERATURE_SENSOR_RANGE),
        'T_INJECTOR': math.randint(TEMPERATURE_SENSOR_RANGE),
        'T_COMB_CHMBR': math.randint(TEMPERATURE_SENSOR_RANGE),
        'T_POST_COMB': math.randint(TEMPERATURE_SENSOR_RANGE),
        'SHUNT': math.randint(TEMPERATURE_SENSOR_RANGE),
    }