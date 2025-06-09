import streamlit as st
import cv2
import numpy as np
from PIL import Image
import json

# Assuming you have functions to load images and annotations
from data_loader import load_image, load_annotations, total_images

def draw_bounding_boxes(image, annotations):
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
        if st.button("◀️ Previous", use_container_width=True):
            st.session_state.current_image = max(0, st.session_state.current_image - 1)
    with col2:
        st.text(f"Image {st.session_state.current_image + 1} / {total_images}")
    with col3:
        if st.button("Next ▶️", use_container_width=True):
            st.session_state.current_image = min(total_images - 1, st.session_state.current_image + 1)

    # Load and display image with annotations
    image = load_image(st.session_state.current_image)
    annotations = load_annotations(st.session_state.current_image)
    image_with_boxes = draw_bounding_boxes(image, annotations)
    
    st.image(image_with_boxes, use_column_width=True)

    # Flag entire image
    if st.button("🚩 Flag Entire Image", use_container_width=True):
        st.session_state.flagged_items[st.session_state.current_image] = "entire_image"
        st.success("Image flagged!")

    # Display and flag individual annotations
    with st.expander("View Annotations"):
        for idx, ann in enumerate(annotations):
            col1, col2 = st.columns([3,1])
            with col1:
                st.text(f"Class: {ann[0]}, Coords: {ann[1:]}")
            with col2:
                if st.checkbox("Flag", key=f"flag_{idx}"):
                    if st.session_state.current_image not in st.session_state.flagged_items:
                        st.session_state.flagged_items[st.session_state.current_image] = []
                    if idx not in st.session_state.flagged_items[st.session_state.current_image]:
                        st.session_state.flagged_items[st.session_state.current_image].append(idx)
                        st.success(f"Annotation {idx} flagged!")
                else:
                    if st.session_state.current_image in st.session_state.flagged_items and idx in st.session_state.flagged_items[st.session_state.current_image]:
                        st.session_state.flagged_items[st.session_state.current_image].remove(idx)
                        st.info(f"Annotation {idx} unflagged.")

    # Export flagged items
    if st.button("Export Flagged Items", use_container_width=True):
        with open("flagged_items.json", "w") as f:
            json.dump(st.session_state.flagged_items, f)
        st.success("Flagged items exported successfully!")

    # Display current flagged items for this image
    if st.session_state.current_image in st.session_state.flagged_items:
        st.write("Flagged items for this image:")
        if st.session_state.flagged_items[st.session_state.current_image] == "entire_image":
            st.write("Entire image flagged")
        else:
            st.write(f"Flagged annotations: {st.session_state.flagged_items[st.session_state.current_image]}")

    # Add some custom CSS to improve mobile layout
    st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        height: 50px;
    }
    .stExpander {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()







