"""
Mateusz Olszowy, Cisco Systems, 2018
Python 3.6+
"""

import asyncio
import csv
import logging
import constants
from devices import test_api, get_device_names, get_registered_devices
from web_access import test_web_access


# Uncheck to see full logging in stdout
#logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('itl_mismatch_detector')

async def main():
    """
    Main
    """

    ## Gather inputs
    pub_ip_address = input('IP address of CUCM Publisher:')
    username = input('API Username:')
    password = input('API Password:')

    ## API connectivity test

    ris_url = f'https://{pub_ip_address}:8443/{constants.RIS_URL}'
    ris_wsdl = f'https://{pub_ip_address}:8443/{constants.RIS_WSDL}'
    axl_url = f'https://{pub_ip_address}:8443/{constants.AXL_URL}'

    if await test_api(username, password, ris_wsdl) and await test_api(username, password, axl_url):
        logger.info(f'The connection/authentication to {pub_ip_address} was successful.')
        print(f'The connection/authentication to {pub_ip_address} was successful.')
    else:
        logger.error('The connection failed or the username/password is incorrect.')
        print('The connection failed or the username/password is incorrect.')
        return

    ## Fetch registered devices(AXL/RIS)

    device_names = await get_device_names(username, password, axl_url)
    logger.info('Gathered %s phones via AXL: %s', len(device_names), device_names)
    print(f'Gathered {len(device_names)} phones via AXL.')

    if not device_names:
        print('No devices found!')
        return

    registered_devices = await get_registered_devices(username, password, ris_url, device_names)
    logger.info('Gathered %s phones registered: %s', len(registered_devices), registered_devices)
    print(f'The number of registered devices: {len(registered_devices)}.')

    if not registered_devices:
        print('No devices registered!')
        return

    ## Enable web access (manual step)

    start = input('(manual step) ENABLE the web access on all devices, restart them and when all registered back, type "y": ')
    if start.strip() != 'y':
        print('The script was stopped!')
        return

    registered_devices_after_checks = await test_web_access(registered_devices)

    devices_with_itl_mismatches_after_enable = [device for device in registered_devices_after_checks if device.web_access == False]

    logger.info('Devices with enabled web interface: %s', [device for device in registered_devices_after_checks
                                                        if device.web_access == True])

    ## Disable web access (manual step)

    start = input('(manual step) DISABLE the web access on all devices, restart them and when all registered back, type "y": ')
    if start.strip() != 'y':
        print('The script was stopped!')
        return

    registered_devices_after_checks = await test_web_access(registered_devices)

    devices_with_itl_mismatches_after_disable = [device for device in registered_devices_after_checks if
                                                device.web_access == True]

    logger.info('Devices with disabled web interface: %s', [device for device in registered_devices_after_checks
                                                        if device.web_access == False])

    ## Combine results and saved them into the file

    itl_mismatches = devices_with_itl_mismatches_after_enable + devices_with_itl_mismatches_after_disable

    if not itl_mismatches:
        print(f'No ITL mismatches found')
        return

    print(f'Detected {len(itl_mismatches)} devices with potential ITL mismatches!')

    try:
        with open('devices_with_itl_mismatches.csv', newline='', mode='w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(['Device Name', 'IP Address'])
            for device in itl_mismatches:
                writer.writerow([device.name, device.ip_address])

        print(f'Saved devices into devices_with_itl_mismatches.csv')
    # Normally we shouldn't do that but this is to capture all errors
    except Exception as exc:
        logger.exception('Error while saving results to the file:')
        print(f'Error while saving results to the file! Exception message: {exc}')
    return itl_mismatches


# Start the main loop
loop = asyncio.get_event_loop()
loop.run_until_complete(main())