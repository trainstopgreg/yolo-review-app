import os
import streamlit as st
from PIL import Image
import glob
import json

st.set_page_config(page_title="YOLO Annotation Reviewer", layout="centered")

# Load class names
with open("classes.txt") as f:
    class_names = f.read().splitlines()

# Dataset split selection
split = st.selectbox("Select dataset split", ["train", "valid", "test"])

# Load image and label files
image_files = sorted(glob.glob(f"dataset/{split}/images/*.jpg"))
label_files = sorted(glob.glob(f"dataset/{split}/labels/*.txt"))

# Session state init
if "image_index" not in st.session_state:
    st.session_state.image_index = 0
if "annotation_index" not in st.session_state:
    st.session_state.annotation_index = 0
if "rejected" not in st.session_state:
    st.session_state.rejected = []

# Check if index is in bounds
if st.session_state.image_index >= len(image_files):
    st.write("No more images.")
    st.stop()

# Get current image and label file
img_path = image_files[st.session_state.image_index]
label_path = label_files[st.session_state.image_index]

# Load image
image = Image.open(img_path)
image_width, image_height = image.size

# Load annotations
with open(label_path) as f:
    lines = f.read().strip().splitlines()

if not lines:
    st.write("No annotations in this image.")
    st.session_state.image_index += 1
    st.session_state.annotation_index = 0
    st.experimental_rerun()

# Get current annotation
if st.session_state.annotation_index >= len(lines):
    st.session_state.image_index += 1
    st.session_state.annotation_index = 0
    st.experimental_rerun()

ann = lines[st.session_state.annotation_index]
class_id, x_center, y_center, w, h = map(float, ann.strip().split())

# Convert YOLO format to pixel bbox
x = int((x_center - w / 2) * image_width)
y = int((y_center - h / 2) * image_height)
w = int(w * image_width)
h = int(h * image_height)

cropped = im
