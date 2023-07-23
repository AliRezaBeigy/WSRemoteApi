import matplotlib.pyplot as plt
import asyncio
import numpy as np
import open3d as o3d
from wsRemoteApi.wsRemoteApi.RemoteAPIClient import RemoteAPIClient
from wsRemoteApi.wsRemoteApi.simConst import sim_object_visionsensor_type


async def main():
    w = 256
    h = w
    fx = 221.7
    fy = fx
    cx = 128
    cy = cx

    intrinsic = o3d.camera.PinholeCameraIntrinsic(w, h, fx, fy, cx, cy)
    intrinsic.intrinsic_matrix = [[fx, 0, cx], [0, fy, cy], [0, 0, 1]]
    cam_parameters = o3d.camera.PinholeCameraParameters()
    cam_parameters.intrinsic = intrinsic

    blank_pcd = o3d.io.read_point_cloud('single_cam_blank.ply')
    blank_z = np.array(blank_pcd.points)[:, 2][0]

    client = RemoteAPIClient()
    await client.connect()

    sim = await client.getObject('sim')

    cam_handler = await sim.getObjects(0, sim_object_visionsensor_type)

    await sim.startSimulation()

    depth = np.array((await sim.getVisionSensorDepthBuffer(cam_handler[0], 0, 0, 0, 0))[0])
    image, resolution = await sim.getVisionSensorImg(cam_handler[0])

    img = np.fromstring(image, np.uint8)
    img.resize([resolution[0], resolution[1], 3])
    depth.resize([resolution[0], resolution[1]])
    plt.subplot(323)
    plt.imshow(img)
    plt.title("Image")
    plt.subplot(324)
    plt.imshow(depth)
    plt.title("Depth")
    plt.show()

    rgb_img = o3d.geometry.RGBDImage.create_from_color_and_depth(
        o3d.geometry.Image(img),
        o3d.geometry.Image((depth).astype(np.float32)),
        convert_rgb_to_intensity=False
    )
    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgb_img, cam_parameters.intrinsic)

    dist = np.asarray(pcd.compute_point_cloud_distance(blank_pcd))
    pcd = pcd.select_by_index(np.where(dist > 0.0000000001)[0])

    pcd.scale(1 / blank_z, center=(0, 0, 0))

    point_cloud = np.asarray(pcd.points)
    pcd.estimate_normals()
    normals = np.asarray(pcd.normals)

    point_cloud_with_normals = np.concatenate((point_cloud, normals), axis=1)

    # o3d.io.write_point_cloud('test.ply', pcd)
    np.save('test.npy', point_cloud_with_normals)

    plt.close()
    await sim.stopSimulation()

    await client.close()


asyncio.run(main())
