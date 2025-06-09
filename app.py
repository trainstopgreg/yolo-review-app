import streamlit as st
import numpy as np
import io
import os
from data_loader import get_dataset, load_image, load_annotation

# Load dataset once
dataset = get_dataset()
total_imgs = len(dataset)

# Initialize session state
if 'current_image_index' not in st.session_state:
    st.session_state.current_image_index = 0

if 'flagged_items' not in st.session_state:
    st.session_state.flagged_items = {}

def draw_bounding_boxes(image, annotations):
    from PIL import ImageDraw, ImageFont

    draw = ImageDraw.Draw(image)
    width, height = image.size
    for ann in annotations:
        class_id, x_center, y_center, box_width, box_height = ann
        x_center, y_center, box_width, box_height = x_center * width, y_center * height, box_width * width, box_height * height
        x1 = int(x_center - box_width / 2)
        y1 = int(y_center - box_height / 2)
        x2 = int(x_center + box_width / 2)
        y2 = int(y_center + box_height / 2)
        draw.rectangle([x1, y1, x2, y2], outline="green", width=2)
        draw.text((x1, y1 - 10), f"Class: {class_id}", fill="green")
    return image

def main():
    st.set_page_config(page_title="YOLO Annotation Review", layout="wide")

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

    # Load image and annotations
    image = load_image(entry)
    annotations = load_annotation(entry)

    # Draw bounding boxes
    image_with_boxes = draw_bounding_boxes(image.copy(), annotations)

    # Display image
    buf = io.BytesIO()
    image_with_boxes.save(buf, format="PNG")
    st.image(buf.getvalue(), use_column_width=True)

    # Initialize annotation index for this image if not present
    if 'current_annotation_idx' not in st.session_state or st.session_state.current_image_index != getattr(st.session_state, 'last_image_index', -1):
        st.session_state.current_annotation_idx = 0
        st.session_state.last_image_index = st.session_state.current_image_index

    # Reset annotation index when switching images
    st.session_state.last_image_index = st.session_state.current_image_index

    annotations = load_annotation(entry)

    # If no annotations, skip
    if not annotations:
        st.write("No annotations for this image.")
        return

    # Navigation for annotations
    if 'current_annotation_idx' not in st.session_state:
        st.session_state.current_annotation_idx = 0

    max_ann_idx = len(annotations) - 1

    col_prev, col_next = st.columns([1,1])
    with col_prev:
        if st.button("Previous Annotation"):
            st.session_state.current_annotation_idx = max(0, st.session_state.current_annotation_idx - 1)
    with col_next:
        if st.button("Next Annotation"):
            st.session_state.current_annotation_idx = min(max_ann_idx, st.session_state.current_annotation_idx + 1)

    ann_idx = st.session_state.current_annotation_idx
    ann = annotations[ann_idx]

    # Show current annotation details
    st.write(f"Annotation {ann_idx + 1} of {len(annotations)}")
    st.write(f"Class: {ann[0]}, Coords: {ann[1:]}")

    # Flag checkbox for the current annotation
    flag_key = f"{idx}_ann_{ann_idx}"
    if st.checkbox("Flag this annotation for review", key=flag_key):
        if idx not in st.session_state.flagged_items:
            st.session_state.flagged_items[idx] = []
        if ann_idx not in st.session_state.flagged_items[idx]:
            st.session_state.flagged_items[idx].append(ann_idx)
            st.success(f"Annotation {ann_idx + 1} flagged!")

    # Display flagged items info
    with st.expander("Flagged Items"):
        flagged = st.session_state.flagged_items
        if flagged:
            for img_idx, flags in flagged.items():
                if flags == "entire_image":
                    st.write(f"Image {img_idx + 1} flagged.")
                else:
                    st.write(f"Image {img_idx + 1} has annotations flagged: {', '.join(map(str, flags))}")
        else:
            st.write("No items have been flagged yet.")


if __name__ == "__main__":
    main()
