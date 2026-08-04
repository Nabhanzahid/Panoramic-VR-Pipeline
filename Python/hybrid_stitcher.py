import cv2
import numpy as np
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("Phase 1: AI Homography Calculation on Frame 1...")

cap_l = cv2.VideoCapture('../SampleData/left.mp4')
cap_f = cv2.VideoCapture('../SampleData/center.mp4')
cap_r = cv2.VideoCapture('../SampleData/right.mp4')

ret_l, img_l = cap_l.read()
ret_f, img_f = cap_f.read()
ret_r, img_r = cap_r.read()

if not (ret_l and ret_f and ret_r):
    print("Error: Could not read first frames.")
    exit(1)

gray_l = cv2.cvtColor(img_l, cv2.COLOR_BGR2GRAY)
gray_f = cv2.cvtColor(img_f, cv2.COLOR_BGR2GRAY)
gray_r = cv2.cvtColor(img_r, cv2.COLOR_BGR2GRAY)

sift = cv2.SIFT_create()

kp_l, des_l = sift.detectAndCompute(gray_l, None)
kp_f, des_f = sift.detectAndCompute(gray_f, None)
kp_r, des_r = sift.detectAndCompute(gray_r, None)

FLANN_INDEX_KDTREE = 1
index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
search_params = dict(checks=50)
flann = cv2.FlannBasedMatcher(index_params, search_params)

def get_homography(des_src, des_dst, kp_src, kp_dst):
    matches = flann.knnMatch(des_src, des_dst, k=2)
    good = []
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good.append(m)
            
    if len(good) > 10:
        src_pts = np.float32([kp_src[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp_dst[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        
        # Calculate Homography with RANSAC
        H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        return H
    return None

# Find homography mapping left to front, and right to front
H_l = get_homography(des_l, des_f, kp_l, kp_f)
H_r = get_homography(des_r, des_f, kp_r, kp_f)

if H_l is None or H_r is None:
    print("Error: Could not find enough features to compute Homography.")
    exit(1)

print("Homography matrices successfully computed and locked!")

# Calculate bounding box of the final stitched image
h, w = img_f.shape[:2]

# Corners of left, front, right images
corners = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)

# Warp corners to find bounding box
warped_corners_l = cv2.perspectiveTransform(corners, H_l)
warped_corners_r = cv2.perspectiveTransform(corners, H_r)

# All corners in the stitched space
all_corners = np.concatenate((corners, warped_corners_l, warped_corners_r), axis=0)

[x_min, y_min] = np.int32(all_corners.min(axis=0).ravel() - 0.5)
[x_max, y_max] = np.int32(all_corners.max(axis=0).ravel() + 0.5)

# Global translation matrix to shift everything into positive coordinates
translation_dist = [-x_min, -y_min]
H_translation = np.array([
    [1, 0, translation_dist[0]],
    [0, 1, translation_dist[1]],
    [0, 0, 1]
], dtype=np.float32)

# Final adjusted matrices
H_l_final = H_translation.dot(H_l).astype(np.float32)
H_r_final = H_translation.dot(H_r).astype(np.float32)
H_f_final = H_translation

canvas_size = (int(x_max - x_min), int(y_max - y_min))
print(f"Internal Warp Canvas Size: {canvas_size}")

# Define the cropping boundaries (Y-axis only, bound to the center frame's height)
crop_y_start = int(-y_min)
crop_y_end = int(-y_min + h)
final_width = canvas_size[0]
final_height = h
final_canvas_size = (final_width, final_height)
print(f"Cropped Final Video Size: {final_canvas_size}")

fps = cap_f.get(cv2.CAP_PROP_FPS)
if fps == 0 or fps != fps: fps = 30.0

fourcc = cv2.VideoWriter_fourcc(*'MJPG')
out = cv2.VideoWriter('../SampleData/stitched_result.avi', fourcc, fps, final_canvas_size)

# Reset videos to beginning
cap_l.set(cv2.CAP_PROP_POS_FRAMES, 0)
cap_f.set(cv2.CAP_PROP_POS_FRAMES, 0)
cap_r.set(cv2.CAP_PROP_POS_FRAMES, 0)

print("\nPhase 2: Static Frame Application...", flush=True)
frame_count = 0

while True:
    ret_l, f_l = cap_l.read()
    ret_f, f_f = cap_f.read()
    ret_r, f_r = cap_r.read()
    
    if not (ret_l and ret_f and ret_r):
        break
        
    # Warp all three frames onto the global canvas
    warp_l = cv2.warpPerspective(f_l, H_l_final, canvas_size)
    warp_f = cv2.warpPerspective(f_f, H_f_final, canvas_size)
    warp_r = cv2.warpPerspective(f_r, H_r_final, canvas_size)
    
    # Merge them
    merged = np.maximum(warp_l, warp_f)
    merged = np.maximum(merged, warp_r)
    
    # Crop out the black voids vertically
    merged_cropped = merged[crop_y_start:crop_y_end, :]
    
    out.write(merged_cropped)
    frame_count += 1
    print(f"Warped and stitched frame {frame_count}...", end="\r", flush=True)

cap_l.release()
cap_f.release()
cap_r.release()
out.release()
print("\nDone! Saved stitched_hybrid.avi", flush=True)
