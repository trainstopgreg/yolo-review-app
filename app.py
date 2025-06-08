import os
import streamlit as st
from PIL import Image
import glob
import zipfile

st.set_page_config(page_title="YOLO Annotation Reviewer", layout="centered")

# Custom CSS for hover effects and layout
st.markdown("""
    <style>
    .button-row {
        display: flex;
        justify-content: center;
        gap: 1rem;
        flex-wrap: wrap;
    }
    .yes-button button:hover {
        border-color: green !important;
        color: green !important;
    }
    .no-button button:hover {
        border-color: red !important;
        color: red !important;
    }
    </style>
""", unsafe_allow_html=True)

# Load class names
with open("classes.txt") as f:
    class_names = f.read().splitlines()

# Horizontal layout for dataset split selector
col1, col2 = st.columns([1, 3])
with col1:
    st.write("### Select dataset split")
with col2:
    split = st.selectbox("", ["train", "valid", "test"])

# Paths based on selected split
image_files = sorted(glob.glob(f"dataset/{split}/images/*.jpg"))
label_files = sorted(glob.glob(f"dataset/{split}/labels/*.txt"))

# Session state
if "image_index" not in st.session_state:
    st.session_state.image_index = 0
if "annotation_index" not in st.session_state:
    st.session_state.annotation_index = 0
if "results" not in st.session_state:
    st.session_state.results = []

# Function to get current annotation
def get_current_annotation():
    img_path = image_files[st.session_state.image_index]
    label_path = label_files[st.session_state.image_index]
    with open(label_path) as f:
        annotations = f.read().strip().splitlines()

    if not annotations:
        return None, None, None

    ann = annotations[st.session_state.annotation_index]
    class_id, x_center, y_center, width, height = map(float, ann.split())
    class_name = class_names[int(class_id)]

    image = Image.open(img_path)
    img_width, img_height = image.size
    left = int((x_center - width / 2) * img_width)
    top = int((y_center - height / 2) * img_height)
    right = int((x_center + width / 2) * img_width)
    bottom = int((y_center + height / 2) * img_height)
    cropped = image.crop((left, top, right, bottom))
    return cropped, class_name, img_path

# Stop session
if st.button("Stop Session"):
    st.session_state.stopped = True
    if st.session_state.results:
        rejected = [r for r in st.session_state.results if r["accepted"] is False]
        if rejected:
            with zipfile.ZipFile("rejected_annotations.zip", "w") as zipf:
                for r in rejected:
                    zipf.write(r["image"])
            st.markdown("### Rejected Annotations")
            for r in rejected:
                st.text(os.path.basename(r["image"]))
            with open("rejected_annotations.zip", "rb") as f:
                st.download_button("Download Rejected Annotations", f, "rejected_annotations.zip")
    st.stop()

# End of images
if st.session_state.image_index >= len(image_files):
    st.write("## All annotations reviewed!")
    st.stop()

# Display current cropped annotation
cropped, class_name, img_path = get_current_annotation()
if cropped:
    st.image(cropped, caption=os.path.basename(img_path), use_container_width=True)

    # Buttons and class display
    st.markdown('<div class="button-row">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Yes", key="yes"):
            st.session_state.results.append({"image": img_path, "class": class_name, "accepted": True})
            st.session_state.annotation_index += 1
            st.rerun()
    with col2:
        if st.button("No", key="no"):
            st.session_state.results.append({"image": img_path, "class": class_name, "accepted": False})
            st.session_state.annotation_index += 1
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"### Class: `{class_name}`")

    # Load next annotation or image
    label_path = label_files[st.session_state.image_index]
    with open(label_path) as f:
        annotations = f.read().strip().splitlines()

    if st.session_state.annotation_index >= len(annotations):
        st.session_state.annotation_index = 0
        st.session_state.image_index += 1
        st.rerun()

# Progress stats
st.markdown("---")
st.write(f"Progress: Image {st.session_state.image_index + 1} of {len(image_files)}")
