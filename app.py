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

# Load images and labels
image_files = sorted(glob.glob(f"dataset/{split}/images/*.jpg"))
label_files = sorted(glob.glob(f"dataset/{split}/labels/*.txt"))

# Initialize session state
if "image_index" not in st.session_state:
    st.session_state.image_index = 0
if "annotation_index" not in st.session_state:
    st.session_state.annotation_index = 0
if "rejected" not in st.session_state:
    st.session_state.rejected = []

# End of images check
if st.session_state.image_index >= len(image_files):
    st.success("✅ Review complete. No more images.")
    if st.session_state.rejected:
        st.download_button(
            "📥 Download rejected annotations",
            data=json.dumps(st.session_state.rejected, indent=2),
            file_name="rejected_annotations.json",
            mime="application/json"
        )
    st.stop()

# Load current image and annotations
img_path = image_files[st.session_state.image_index]
label_path = label_files[st.session_state.image_index]
image = Image.open(img_path)
img_w, img_h = image.size

with open(label_path) as f:
    lines = f.read().strip().splitlines()

# No annotations
if not lines:
    st.session_state.image_index += 1
    st.session_state.annotation_index = 0
    st.experimental_rerun()

# Move to next image if annotations exhausted
if st.session_state.annotation_index >= len(lines):
    st.session_state.image_index += 1
    st.session_state.annotation_index = 0
    st.experimental_rerun()

# Get annotation
ann = lines[st.session_state.annotation_index]
class_id, x_center, y_center, w, h = map(float, ann.split())

# Convert to pixels
x = int((x_center - w / 2) * img_w)
y = int((y_center - h / 2) * img_h)
w = int(w * img_w)
h = int(h * img_h)

# Crop
cropped = image.crop((x, y, x + w, y + h))

# Resize cropped image to max width 300px for mobile
max_width = 300
w_cropped, h_cropped = cropped.size
if w_cropped > max_width:
    new_height = int(h_cropped * max_width / w_cropped)
    resized_cropped = cropped.resize((max_width, new_height))
else:
    resized_cropped = cropped

# Display class name and buttons at the top
st.markdown(f"## Class: `{class_names[int(class_id)]}`")
col1, col2 = st.columns(2)

yes_clicked = col1.button("✅ Yes - Correct")
no_clicked = col2.button("❌ No - Incorrect")

# Show cropped annotation image
st.image(cropped, caption=f"{class_names[int(class_id)]}", use_container_width=True)

# Track annotation count
st.markdown(f"Image {st.session_state.image_index + 1} of {len(image_files)}")
st.markdown(f"Annotation {st.session_state.annotation_index + 1} of {len(lines)}")

# Handle button clicks
if yes_clicked or no_clicked:
    if no_clicked:
        st.session_state.rejected.append({
            "image": os.path.basename(img_path),
            "class_id": int(class_id),
            "class_name": class_names[int(class_id)],
            "bbox": [x, y, w, h],
            "split": split
        })
    st.session_state.annotation_index += 1
    st.rerun()
