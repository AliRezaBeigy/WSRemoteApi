import asyncio
from RemoteAPIClient import RemoteAPIClient

async def main():
    client = RemoteAPIClient()
    print('Connecting...')
    await client.connect()

    print('Getting proxy object "sim"...')
    sim = await client.getObject('sim')

    print('Calling sim.getObject("/Floor")...')
    floor_object_getter = await sim.getObject('/Floor')

    print(f'Result: {floor_object_getter}')

    await client.close()

asyncio.run(main())
