import cv2
import asyncio
import numpy as np
from RemoteAPIClient import RemoteAPIClient
from simConst import sim_object_visionsensor_type


async def main():
    client = RemoteAPIClient()
    await client.connect()

    sim = await client.getObject('sim')

    objects = await sim.getObjects(0, sim_object_visionsensor_type)

    await sim.startSimulation()

    while True:
        image, resolution = await sim.getVisionSensorImg(objects[0])

        img = np.fromstring(image, np.uint8)
        img.resize([resolution[0], resolution[1], 3])
        cv2.imshow('image', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    await sim.stopSimulation()

    await client.close()

asyncio.run(main())
