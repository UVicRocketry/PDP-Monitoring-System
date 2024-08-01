'''
    This map is accurate as of August 2024
'''
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

'''
    The gain and offset values for the sensors
    approximately linear over our working ranges
    Follows the equation: x*GAIN_OFFSETS["KEY"][0] + GAIN_OFFSETS["KEY"][1]
'''
GAIN_OFFSETS = {
    "P_N2O_FLOW": (9982.03, 0),         # PSI
    "P_N2_FLOW": (9936.41, 0),          # PSI
    "P_RUN_TANK": (10206.74, 0),        # PSI
    "P_INJECTOR": (10170.95, 0),        # PSI
    "L_RUN_TANK": (2014.22, 0.8044),    # kg
    "L_TRUST": (466000, -25.8),         # N 
}

'''
    **stream config details:**
    
    For information from labjack check out section 5.2.12 of the user manual for the U6 in the docs section of this repo

    - `NumChannels` int: number of channel to sample
    - `ResolutionIndex` int: Resolution index of samples (0-8)
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
    
    below is the default configuration for the stream
'''
default_stream_Config_details = {
    "NumChannels": 12,
    "ChannelNumbers": [48, 49, 50, 51, 64, 65, 66, 67, 68, 80, 81, 82],
    "ChannelOptions": [0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A],
    "SettlingFactor": 1,
    "ResolutionIndex": 0,
    "ScanFrequency": 12,
    "SamplesPerPacket": 25,
    "InternalStreamClockFrequency": 0,
    "DivideClockBy256": True,
    "ScanInterval": 1
}