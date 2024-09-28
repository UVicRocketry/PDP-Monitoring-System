import u6
import json

# Gains
X1    = 0b00000000
X10   = 0b00010000
X100  = 0b00100000
X1000 = 0b00110000

# Channel mode
SING = 0b00000000
DIFF = 0b10000000


'''
NOTE:
  Only change the values between
  ######### BEGIN USER ADJUSTABLE ########

  #########  END USER ADJUSTABLE  ########

  (If you add a new sensor you will need to adjust other code too)


Overview:

  LabJackPython provides wraps the low level functions for communicating
  with the labjack so it can be used with python. All of the low level
  functions are discussed in section 5.2 of the U6 user guide.

  This file sets up the LJ in stream mode to acquire data at the fastest
  rate possible. All channels and their settings for each sensor are 
  configured here. Data produced by the LJ is consumed and written to
  a file for later processing.


Sensor Overview:

  Both the CTL-190 and HKM-375 are absolute pressure transducers that have
  a supply voltage of 10VDC, output impedance of 1000 ohms and a differential
  output with full scale range of 100mV.

  All thermocouples used are K-type.

  Load cells used are typical bridge sensors with low output impedance and
  a very small full scale range. Supplied with 5VDC.


streamConfig():

  Streaming data from the LJ is the fastest way to acquire data.
  See section 5.2.12 for StreamConfig documentation for details.

  samples_per_packet:
    The number of samples in each packet sent over USB by the LJ. If the
    number of channels being scanned is low, then this number should be
    set lower than the default of 25, otherwise the packet frequency will
    be lower than desirable. If the number of channels is high then the number
    should be left at 25 or increased.

  scan_frequency:
    The frequency in Hz to scan the channel list (ChannelNumbers). 
    The sample rate (Hz) = scan_frequency * num_channels.

  num_channels:
    Number of channels to stream. Equal to length of channel_numbers.

  resolution_index:
    See section 3.1. Higher values increase ENOB but at the expense
    of longer sample times.

  settling_factor:
    For high impedance sensors, a longer settling time is required to acquire
    enough charge in the ADC to get an accurate reading. LJ says that the
    auto setting is good for any sensor with at most 1000 ohm output 
    impedance. 
    See https://support.labjack.com/docs/analog-input-settling-time-app-note
 
  channel_settings[]:
    Channels to read from and their settings. For differential pairs, only
    specify the positive channel (even numbered). OR a channel mode and 
    gain value together to conveniently set the options for that channel.

    Each channel has options that can be set with the ChannelOptions byte.
    These options should be configured for each type of sensor to account
    for their output impedance, fullscale range etc. Each bit of the byte
    configures a different setting:

      Set bit 4-5 = GainIndex:
        GainIndex   Gain   Max V    Min V
        b00         1      10.1     -10.6
        b01         10     1.01     -1.06
        b10         100    0.101    -0.106
        b11         1000   0.0101   -0.0106
    
      Set bit 7 for differential reading.


Adding a Sensor: 
    1) Add a new tuple to channel_settings with the LJ pin the sensor is
       connected to. For single ended sensors, this is just the single
       sensor pin. For differential, it is the positive channel. LJ will
       automatically configure the negative channel.

       The tuple should have the form: (CHAN_NUM, SETTINGS)
       Ex: Channel 0 single ended with gain 10:  (0, SING | X10)
           Channel 2,3 differential with gain 1: (2, DIFF | X1)

    2) Add a new GAIN variable and OFFSET variable if needed that converts
       the raw voltage from the sensor to the appropriate SI unit.

    3) Add a new variable (called CHAN_XXX where XXX refers to the sensor name)
       to refer to the pin the sensor is connected to. Again for single ended
       just use the pin, and differential the positive channel. This is used
       for lookup in the LJ results dictionary. The LJ naming convention is 
       'AINX' where X is the pin number (1, 2, .. 56 etc)

    4) Add a few lines of code to read and convert the voltage to SI:

       if reading is not None:

           # Add and fill out this line
           SENSOR_NAME = values[CHAN_XXX]
           converted['SENSOR_NAME'] = GAIN*SENSOR_NAME + OFFSET # etc...

        Thats it, Have fun with your new sensor!
    
'''

######### BEGIN USER ADJUSTABLE #########

# Stream settings
scan_frequency   = 25
resolution_index = 2
settling_factor  = 2
samples_per_packet = 50
channel_settings = [(86, DIFF | X1000), # L_RUN_TANK (SEEMS GOOD. CHECK CAL)
                    (87, DIFF | X1000), # L_THRUST (VERY NOISY)

                    (82, DIFF | X100),  # P_INJECTOR (GOOD!)
                    (85, DIFF | X100),  # P_COMB_CHMBR
                    (84, DIFF | X100),  # P_N2O_FLOW
                    (83, DIFF | X100),  # P_N2_FLOW
                    (81, DIFF | X100),  # P_RUN_TANK
                    
                    (55, SING | X100),  # T_COMB_CHMBR
                    (53, SING | X100),  # T_POST_COMB_CHMBR
                    (57, SING | X100),  # T_INJECTOR
                    (49, SING | X100)]  # T_RUN_TANK 

# These gains and offsets convert raw volts to the SI unit of the sensor

# 6895 converts PSI to Pa. *2 since running on 5V supply rather than 10V
GAIN_P_COMB_CHMBR = 2*6895*0.0       # [Pa/V] at 10V supply TODO: Not in use
GAIN_P_N2O_FLOW   = 2*6895*9982.03   # [Pa/V] at 10V supply 
GAIN_P_N2_FLOW    = 2*6895*9936.41   # [Pa/V] at 10V supply
GAIN_P_RUN_TANK   = 2*6895*10206.74  # [Pa/V] at 10V supply
GAIN_P_INJECTOR   = 2*6895*10170.95  # [Pa/V] at 10V supply

GAIN_L_RUN_TANK   = 2014.22   # [N/V]  at 5V supply
GAIN_L_THRUST     = 466000    # [N/V]  at 5V supply 

OFFSET_L_THRUST   = -25.8     # [N] # TODO double check
OFFSET_L_RUN_TANK = -5.8      # [N] # TODO add 

# Channel mapping from LJ to sensor
CHAN_L_RUN_TANK   = 'AIN86'
CHAN_L_THRUST     = 'AIN87'

CHAN_P_COMB_CHMBR = 'AIN85'
CHAN_P_N2O_FLOW   = 'AIN84'
CHAN_P_N2_FLOW    = 'AIN83'
CHAN_P_RUN_TANK   = 'AIN81'
CHAN_P_INJECTOR   = 'AIN82'

CHAN_T_RUN_TANK   = 'AIN49'
CHAN_T_INJECTOR   = 'AIN57'
CHAN_T_COMB_CHMBR = 'AIN55'
CHAN_T_POST_COMB  = 'AIN53'

CHAN_SHUNT        = 'AIN82' # Not implemented yet on cart

#########  END USER ADJUSTABLE  #########

# Set up the stream
d = u6.U6()

#Get starting reference temp of LabJack
Tref = d.getTemperature() - 273.15

c0 = -1.7600413686 * 10**-2
c1 = 3.8921204975 * 10**-2
c2 = 1.8558770032 * 10**-5
c3 = -9.9457592874 * 10**-8
c4 = 3.1840945719 * 10**-10
c5 = -5.6072844889 * 10**-13
c6 = 5.6075059059 * 10**-16
c7 = -3.2020720003 * 10**-19
c8 = 9.7151147152 * 10**-23
c9 = -1.2104721275 * 10**-26

voltage_reference = c0 + \
                    c1*Tref + \
                    c2*Tref**2 + \
                    c3*Tref**3 + \
                    c4*Tref**4 + \
                    c5*Tref**5 + \
                    c6*Tref**6 + \
                    c7*Tref**7 + \
                    c8*Tref**8 + \
                    c9*Tref**9

d.streamConfig(
        ScanFrequency   = scan_frequency,
        ChannelNumbers  = [x[0] for x in channel_settings],
        ChannelOptions  = [x[1] for x in channel_settings],
        NumChannels     = len(channel_settings),
        ResolutionIndex = resolution_index,
        SettlingFactor  = settling_factor,
        SamplesPerPacket = samples_per_packet)

if samples_per_packet < len(channel_settings):
    raise ValueError \
            ("samples_per_packet: (" + str(samples_per_packet) + \
             ") must be at least the number of channels: (" + \
             str(len(channel_settings)) + ")!")

# Stream data from the LJ
try:
    d.streamStart()
except Exception as e:
    print("Failed to start LabJack")
    print(str(e))

if d is None:
    print("No LabJack device connected. Exiting...")
    exit()
else:
    d.streamStart()

# Function to turn thermocouple voltages to kelvin
def v_to_K(voltage):
    voltage_actual = voltage
    if voltage > 0.020644 and voltage < 0.054886:
        C0 = -131.8058
        C1 = 48.30222
        C2 = -1.646031 
        C3 = 0.05464731
        C4 = -0.0009650715
        C5 = 0.000008802193
        C6 = -0.00000003110810
        C7 = 0
        C8 = 0
        C9 = 0
    elif voltage > -0.005891 and voltage < 0:
        C0 = 0
        C1 = 25.173462
        C2 = -1.1662878
        C3 = -1.0833638
        C4 = -0.89773540
        C5 = -0.37342377
        C6 = -0.086632643
        C7 = -0.010450598
        C8 = -0.00051920577
        C9 = 0
    elif voltage > 0 and voltage < 0.020644:
        C0 = 0
        C1 = 25.08355
        C2 = 0.07860106
        C3 = -0.2503131
        C4 = 0.08315270
        C5 = -0.01228034
        C6 = 0.0009804036
        C7 = -0.0000413030
        C8 = 0.000001057734
        C9 = -0.00000001052755
    else:
       return 0
    
    voltage_actual = voltage_actual*1000

    tempC = C0 + \
    C1*voltage_actual + C2*voltage_actual**2 + C3*voltage_actual**3 + \
    C4*voltage_actual**4 + C5*voltage_actual**5 + C6*voltage_actual**6 + \
    C7*voltage_actual**7 + C8*voltage_actual**8 + C9*voltage_actual**9
   
    return (tempC + 273.15)

try:
    with open('instrumentation_data.txt', 'w') as file:

        # Contains sensor values in SI units
        converted = {}

        for reading in d.streamData(convert=False):

            # Reading is a dict of many things, one of which is the
            # 'result' which can be passed to processStreamData() to
            # give voltages.

            if reading is not None:

                values = d.processStreamData(reading['result'])

                # Extract values from each channel
                P_INJECTOR   = values[CHAN_P_INJECTOR]
                P_COMB_CHMBR = values[CHAN_P_COMB_CHMBR]
                P_N2O_FLOW   = values[CHAN_P_N2O_FLOW]
                P_N2_FLOW    = values[CHAN_P_N2_FLOW]
                P_RUN_TANK   = values[CHAN_P_RUN_TANK]

                L_RUN_TANK   = values[CHAN_L_RUN_TANK]
                L_THRUST     = values[CHAN_L_THRUST]

                T_RUN_TANK   = values[CHAN_T_RUN_TANK]
                T_INJECTOR   = values[CHAN_T_INJECTOR]
                T_COMB_CHMBR = values[CHAN_T_COMB_CHMBR]
                T_POST_COMB  = values[CHAN_T_POST_COMB]

                SHUNT        = values[CHAN_SHUNT]

                # Convert voltage to sensor value in SI units and store in dict
                converted['P_INJECTOR'] = \
                (sum(P_INJECTOR)/len(P_INJECTOR))*GAIN_P_INJECTOR

                converted['P_COMB_CHMBR'] = \
                (sum(P_COMB_CHMBR)/len(P_COMB_CHMBR))*GAIN_P_COMB_CHMBR

                converted['P_N2O_FLOW'] = \
                (sum(P_N2O_FLOW)/len(P_N2O_FLOW))*GAIN_P_N2O_FLOW

                converted['P_N2_FLOW'] = \
                (sum(P_N2_FLOW)/len(P_N2_FLOW))*GAIN_P_N2_FLOW

                converted['P_RUN_TANK'] = \
                (sum(P_RUN_TANK)/len(P_RUN_TANK))*GAIN_P_RUN_TANK

                converted['L_RUN_TANK'] = \
                (sum(L_RUN_TANK)/len(L_RUN_TANK))*GAIN_L_RUN_TANK+OFFSET_L_RUN_TANK

                converted['L_THRUST'] = \
                (sum(L_THRUST)/len(L_THRUST))*GAIN_L_THRUST+OFFSET_L_THRUST

                # Thermocouples
                converted['T_RUN_TANK'] = v_to_K(sum(T_RUN_TANK)/len(T_RUN_TANK))
                converted['T_INJECTOR'] = v_to_K(sum(T_INJECTOR)/len(T_INJECTOR))
                converted['T_COMB_CHMBR'] = v_to_K(sum(T_COMB_CHMBR)/len(T_COMB_CHMBR))
                converted['T_POST_COMB'] = v_to_K(sum(T_POST_COMB)/len(T_POST_COMB))

            print(f'v:{sum(T_RUN_TANK)/len(T_RUN_TANK)}, t: {v_to_K(sum(T_RUN_TANK)/len(T_RUN_TANK))}')

            # Write to file so websocket can send to ground support
            file.write(f'{json.dumps(converted)}\n')

            with open('tmp.txt', 'w') as tmp:
              tmp.write(f'{json.dumps(converted)}')
              tmp.write('\n!')
except:
    print("Interrupt signal received!")
finally:
    d.streamStop()
    print("Stream stopped.\n")
    d.close()
