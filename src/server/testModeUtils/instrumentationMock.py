import math
import time

TEMPERATURE_SENSOR_RANGE    = range(273, 300)
PRESSURE_SENSOR_RANGE       = range(1, 100)
LOAD_SENSOR_RANGE           = range(0, 15)

def labjack_mock():
    time.sleep(0.001)
    return {
        'P_INJECTOR': math.random.choice(PRESSURE_SENSOR_RANGE),
        'P_COMB_CHMBR': math.random.choice(PRESSURE_SENSOR_RANGE),
        'P_N2O_FLOW': math.random.choice(PRESSURE_SENSOR_RANGE),
        'P_N2_FLOW': math.random.choice(PRESSURE_SENSOR_RANGE),
        'P_RUN_TANK': math.random.choice(PRESSURE_SENSOR_RANGE),
        'L_RUN_TANK': math.random.choice(LOAD_SENSOR_RANGE),
        'L_THRUST': math.random.choice(LOAD_SENSOR_RANGE),
        'T_RUN_RANK': math.random.choice(TEMPERATURE_SENSOR_RANGE),
        'T_INJECTOR': math.random.choice(TEMPERATURE_SENSOR_RANGE),
        'T_COMB_CHMBR': math.random.choice(TEMPERATURE_SENSOR_RANGE),
        'T_POST_COMB': math.random.choice(TEMPERATURE_SENSOR_RANGE),
        'SHUNT': math.random.choice(TEMPERATURE_SENSOR_RANGE),
    }