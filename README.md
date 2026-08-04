# Panoramic VR Camera Pipeline

A custom computer vision and 3D rendering pipeline that seamlessly combines multiple wide-angle video feeds into a single, undistorted panoramic VR experience.

## Overview

Building a custom VR camera rig presents a major software challenge: mathematically aligning and stitching multiple camera angles while avoiding the extreme distortion common in panoramic video. 

This project solves that by splitting the workflow into a highly optimized Python computer vision backend, and a high-performance Unity VR frontend.

### Features
* **SIFT Feature Extraction & Homography:** Uses OpenCV and SIFT (Scale-Invariant Feature Transform) to analyze microscopic feature points across multiple camera feeds. RANSAC is used to calculate robust Homography matrices to mathematically warp and align the perspectives.
* **Dynamic Cropping:** Fixes the "batwing" distortion common in panoramic stitching by dynamically calculating the pure rectangular bounding box of the overlapped frames. This produces a flawless `17:1` ultra-wide cinematic strip.
* **Procedural 3D Mesh Generation (Unity):** Includes custom C# scripts that procedurally generate a cap-less, 180-degree curved 3D mesh inside Unity perfectly mapped to the video's aspect ratio.
* **VR Head Tracking:** Includes an axis-clamped `MouseLook` controller to simulate VR head tracking on desktop, preventing users from looking past the physical bounds of the curved screen.

## Project Structure
* `/Python/` - Contains the core `hybrid_stitcher.py` script for processing video feeds.
* `/UnityScripts/` - Contains the C# scripts (`AutoDrive.cs`, `CurvedScreen.cs`, `MouseLook.cs`) to drop into your Unity VR project.
* `/SampleData/` - Contains sample left, center, and right camera footage from a virtual simulated rig, plus the stitched output.

## How to use the Python Stitcher
1. Place your 3 synchronized video feeds into the `SampleData` folder (named `left.mp4`, `center.mp4`, `right.mp4`).
2. Run `python hybrid_stitcher.py`.
3. The script will calculate the homography on the first frame, lock the matrices, and process the rest of the video, outputting `stitched_result.avi`.

## How to use the Unity Frontend
1. Import the C# scripts into your Unity project (Built-in or URP).
2. Attach `CurvedScreen.cs` to an Empty GameObject to generate the screen mesh.
3. Apply a Video Player component with an Unlit material to the screen, and load the stitched video.
4. Attach `MouseLook.cs` to your Main Camera to enable tracking.
