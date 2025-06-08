import os
import json
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

# Session state initialization
if "image_index" not in st.session_state:
    st.session_state.image_index = 0
if "annotation_index" not in st.session_state:
    st.session_state.annotation_index = 0
if "results" not in st.session_state:
    st.session_state.results = []
if "rejected" not in st.session_state:
    st.session_state.rejected = []
if "stopped" not in st.session_state:
    st.session_state.stopped = False

def save_rejection(annotation):
    # Append to a json file for rejected annotations
    rejected_file = "rejected_annotations.json"
    if os.path.exists(rejected_file):
        with open(rejected_file, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(annotation)
    with open(rejected_file, "w") as f:
        json.dump(data, f, indent=2)

def read_annotations(label_path):
    with open(label_path, "r") as f:
        lines = f.read().strip().split("\n")
    annotations = []
    for line in lines:
        parts = line.split()
        if len(parts) == 5:
            class_id, x, y, w, h = parts
            annotations.append({
                "class_id": int(class_id),
                "x": float(x),
                "y": float(y),
                "w": float(w),
                "h": float(h),
            })
    return annotations

def crop_annotation(image, ann):
    h, w, _ = image.shape
    cx = int(ann["x"] * w)
    cy = int(ann["y"] * h)
    bw = int(ann["w"] * w)
    bh = int(ann["h"] * h)

    x1 = max(cx - bw // 2, 0)
    y1 = max(cy - bh // 2, 0)
    x2 = min(cx + bw // 2, w)
    y2 = min(cy + bh // 2, h)

    cropped = image[y1:y2, x1:x2]
    return cropped

if st.session_state.stopped:
    st.warning("Session stopped. You can review and download rejected annotations below.")
    if st.session_state.rejected:
        rejected_images = sorted(set(item["image"] for item in st.session_state.rejected))
        st.markdown("### Rejected annotations from these images:")
        for img_name in rejected_images:
            st.write(f"- {img_name}")

        st.download_button(
            "📥 Download rejected annotations",
            data=json.dumps(st.session_state.rejected, indent=2),
            file_name="rejected_annotations.json",
            mime="application/json"
        )
    else:
        st.info("No rejected annotations recorded.")
    st.stop()

if st.session_state.image_index >= len(image_files):
    st.success("🎉 You have reviewed all images!")
    st.stop()

img_path = image_files[st.session_state.image_index]
label_path = label_files[st.session_state.image_index]

image = cv2.imread(img_path)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

annotations = read_annotations(label_path)
if st.session_state.annotation_index >= len(annotations):
    # Move to next image
    st.session_state.image_index += 1
    st.session_state.annotation_index = 0
    st.experimental_rerun()

ann = annotations[st.session_state.annotation_index]
cropped = crop_annotation(image, ann)

# Resize cropped image for mobile-friendly display (max width 300px)
pil_img = Image.fromarray(cropped)
max_width = 300
wpercent = (max_width / float(pil_img.size[0]))
hsize = int((float(pil_img.size[1]) * float(wpercent)))
resized_cropped = pil_img.resize((max_width, hsize))

# Buttons side by side at top
col1, col2 = st.columns([1, 1], gap="small")
yes_clicked = col1.button("✅ Yes - Correct")
no_clicked = col2.button("❌ No - Incorrect")

# Class name below buttons
st.markdown(f"## Class: `{class_names[ann['class_id']]}`")

# Show cropped image below class name
st.image(resized_cropped, use_container_width=False)

if yes_clicked or no_clicked:
    if no_clicked:
        annotation = {
            "image": os.path.basename(img_path),
            "class_id": ann["class_id"],
            "class_name": class_names[ann["class_id"]],
            "bbox": [ann["x"], ann["y"], ann["w"], ann["h"]],
            "split": split
        }
        st.session_state.rejected.append(annotation)
        save_rejection(annotation)
        st.write(f"Rejected count: {len(st.session_state.rejected)}")

    st.session_state.annotation_index += 1
    st.rerun()

# Stop session button at bottom
st.markdown("---")
if st.button("⏹ Stop Session and Review Rejected Annotations"):
    st.session_state.stopped = True
    st.experimental_rerun()
