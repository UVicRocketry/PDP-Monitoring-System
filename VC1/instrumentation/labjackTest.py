import u6

ChannelNumbers = [80, 88]
ChannelOptions = [0x0A, 0x0A]

default_stream_Config_details = {
    "NumChannels": len(ChannelNumbers),
    "ChannelNumbers": ChannelNumbers,
    "ChannelOptions": ChannelOptions,
    "SettlingFactor": 1,
    "ResolutionIndex": 0,
    "ScanFrequency": 100,
}

d = u6.U6()

d.getCalibrationData()

d.streamConfig(
                NumChannels     = default_stream_Config_details["NumChannels"], 
                ChannelNumbers  = default_stream_Config_details["ChannelNumbers"],   #82 and 68 arent used. delete if broke 
                ChannelOptions  = default_stream_Config_details["ChannelOptions"], 
                SettlingFactor  = default_stream_Config_details["SettlingFactor"], 
                ResolutionIndex = default_stream_Config_details["ResolutionIndex"],
                ScanFrequency   = default_stream_Config_details["ScanFrequency"])

d.streamStart()
while True:
    try: 
        returnDict = next(d.streamData(convert=False))
        output_voltage = d.processStreamData(returnDict['result']) 
        
        for key in output_voltage:
            # take the average of the output voltage
            averaged = sum(output_voltage[key]) / len(output_voltage[key])
            output_voltage[key] = averaged
        
        voltage = output_voltage["AIN80"] - output_voltage["AIN88"]
        reverse_voltage = output_voltage["AIN80"] - output_voltage["AIN88"]

        pressure = 2014.22*voltage
        reverse_pressure = 2014.22*reverse_voltage

        print(f'{output_voltage}, V: {voltage}, reverse_V:{reverse_voltage}, p:{pressure}, reverse_p:{reverse_pressure}')
    except Exception as e: 
        d.close()
        print(f'{e}')

