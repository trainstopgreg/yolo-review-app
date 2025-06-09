import streamlit as st
from PIL import Image, ImageDraw
import os

# Function to load YOLO annotations
def load_yolo_annotations(file_content):
    annotations = []
    for line in file_content:
        parts = line.strip().split()
        if len(parts) == 5:
            cls, x_center, y_center, width, height = map(float, parts)
            annotations.append({
                'class': int(cls),
                'x_center': x_center,
                'y_center': y_center,
                'width': width,
                'height': height
            })
    return annotations

# Function to draw bounding boxes
def draw_bboxes(image, annotations):
    draw = ImageDraw.Draw(image)
    width, height = image.size
    for ann in annotations:
        x_c, y_c, w, h = ann['x_center'], ann['y_center'], ann['width'], ann['height']
        xmin = (x_c - w / 2) * width
        ymin = (y_c - h / 2) * height
        xmax = (x_c + w / 2) * width
        ymax = (y_c + h / 2) * height
        draw.rectangle([xmin, ymin, xmax, ymax], outline='red', width=2)
    return image

st.title("YOLO Annotation Viewer and Verifier")

uploaded_image = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
uploaded_ann = st.file_uploader("Upload YOLO Annotation", type=["txt"])

if uploaded_image and uploaded_ann:
    # Load image
    image = Image.open(uploaded_image).convert("RGB")
    # Read annotation file content
    ann_content = uploaded_ann.read().decode('utf-8')
    annotations = load_yolo_annotations(ann_content)
    # Draw bounding boxes
    image_with_bboxes = draw_bboxes(image.copy(), annotations)
    st.image(image_with_bboxes, caption="Image with Annotations")
    # Approve / Reject buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Verify"):
            st.success("Annotation verified.")
            # Save or process verification
    with col2:
        if st.button("Reject"):
            st.error("Annotation rejected.")
            # Save or process rejection
else:
    st.info("Please upload both an image and annotation file.")
