# -*- coding: utf-8 -*-
"""
Created on Sun Jul 14 10:44:59 2024

@author: ardag
"""

import numpy as np
import matplotlib.pyplot as plt
from ultralytics import YOLO
import cv2
from .utils.auto_cc_norm_batch_log2 import log_autocorrelation_2D_torch
import torch


def object_detection_test(data, i, j, normalize1, normalize2, path_to_image, img_size=1024, conf_score=0.01, radius=15, save = False, s_txt = False, auto_cc = False, gauss=False, cm=False):
    # === Bounds check ===
    try:
        img = data[i, j, :, :]
    except IndexError:
        print(f"IndexError: i={i}, j={j} out of bounds for data shape {data.shape}")
        return None
    img= cv2.normalize(img, None, 0, normalize1, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    if auto_cc == True:
        #img = normalized_autocorrelation_2D_single(img)
        img = log_autocorrelation_2D_torch(img)
    img= cv2.normalize(img, None, 0, normalize2, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    img =  cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    img_x =cv2.bitwise_not(img)
    from importlib.resources import path
    from tempo4d import models  # assuming your weights are in data_processor/models
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    with path(models, "yolov8_weights.pt") as weights_path:
       model = YOLO(str(weights_path))

       model.to(device)
    
    # Run detection on the image
    results = model.predict(source=img_x, imgsz=img_size, conf=conf_score, max_det=100, iou=0.01, save_txt = s_txt)
    
    
    # Check if any detections were found
    if results[0].boxes.shape[0] == 0:
        print(f"No detections found for tile i={i}, j={j}")
        return None  # or return a placeholder / skip further processing
    # Get bounding boxes
    boxes = results[0].boxes
    bbox_xyxy = boxes.xyxy.tolist()
    #bbox_xywh = boxes.xywh.tolist()
    
    #bbox_xywh = xyxy2xywh(np.asarray(bbox_xyxy))
    # Convert bounding boxes from xyxy to xywh
    
    bbox_xywh = []
    for bbox in bbox_xyxy:
       x1, y1, x2, y2 = bbox

       x_center = ((x1+x2) / 2) - 0.5
       y_center = ((y1+y2) / 2) - 0.5
       width = x2 - x1
       height = y2 - y1
       bbox_xywh.append([x_center, y_center, width, height])
    
    bbox_xywh = np.array(bbox_xywh)
    
    if gauss == True:
        from fit_index_batch import custom_find_peaks
        coords = custom_find_peaks(img, bbox_xyxy, bbox_xywh, com=False, gfit=True)
    if cm == True:
        from fit_index_batch import custom_find_peaks
        coords = custom_find_peaks(img, bbox_xyxy, bbox_xywh, com=True, gfit=False)
    else:
        coords = bbox_xywh[:, :2]
    def show_points(coords, ax, marker_size=1):
        ax.scatter(coords[:, 0], coords[:, 1], color='red', marker='.', s=marker_size, edgecolor='white', linewidth=0)
        """
        for coord in coords:
            circle = plt.Circle(coord, radius, color='red', fill=False, linewidth=1.25)
            ax.add_patch(circle)
            """
    # Create a figure with two subplots
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 8))
    
    # Plot the object detection results on the first subplot
    #img= cv2.normalize(img, None, 0, 300, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    ax1.imshow(img)
    ax1.set_title('Pattern', fontsize=26, fontweight='bold')
    ax1.axis('off')
    
    ax2.imshow(img)
    for bbox in bbox_xywh:
        
        rect = plt.Rectangle((bbox[0] - (bbox[2] / 2) , bbox[1] - (bbox[3] / 2)), bbox[2], bbox[3], linewidth=2, edgecolor='red', facecolor='none')
        ax2.add_patch(rect)
    ax2.set_title('Detection', fontsize=26, fontweight='bold')
    ax2.axis('off')
    
    # Plot the points on the second subplot
    ax3.imshow(img)
    show_points(coords, ax3)
    #ax3.set_title('Center Points')
    ax3.axis('off')
    plt.tight_layout()
    
    if save == True:
        plt.imsave(path_to_image, img_x)
    
    plt.show()
    return coords




def plot_coordinates(coords_r, num_neighbors=1):
    """
    Find and visualize the nearest neighbors of the point closest to the centroid.

    Parameters:
    - coords_r: np.ndarray of shape (n, 2)
    - num_neighbors: int, number of nearest neighbors to find

    Returns:
    - selected_index: int
    - nearest_indices: np.ndarray
    - dspacing: np.ndarray
    """
    # === Validate input ===
    if coords_r is None or len(coords_r) == 0:
        print("No coordinates provided.")
        return None, None, None

    if len(coords_r) <= num_neighbors:
        print(f"Not enough points to find {num_neighbors} neighbors (only {len(coords_r)} available).")
        return None, None, None

    try:
        centroid = np.mean(coords_r, axis=0)
        distances_from_centroid = np.linalg.norm(coords_r - centroid, axis=1)
        selected_index = np.argmin(distances_from_centroid)
        selected_point = coords_r[selected_index]
        
        selected_distances = np.linalg.norm(coords_r - selected_point, axis=1)
        nearest_indices = np.argsort(selected_distances)[1:num_neighbors + 1]
        dspacing = selected_distances[nearest_indices]

        # === Plotting ===
        plt.scatter(coords_r[:, 0], coords_r[:, 1], color='blue', label='Original Points', alpha=0.5)
        plt.scatter(selected_point[0], selected_point[1], color='red', label='Selected Point')

        colors = plt.cm.turbo(np.linspace(0, 1, len(nearest_indices)))
        for idx, (neighbor_idx, color) in enumerate(zip(nearest_indices, colors)):
            px, py = coords_r[neighbor_idx]
            plt.scatter(px, py, color='yellow', label=f'Neighbor {idx+1}')
            plt.text(px + 6, py, str(idx), color=color, fontsize=14, weight='bold')

        plt.title('Centers', fontsize=22, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        plt.show()

        return selected_index, nearest_indices, dspacing

    except Exception as e:
        print(f"Error during coordinate processing: {e}")
        return None, None, None


