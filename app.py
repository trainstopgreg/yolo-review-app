import streamlit as st
import numpy as np

try:
    import cv2
    USE_CV2 = True
except ImportError:
    from PIL import Image, ImageDraw, ImageFont
    USE_CV2 = False

import json
import io
import os
from PIL import Image

# Paths
images_dir = os.path.join("dataset", "train", "images")
labels_dir = os.path.join("dataset", "train", "labels")

# Build dataset list
image_files = [f for f in os.listdir(images_dir) if f.endswith('.jpg')]
dataset = []

for img_filename in image_files:
    base_name = os.path.splitext(img_filename)[0]
    label_filename = base_name + ".txt"  # adjust if using different formats
    dataset.append({
        'image_path': os.path.join(images_dir, img_filename),
        'label_path': os.path.join(labels_dir, label_filename),
        'filename': img_filename
    })

def draw_bounding_boxes(image, annotations):
    if USE_CV2:
        img = image.copy()
        height, width = img.shape[:2]
        for ann in annotations:
            # Convert YOLO format to pixel coordinates
            class_id, x_center, y_center, box_width, box_height = ann
            x_center, y_center, box_width, box_height = x_center * width, y_center * height, box_width * width, box_height * height
            x1 = int(x_center - box_width / 2)
            y1 = int(y_center - box_height / 2)
            x2 = int(x_center + box_width / 2)
            y2 = int(y_center + box_height / 2)
            
            # Draw rectangle on image
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, f"Class: {class_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        return img
    else:
        draw = ImageDraw.Draw(image)
        width, height = image.size
        for ann in annotations:
            # Convert YOLO format to pixel coordinates
            class_id, x_center, y_center, box_width, box_height = ann
            x_center, y_center, box_width, box_height = x_center * width, y_center * height, box_width * width, box_height * height
            x1 = int(x_center - box_width / 2)
            y1 = int(y_center - box_height / 2)
            x2 = int(x_center + box_width / 2)
            y2 = int(y_center + box_height / 2)
            
            # Draw rectangle on image
            draw.rectangle([x1, y1, x2, y2], outline="green", width=2)
            draw.text((x1, y1 - 10), f"Class: {class_id}", fill="green")
        return image

def main():
    st.set_page_config(page_title="YOLO Annotation Review", layout="wide")
    total_imgs = len(dataset)

    if 'current_image_index' not in st.session_state:
        st.session_state.current_image_index = 0
    if 'flagged_items' not in st.session_state:
        st.session_state.flagged_items = {}

    # Navigation controls
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("◀️ Previous", use_container_width=True):
            st.session_state.current_image_index = max(0, st.session_state.current_image_index - 1)
    with col2:
        st.text(f"Image {st.session_state.current_image_index + 1} / {total_imgs}")
    with col3:
        if st.button("Next ▶️", use_container_width=True):
            st.session_state.current_image_index = min(total_imgs - 1, st.session_state.current_image_index + 1)

    idx = st.session_state.current_image_index
    entry = dataset[idx]

    # Load image
    image = Image.open(entry['image_path'])
    # Load annotations
    annotations = load_annotation(entry)

    # Draw bounding boxes
    image_with_boxes = draw_bounding_boxes(image, annotations)

    # Display image
    buf = io.BytesIO()
    image_with_boxes.save(buf, format="PNG")
    st.image(buf.getvalue(), use_column_width=True)

    # Flag entire image
    if st.button("🚩 Flag Entire Image"):
        st.session_state.flagged_items[idx] = "entire_image"
        st.success("Image flagged!")

    # View and flag annotations
    with st.expander("View Annotations"):
        for ann_idx, ann in enumerate(annotations):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text(f"Class: {ann[0]}, Coords: {ann[1:]}")
            with col2:
                if st.checkbox("Flag", key=f"{idx}_ann_{ann_idx}"):
                    if idx not in st.session_state.flagged_items:
                        st.session_state.flagged_items[idx] = []
                    st.session_state.flagged_items[idx].append(ann_idx)
                    st.success(f"Annotation {ann_idx} flagged!")

    # Show flagged items
    with st.expander("Flagged Items"):
        if st.session_state.flagged_items:
            for img_idx, flags in st.session_state.flagged_items.items():
                if flags == "entire_image":
                    st.write(f"Image {img_idx + 1} flagged.")
                else:
                    st.write(f"Image {img_idx + 1} annotations flagged: {', '.join(map(str, flags))}")
        else:
            st.write("No items have been flagged yet.")



if __name__ == "__main__":
    main()








