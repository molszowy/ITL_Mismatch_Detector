"""
Mateusz Olszowy, Cisco Systems, 2018
Python 3.6+
"""

import asyncio
import logging
import constants
from devices import test_api, get_device_names, get_registered_devices
from web_access import test_web_access

logger = logging.getLogger('itl_mismatch_detector')

async def main():
    """
    Main
    """

    # Gather inputs
    pub_ip_address = input('IP address of CUCM Publisher:')
    username = input('API Username:')
    password = input('API Password:')
    #pub_ip_address = '10.48.46.177'
    #username = 'admin'
    #password = 'C1sc0123'

    # Test connectivity
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

    # Main logic
    start = input('Enable the web access on all devices, restart them and when ready, type "y": ')
    if start.strip() != 'y':
        print('The script was stopped!')
        return

    device_names = await get_device_names(username, password, axl_url)
    logger.info('Gathered %s phones via AXL: %s', len(device_names), device_names)
    print(f'Gathered {len(device_names)} phones via AXL.')

    if not device_names:
        print('No devices found!')
        return

    registered_devices = await get_registered_devices(username, password, ris_url, device_names)
    print(f'The number of registered devices: {len(registered_devices)}.')

    if not registered_devices:
        print('No devices registered!')
        return

    proceed = input('Do you want to proceed with web access checks for all registered devices ? Type "y": ')
    if proceed.strip() != 'y':
        print('The script was stopped!')
        return

    registered_devices_after_checks = await test_web_access(registered_devices)

    devices_with_itl_mismatches = [device for device in registered_devices_after_checks if device.web_access == False]
    print(f'The list of devices with potential ITL mismatches: {devices_with_itl_mismatches}')

    return devices_with_itl_mismatches


# Start the main loop
loop = asyncio.get_event_loop()
loop.run_until_complete(main())