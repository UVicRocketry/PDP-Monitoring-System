# Instrumentation Driver


**Installation**
```bash
python -m pip install LabJackPython
```

**setup**
```bash 
python setup.py install
```

**Resources**

https://github.com/labjack/LabJackPython/blob/master/src/u6.py
https://support.labjack.com/docs/labjackpython-for-ud-exodriver-u12-windows-mac-lin

## Configuration

Configuration of the labjack driver is done through altering the pararmters of the `u6.streamConfig()` function.

The most important paramters that must be configured are as follows:

- `ChannelNumbers`: List of channels to stream. ex: [56, 57] which corresponds to AI56 and AI57
- `NumChannels`: Number of channels to stream, this will have to be the **same as length the `ChannelNumbers` list** 
- `ResolutionIndex`:
- `SettlingFactor`:
- `ChannelOptions`: 


For specifics on the paramters please see [U6 Pro User Manual](U6PROUserManual.pdf).

