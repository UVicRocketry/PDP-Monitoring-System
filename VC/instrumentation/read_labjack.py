import u6
import json

'''
NOTE:
  Only change the values between
  ######### BEGIN USER ADJUSTABLE ########

  #########  END USER ADJUSTABLE  ########

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
 
  channel_settings [0, 1]:
    Channels to read from and their settings. For differential pairs, only
    specifiy the positive channel (even numbered). OR a channel mode and 
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

    Ex:
      Channel 0 single ended with gain 10: (0, SINGLE | X10)
      Channel 0,1 differential with gain 1: (0, DIFF | X1)

'''

# Gains
X1    = 0b00000000
X10   = 0b00010000
X100  = 0b00100000
X1000 = 0b00110000

# Channel mode
SINGLE = 0b00000000
DIFF   = 0b10000000

######### BEGIN USER ADJUSTABLE ########

scan_frequency   = 50
resolution_index = 2
settling_factor  = 0
samples_per_packet = 1
channel_settings = [(0, DIFF | X1000)]

# These gains should convert volts to the SI unit of the sensor
PT_Comb_Gain = 10170.95  # [Pa/V] at 10V supply
PT_WXYZ_Gain = 10000.00  # [Pa/V] at 10V supply

#########  END USER ADJUSTABLE  ########

# Set up the stream
d = u6.U6()
d.streamConfig(
        ScanFrequency   = scan_frequency,
        ChannelNumbers  = [x[0] for x in channel_settings],
        ChannelOptions  = [x[1] for x in channel_settings],
        NumChannels     = len(channel_settings),
        ResolutionIndex = resolution_index,
        SettlingFactor  = settling_factor,
        SamplesPerPacket = samples_per_packet)

# Avoid having to power cycle the LJ
try:
    d.streamStop()
except:
    pass

# Stream
d.streamStart()

with open('instrumentation_data.txt', 'w') as file:

    # Contains sensor values in SI units
    converted = {}

    for reading in d.streamData(convert=False):

        # Reading is a dict of many things, one of which is the
        # 'result' which can be passed to processStreamData() to
        # give voltages.

        if reading is not None:

            values = d.processStreamData(reading['result'])

            # Extract values
            PT_Comb = values['AIN0']
            PT_WXYZ = values['AIN2']

            # Convert voltage to sensor value in SI units and store in dict
            converted['PT_Comb'] = (sum(PT_Comb)/len(PT_Comb))*PT_Comb_Gain
            converted['PT_WXYZ'] = (sum(PT_WXYZ)/len(PT_WXYZ))*PT_WXYZ_Gain

            # Write to file so websocket can send to ground support
            file.write(f'{json.dumps(formatted_output_voltage)}\n')




















