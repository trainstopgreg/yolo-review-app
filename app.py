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

cropped = image.crop((x, y, x + w, y + h))

# Top row: Class name and buttons
st.markdown(f"### Class: {class_names[int(class_id)]}")
col1, col2 = st.columns([1, 1])

yes_clicked = col1.button("✅ Yes - This is correct")
no_clicked = col2.button("❌ No - This is incorrect")

if yes_clicked:
    st.session_state.annotation_index += 1
    st.experimental_rerun()

if no_clicked:
    st.session_state.rejected.append({
        "image": os.path.basename(img_path),
        "class_id": int(class_id),
        "class_name": class_names[int(class_id)],
        "bbox": [x, y, w, h],
        "split": split
    })
    st.session_state.annotation_index += 1
    st.experimental_rerun()


with col2:
    if st.button("❌ No - This is incorrect"):
        st.session_state.rejected.append({
            "image": os.path.basename(img_path),
            "class_id": int(class_id),
            "class_name": class_names[int(class_id)],
            "bbox": [x, y, w, h],
            "split": split
        })
        st.session_state.annotation_index += 1
        st.experimental_rerun()

# Then show cropped image
st.image(cropped, width=350)

# Image and annotation count
st.markdown(f"**Image {st.session_state.image_index + 1} of {len(image_files)}**")
st.markdown(f"**Annotation {st.session_state.annotation_index + 1} of {len(lines)}**")

# Download rejected annotations
if st.session_state.rejected:
    rejected_json = json.dumps(st.session_state.rejected, indent=2)
    st.download_button(
        label="📥 Download rejected annotations",
        data=rejected_json,
        file_name="rejected_annotations.json",
        mime="application/json"
    )
