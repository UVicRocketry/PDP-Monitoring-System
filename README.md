# PDP-Monitoring-System

The Propulsion Development Platform (PDP) Monitoring System is a web-based application that allows users to monitor the status of the engine controls and instrumentation. The PDP is a testbed for the development of propulsion systems, and the monitoring system is used to control valve actuation, monitor sensor readings, and record data. The monitoring system is designed to be used by engineers and technicians who are responsible for the operation of the PDP. 

This repository contains the server for used on valve cart. The server runs off of a linux based ubuntu mini computer which acts as a middle man for controls and instrumentation. The server has a built in websocket api that comminations with a client. The UI repo for this project is [Ground Support v2](https://github.com/klemie/PDP-Monitoring-System-UI), however the api can accommodate any external client given it has a websocket connection. 

# Table of Contents

## [1. Guides](Docs/guides.md)
### [1.1 Installation Guides](Docs/guides.md#installation-guide)
### [1.2 StartUp Guides](Docs/guides.md#startup-guide)
### [1.3 Style Guides](Docs/guides.md#style-guide)
### [1.4 Developer Guides](Docs/guides.md#developer-guide)
## [2. Serial Interface](Docs/serial-api.md#serial-interface)
### [2.1 Command Structure](Docs/serial-api.md#command-structure)
#### [2.2 Source Tags](Docs/serial-api.md#source-tags)
## [3. Communication](Docs/comms.md#communication)
### [3.1 TP-Links](Docs/comms.md#tp-links)
#### [3.2 Setup](Docs/comms.md#setup)
## [4. API](Docs/api.md)
### [4.1 Websocket API](Docs/ws-api.md)
