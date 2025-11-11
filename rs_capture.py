import pyrealsense2 as rs
import numpy as np
import cv2
import os
from datetime import datetime

img_h, img_w = 480, 640
saved_dataset = "../"
obj = "cola"

# ------------------------------------------------
#     Set the camera parameters
# ------------------------------------------------
# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

now = datetime.now()
timestamp = now.strftime("%Y-%m-%d-%H-%M-%S")

# data folder
dataset_folder = f"{saved_dataset}/{timestamp}_{obj}/"

depth_output_dir = f"{dataset_folder}/depth"
color_output_dir = f"{dataset_folder}/rgb"

os.makedirs(depth_output_dir, exist_ok=True)
os.makedirs(color_output_dir, exist_ok=True)

# Start streaming
pipeline.start(config)
align = rs.align(rs.stream.color)

# Get device product line for setting a supporting resolution
profile = pipeline.get_active_profile()

# Get the depth sensor's depth stream profile and extract intrinsic parameters
color_stream = profile.get_stream(rs.stream.color)
intrinsics = color_stream.as_video_stream_profile().get_intrinsics()
print(intrinsics)

fx, fy, cx, cy = intrinsics.fx, intrinsics.fy, intrinsics.ppx, intrinsics.ppy
cam_K = np.array([[fx, 0, cx],
                  [0, fy, cy],
                  [0, 0, 1]])

# save to txt
np.savetxt(os.path.join(dataset_folder, 'cam_K.txt'), cam_K, fmt='%f')

index = 0
start = False
try:
    while True:
        frames = pipeline.wait_for_frames()
        aligned_frames = align.process(frames)

        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        if not depth_frame or not color_frame:
            continue
        
        # Convert images to numpy arrays
        depth_img = np.asanyarray(depth_frame.get_data())
        rgb_img = np.asanyarray(color_frame.get_data())
        
        if start:
            index += 1
            print(f"save the {index} frame")
            cv2.imwrite(os.path.join(depth_output_dir, f'{index:05d}.png'), depth_img)
            cv2.imwrite(os.path.join(color_output_dir, f'{index:05d}.png'), rgb_img)

        cv2.imshow("rgb", rgb_img)

        # viz depth image using jet color
        depth_clipped = np.clip(depth_img, 0, 1000)
        depth_normalized = cv2.normalize(depth_clipped, None, 0, 255, cv2.NORM_MINMAX)
        depth_normalized = np.uint8(depth_normalized)
        depth_colormap = cv2.applyColorMap(depth_normalized, cv2.COLORMAP_JET)
        cv2.imshow("depth", depth_colormap)

        key_num = cv2.waitKey(30)
        if key_num == ord('q'):
            print("q pressed. close the program.")
            break
        if key_num == ord('c'):
            print("c pressed. start to save the rgb-d data.")
            start = True
        if key_num == ord('s'):
            print("s pressed. stop to save the rgb-d data.")
            start = False
        # if key_num == ord('c'):
        #     index += 1
        #     print("c pressed. save the rgb image.")
        #     cv2.imwrite(os.path.join(depth_output_dir, f'{index:05d}.png'), depth_img)
        #     cv2.imwrite(os.path.join(color_output_dir, f'{index:05d}.png'), rgb_img)
finally:
    # 停止管道
    pipeline.stop()
    cv2.destroyAllWindows()
# pipeline.stop()