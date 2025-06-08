import os
import streamlit as st
from PIL import Image
import cv2
import glob

st.set_page_config(page_title="YOLO Annotation Reviewer", layout="centered")

# Load class names
with open("classes.txt") as f:
    class_names = f.read().splitlines()

# Dataset split selection
split = st.selectbox("Select dataset split", ["train", "valid", "test"])

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

def crop_annotation(img, box, img_width, img_height):
    class_id, x, y, w, h = map(float, box)
    x1 = int((x - w / 2) * img_width)
    y1 = int((y - h / 2) * img_height)
    x2 = int((x + w / 2) * img_width)
    y2 = int((y + h / 2) * img_height)
    cropped = img[y1:y2, x1:x2]
    return cropped, int(class_id)

if st.session_state.image_index < len(image_files):
    img_path = image_files[st.session_state.image_index]
    label_path = label_files[st.session_state.image_index]

    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    height, width, _ = img.shape

    with open(label_path) as f:
        lines = f.read().splitlines()

    if lines:
        box_line = lines[st.session_state.annotation_index]
        cropped, class_id = crop_annotation(img, box_line.split(), width, height)
        cropped_pil = Image.fromarray(cropped)
        cropped_pil.thumbnail((400, 400))  # Resize for mobile

        st.image(cropped_pil, caption=f"{os.path.basename(img_path)}: Annotation {st.session_state.annotation_index + 1}/{len(lines)}")
        st.markdown(f"### Class: **{class_names[class_id]}**")

        feedback = st.radio("Is this annotation correct?", ["Yes", "No"], horizontal=True)

        if st.button("Next ▶️"):
            # Save result
            st.session_state.results.append({
                "image": os.path.basename(img_path),
                "annotation_index": st.session_state.annotation_index,
                "class": class_names[class_id],
                "response": feedback
            })

            # Move to next annotation
            st.session_state.annotation_index += 1
            if st.session_state.annotation_index >= len(lines):
                st.session_state.annotation_index = 0
                st.session_state.image_index += 1
else:
    st.write("✅ Review complete!")
    st.download_button("Download Results", data=str(st.session_state.results), file_name="annotation_review.txt")

