# PDP-Monitoring-System

The Propulsion Development Platform (PDP) Monitoring System is a web-based application that allows users to monitor the status of the engine controls and instrumentation. The PDP is a testbed for the development of propulsion systems, and the monitoring system is used to control valve actuation, monitor sensor readings, and record data. The monitoring system is designed to be used by engineers and technicians who are responsible for the operation of the PDP. 

This repository contains the server for used on valve cart. The server runs off of a linux based ubuntu mini computer which acts as a middle man for controls and instrumentation. The server has a built in api that comminations with a client. A fork of [Ground Support](https://github.com/UVicRocketry/Ground-Support) was used for the client, however the api can accommodate any external client given it has a websocket connection. 

# Table of Contents

## [1. Installation Guide](docs/guides.md#installation-guide)
## [2. Serial Interface](docs/serial-api.md#serial-interface)
### [2.1 Command Structure](docs/serial-api.md#command-structure)
#### [2.2 Source Tags](docs/serial-api.md#source-tags)
## [3. Communication](docs/comms.md#communication)
### [3.1 TP-Links](docs/comms.md#tp-links)
#### [3.2 Setup](docs/comms.md#setup)
## [4. API](docs/api.md)
### [4.1 Websocket API](docs/ws-api.md)
