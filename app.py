import streamlit as st
import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
from PIL import Image

def load_image(image_file):
    img = Image.open(image_file)
    return np.array(img)

def load_annotations(annotation_file):
    with open(annotation_file, 'r') as f:
        lines = f.readlines()
    return [line.strip().split() for line in lines]

def draw_annotations(image, annotations, class_names):
    img_height, img_width = image.shape[:2]
    for ann in annotations:
        class_id, x_center, y_center, width, height = map(float, ann)
        x_center, y_center, width, height = x_center * img_width, y_center * img_height, width * img_width, height * img_height
        x1, y1 = int(x_center - width / 2), int(y_center - height / 2)
        x2, y2 = int(x_center + width / 2), int(y_center + height / 2)
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(image, class_names[int(class_id)], (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    return image

st.title("YOLO Dataset Annotation Reviewer")

# Step 1: File upload
image_file = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])
annotation_file = st.file_uploader("Upload Annotation File", type=['txt'])

if image_file is not None and annotation_file is not None:
    # Step 2: Image display
    image = load_image(image_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Step 3: Annotation visualization
    annotations = load_annotations(annotation_file)
    class_names = ['class1', 'class2', 'class3']  # Replace with your actual class names
    annotated_image = draw_annotations(image.copy(), annotations, class_names)
    st.image(annotated_image, caption="Annotated Image", use_column_width=True)

    # Step 4: Verification interface
    st.write("Annotations:")
    for idx, ann in enumerate(annotations):
        class_id, x_center, y_center, width, height = ann
        st.write(f"Object {idx + 1}: Class {class_names[int(class_id)]}, Center: ({x_center}, {y_center}), Size: ({width}, {height})")

    if st.button("Verify Annotations"):
        st.success("Annotations verified!")
    if st.button("Flag for Review"):
        st.warning("Image flagged for review.")
