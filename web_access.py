"""web_access.py"""

import aiohttp
import asyncio
import logging
from typing import List
from itertools import islice
from devices import Device

logger = logging.getLogger('itl_mismatch_detector')
loop = asyncio.get_event_loop()

async def test_web_access(registered_devices: List[Device], max_parallel_connections:int = 30) -> List[Device]:
    """
    Verify the list of registered devices to check whether the web access is enabled or not

    :param registered_devices: the list of registered devices to test with
    :param max_parallel_connections: the number of connections to establish in parallel
    """

    session = aiohttp.ClientSession()
    registered_devices_after_checks = []

    test_connection_tasks = (is_web_enabled(session, device) for device in registered_devices)

    while True:
        parallel_tasks = list(islice(test_connection_tasks, max_parallel_connections))
        if not parallel_tasks:
            break

        done, pending = await asyncio.wait(parallel_tasks, loop=loop)

        for task in done:
            registered_devices_after_checks.append(task.result())

    session.close()

    return registered_devices_after_checks

async def is_web_enabled(session:aiohttp.ClientSession, device:Device) -> Device:
    """
    Attempt the connection to device web access to confirm that it's enabled or not

    :param session: active ClientSession
    :param device: device to use for test
    """

    logger.info('Testing device: %s %s', device.name, device.ip_address)
    print(f'Testing device: {device.name} {device.ip_address}')

    try:
        async with session.get(f'http://{device.ip_address}', timeout=30) as resp:
            if resp.status == 200:
                device.web_access = True
                return device
    except asyncio.TimeoutError:
            device.web_access = False
            return device
    except (aiohttp.ClientConnectionError,
                    aiohttp.ServerDisconnectedError,
                    aiohttp.ClientError):
        device.web_access = False
        return device

    device.web_access = False
    return device