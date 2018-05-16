"""devices.py"""

import aiohttp
import asyncio
import logging
from typing import List
from jinja2 import Template
import xml.etree.ElementTree as et
import constants

logger = logging.getLogger('itl_mismatch_detector')


class Device:
    """
    Container for device/phone information

    :param name: device name(SEP<MAC>)
    :param ip_address: device IP address
    :param web_access: Enabled if True otherwise False
    """
    def __init__(self, name: str, ip_address: str = '', web_access:bool = False):
        self.name = name
        self.ip_address = ip_address
        self.web_access = web_access

    def __repr__(self):
        return f'Device(name: {self.name}, ip_address: {self.ip_address}, web_access: {self.web_access})'


async def get_device_names(username: str, password: str, axl_url: str) -> list:
    """
    Use AXL SOAP API to obtain all registered devices from CUCM cluster and return a list of device names
    :param username: AXL API username
    :param password: AXL API password
    :param axl_url: AXL web service URL
    """

    list_of_devices = []

    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False),
                                         auth=aiohttp.BasicAuth(username,password),
                                         headers={'SOAPAction':'CUCM:DB ver=1.0 listPhone'}) as session:
            async with session.post(axl_url, timeout=180, data=constants.AXL_QUERY_TEMPLATE) as resp:
                if resp.status == 200:
                    resp_data = await resp.text()
                    logger.debug('Raw AXL response: %s', resp_data)

                    # Parsing response
                    root = et.fromstring(resp_data)
                    for cm_devices in root.iter(f'return'):
                        for device in cm_devices.findall(f'phone'):
                            name = device.find(f'name').text
                            if name:
                                list_of_devices.append(name)
                else:
                    logger.error('Raw AXL response: %s', await resp.text())
                    print(f'The query failed with HTTP response {resp.status}.')

    except asyncio.TimeoutError:
        logger.error('Connection to %s timed out.' % axl_url)
        print(f'The connection to {axl_url} timed out.')

    return list_of_devices


async def get_registered_devices(username: str, password: str, ris_url: str, devices: list) -> List[Device]:
    """
    Use RIS API to obtain registered devices based on the list of device names
    :param username: API username
    :param password: API password
    :param ris_url: RIS API url
    :param devices: a list of device names(SEP*)
    """

    # RIS API can return maximum 1000 devices so split the list
    chunks = [devices[x:x + 1000] for x in range(0, len(devices), 1000)]

    list_of_devices = []

    for chunk in chunks:
        query = Template(constants.RIS_QUERY_TEMPLATE).render(devices=chunk)

        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False),
                                             auth=aiohttp.BasicAuth(username,password)) as session:
                async with session.post(ris_url, timeout=180, data=query) as resp:
                    if resp.status == 200:
                        resp_data = await resp.text()
                        logger.debug(resp_data)

                        # Parsing response
                        root = et.fromstring(resp_data)
                        # Only one CmDevices tag should be present
                        for cm_devices in root.iter(f'{constants.RIS_NAMESPACE}CmDevices'):
                            for device in cm_devices.findall(f'{constants.RIS_NAMESPACE}item'):
                                name = device.find(f'{constants.RIS_NAMESPACE}Name').text
                                ip = device.find(f'{constants.RIS_NAMESPACE}IPAddress').find(f'{constants.RIS_NAMESPACE}item').find(f'{constants.RIS_NAMESPACE}IP').text

                                if name and ip:
                                    list_of_devices.append(Device(name, ip))
                    else:
                        logger.error('Raw response: %s', await resp.text())
                        print(f'The query failed with HTTP response {resp.status}.')

        except asyncio.TimeoutError:
            logger.error('Connection to %s timed out.' % ris_url)
            print(f'The connection to {ris_url} timed out.')

    return list_of_devices


async def test_api(username: str, password: str, url: str) -> bool:
    """
    Check connectivity by accessing 'url' and BasicAuth
    :param username: API username
    :param password: API passowrd
    :param url: API URL that requires authentication
    """

    logger.info('Running connectivity tests to %s', url)

    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False),
                                         auth=aiohttp.BasicAuth(username,password)) as session:
            async with session.get(url, timeout=30) as resp:
                if resp.status == 200:
                    return True
    except asyncio.TimeoutError:
        return False
    except:
        logger.exception('The test connection failed.')

    return False