import streamlit as st
import cv2
import numpy as np
from PIL import Image
import json

# Assuming you have functions to load images and annotations
from data_loader import load_image, load_annotations, total_images

def draw_bounding_boxes(image, annotations):
    # Function to draw bounding boxes on the image
    for ann in annotations:
        # Convert YOLO format to pixel coordinates
        # Draw rectangle on image
    return image

def main():
    st.set_page_config(page_title="YOLO Annotation Review", layout="wide")

    st.title("YOLO Annotation Review")

    # Session state to keep track of current image and flagged items
    if 'current_image' not in st.session_state:
        st.session_state.current_image = 0
        st.session_state.flagged_items = {}

    # Navigation
    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        if st.button("◀️ Previous"):
            st.session_state.current_image = max(0, st.session_state.current_image - 1)
    with col2:
        st.text(f"Image {st.session_state.current_image + 1} / {total_images}")
    with col3:
        if st.button("Next ▶️"):
            st.session_state.current_image = min(total_images - 1, st.session_state.current_image + 1)

    # Load and display image with annotations
    image = load_image(st.session_state.current_image)
    annotations = load_annotations(st.session_state.current_image)
    image_with_boxes = draw_bounding_boxes(image, annotations)
    
    st.image(image_with_boxes, use_column_width=True)

    # Flag entire image
    if st.button("🚩 Flag Entire Image"):
        st.session_state.flagged_items[st.session_state.current_image] = "entire_image"

    # Display and flag individual annotations
    with st.expander("View Annotations"):
        for idx, ann in enumerate(annotations):
            col1, col2 = st.columns([3,1])
            with col1:
                st.text(f"Class: {ann['class']}, Coords: {ann['bbox']}")
            with col2:
                if st.checkbox("Flag", key=f"flag_{idx}"):
                    if st.session_state.current_image not in st.session_state.flagged_items:
                        st.session_state.flagged_items[st.session_state.current_image] = []
                    st.session_state.flagged_items[st.session_state.current_image].append(idx)

    # Export flagged items
    if st.button("Export Flagged Items"):
        with open("flagged_items.json", "w") as f:
            json.dump(st.session_state.flagged_items, f)
        st.success("Flagged items exported successfully!")

if __name__ == "__main__":
    main()
