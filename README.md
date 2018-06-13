# ITL Mismatch Detector
This tool automates the process to detect ITL(Initial Trust List) mismatches 
on Cisco IP Phones and Endpoints at scale. 
It generates devices_with_itl_mismatches.csv file that 
lists all registered endpoints with suspected mismatches(Device Name / IP address).


### Prerequisites:
* CUCM(Cisco Unified Communications Manager) version 9+
* AXL service activated on the publisher(Cisco Unified Serviceability)
* Admin user with the 'Standard CCM Super Users' Access Group assigned
* Python 3.6+
* All required dependencies installed
* Connectivity to CUCM and all phones

### Algorithm

The script works in the following way:

* Connects to the AXL(Administrative XML) API in order to fetch configured phones and their names(listPhone operation) 
* Connects to the RIS(Real-Time Information Service) API in order to fetch IP addresses of registered devices
* Asks to ENABLE the web interface on all phones, reset and wait for them to register back(manual step)
* Checks connectivity(web interface - HTTP only) to all registered phones.
* If the web interface is NOT ENABLED after the configuration change,
it's a potential ITL mismatch - the phone does not follow the configuration change.
* Asks to DISABLE the web interface on all phones, reset and wait for them to register back(manual step)
* Checks connectivity(web interface - HTTP only) to all registered phones
* If the web interface is NOT DISABLED after the configuration change,
it's a potential ITL mismatch - the phone does not follow the configuration change.

### Installation

Python3.6+ is required to properly run the script.

```
$ git clone https://github.com/molszowy/ITL_Mismatch_Detector.git
$ cd ITL_Mismatch_Detector
$ pip install -r requirements.txt
```

### Run

```
$ python run.py
IP address of CUCM Publisher:1.1.1.1
API Username:admin
API Password:pass123
The connection/authentication to 1.1.1.1 was successful.
Enable the web access on all devices, restart them and when ready, type "y": y
Device Names via AXL: 10.
Registered devices: 2.
(manual step) ENABLE the web access on all devices, restart them and when all registered back, type "y": y
Testing device: SEPXXXXXXXXA 10.10.10.1
Testing device: SEPXXXXXXXXB 10.10.10.2
(manual step) DISABLE the web access on all devices, restart them and when all registered back, type "y": y
Testing device: SEPXXXXXXXXA 10.10.10.1
Testing device: SEPXXXXXXXXB 10.10.10.2
Detected 1 device(s) with potential ITL mismatches!
Saved devices into devices_with_itl_mismatches.csv
```