import os
import streamlit as st
from PIL import Image
import glob

# Streamlit config
st.set_page_config(page_title="YOLO Annotation Reviewer", layout="centered")

# Custom styles
st.markdown("""
<style>
button {
    border: 2px solid #ccc;
    padding: 0.5em 1em;
    font-size: 1.1em;
}

/* YES button (left) */
div[data-testid="column"] > div:nth-child(1) button {
    border-color: #28a745 !important;
    color: #28a745 !important;
}
div[data-testid="column"] > div:nth-child(1) button:hover {
    background-color: #28a745 !important;
    color: white !important;
    border-color: #28a745 !important;
}

/* NO button (right) */
div[data-testid="column"] > div:nth-child(2) button {
    border-color: #dc3545 !important;
    color: #dc3545 !important;
}
div[data-testid="column"] > div:nth-child(2) button:hover {
    background-color: #dc3545 !important;
    color: white !important;
    border-color: #dc3545 !important;
}
</style>
""", unsafe_allow_html=True)

# Load class names
with open("classes.txt") as f:
    class_names = f.read().splitlines()

# Dataset split selection
split = st.selectbox("Select dataset split", ["train", "valid", "test"])

# Load dataset paths
image_files = sorted(glob.glob(f"dataset/{split}/images/*.jpg"))
label_files = sorted(glob.glob(f"dataset/{split}/labels/*.txt"))

# Session state
if "image_index" not in st.session_state:
    st.session_state.image_index = 0
if "annotation_index" not in st.session_state:
    st.session_state.annotation_index = 0
if "results" not in st.session_state:
    st.session_state.results = []

# End condition
if st.session_state.image_index >= len(image_files):
    st.success("Review complete! Here are the rejected annotations:")
    rejected = [r for r in st.session_state.results if r["decision"] == "no"]
    for r in rejected:
        st.write(r["image"])
    if rejected:
        with open("rejected.txt", "w") as f:
            for r in rejected:
                f.write(f"{r['image']},{r['label']}\n")
        with open("rejected.txt", "rb") as f:
            st.download_button("Download Rejected Annotations", f, "rejected.txt")
    st.stop()

# Load current image and label
image_path = image_files[st.session_state.image_index]
label_path = label_files[st.session_state.image_index]

image = Image.open(image_path)
with open(label_path) as f:
    labels = f.read().splitlines()

if st.session_state.annotation_index >= len(labels):
    st.session_state.image_index += 1
    st.session_state.annotation_index = 0
    st.rerun()

annotation = labels[st.session_state.annotation_index]
parts = annotation.split()
class_id = int(parts[0])
class_name = class_names[class_id]

# Convert YOLO format to pixel box
img_w, img_h = image.size
x_center, y_center, w, h = map(float, parts[1:])
x1 = int((x_center - w / 2) * img_w)
y1 = int((y_center - h / 2) * img_h)
x2 = int((x_center + w / 2) * img_w)
y2 = int((y_center + h / 2) * img_h)

cropped = image.crop((x1, y1, x2, y2))
st.image(cropped, caption=os.path.basename(image_path), use_container_width=True)

# Buttons and class name
with st.form("annotation_form"):
    col1, col2 = st.columns([1, 1])
    with col1:
        yes_clicked = st.form_submit_button("✅ Yes")
    with col2:
        no_clicked = st.form_submit_button("❌ No")

    st.markdown(f"**Class:** {class_name}")

# Progress stats
st.write(f"Image {st.session_state.image_index + 1} of {len(image_files)}")
st.write(f"Annotation {st.session_state.annotation_index + 1} of {len(labels)}")

# Decision handling
if yes_clicked:
    st.session_state.results.append({
        "image": os.path.basename(image_path),
        "label": class_name,
        "decision": "yes"
    })
    st.session_state.annotation_index += 1
    st.rerun()

if no_clicked:
    st.session_state.results.append({
        "image": os.path.basename(image_path),
        "label": class_name,
        "decision": "no"
    })
    st.session_state.annotation_index += 1
    st.rerun()

# Stop session button
st.divider()
if st.button("⏹️ Stop Session"):
    st.success("Session stopped. Rejected annotations:")
    rejected = [r for r in st.session_state.results if r["decision"] == "no"]
    for r in rejected:
        st.write(r["image"])
    if rejected:
        with open("rejected.txt", "w") as f:
            for r in rejected:
                f.write(f"{r['image']},{r['label']}\n")
        with open("rejected.txt", "rb") as f:
            st.download_button("Download Rejected Annotations", f, "rejected.txt")
    st.stop()
