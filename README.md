# ITL_Mismatch_Detector
This tool connects to CUCM(Cisco Unified Communications Manager) over RIS/AXL APIs and retrives 
all registered devices in order to detect ITL mismatches.


### Prerequisites:
* CUCM version 9+
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
* Checks connectivity(web interface) to all registered phones
* If the web interface is NOT ENABLED after the configuration change,
it's a potential ITL mismatch - the phone does not follow the configuration change.
* Asks to DISABLE the web interface on all phones, reset and wait for them to register back(manual step)
* Checks connectivity to all registered phones
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
Gathered 2 phones via AXL.
The number of registered devices: 1.
Do you want to proceed with web access checks for all registered devices ? Type "y": y
Testing device: SEPxxxxxx 10.10.10.10
The list of devices with potential ITL mismatches: [Device(name: SEPxxxxxx, ip_address: 10.10.10.10, web_access: False)]
```