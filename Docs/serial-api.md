# Serial Interface 

A serial connection is used to communicate with both the controls system and the instrumentation system. The controls system uses a USB to connect to the arduino which starts stepper motors and solenoids which controls the valves. This document explains the commands that the arduino can receive and the response it will give.

## Command Structure

Communication between the control components will be done over a USB serial protocol. All sent data will be in CSV form and follow naming and type conventions.

Standard communication consists of a single line of serial data in the following format.

| Source Tag | Data Type | Data Label | Data Value |...| Terminator |
| --- | --- |--- |--- |--- |---|
| MCB | CTRL | N2F | OPEN | ...|\n |

Each field is separated with a comma (NO SPACES). The start of each message will be the source tag of the device from which the message originates. The end of a message will be signified the the \n character. By default all characters are CAPITALIZED.

### Source Tags

| Source Tag | Description |
| --- | --- |
| MCC | Mission Control Computer |
| VC | Valve Control Arduino |

### Data Types

| Data Type | Description |
| --- | --- |
| CTRL | Control data relating the the valve and igniter states |
| ABORT | A keyword that triggers a system SHUTDOWN. Can be reversed. No data is associated with this command |
| UNABORT | Cancels the abort procedure. For when control needs to be reestablished after abort. |
| ACK | An acknowledgement or confirmation of data received. (Optional) May be followed by a copy of the original sent data. |
| STATUS | Indicates a non critical status update. Followed by the status |
| CONNECT | Verifies connection established between senders |
| SUMMARY | Indicates states of components, followed by list of names and states |
### Data Labels & Data Values
Given the current configuration of the valve cart the following data labels and values are used.

| Data Label | Description | Data Values |
| --- | --- |--- |
| N2OF | N2O flow valve | OPEN, CLOSE |
| N2OV | N2O vent valve | OPEN, CLOSE |
| N2F | Valve Control Arduino | OPEN, CLOSE |
| RTV | Run Tank Valve | OPEN, CLOSE |
| NCV | Normally Closed Valve | OPEN, CLOSE |
| EVV | Emergency Vent Valve | OPEN, CLOSE |
| IGPRIME | Igniter Prime switch | OPEN, CLOSE |
| IGFIRE | Igniter Fire Button | OPEN, CLOSE |
| MEV | Main Engine Valve | OPEN, CLOSE |
| STARTUP | Indicates a device has powered on and is beginning its start up process | – |
| READY | Indicates a device is ready to complete tasks | – |
| ARMED | A device is in a active state which will affect the state of the external environment | – |
| DISARMED | Indicates a device is in a suppressed state where it cannot affect its environment | – |
| LISTENING | A device is BLOCKING and waiting for instruction | – |
| CALIB | A device is calibrating | – |

## Serial interface API
The custom defined library `serial-interface.py` is used to abstract these command types above into a .