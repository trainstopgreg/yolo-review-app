import os
import streamlit as st
from PIL import Image
import glob
import json

st.set_page_config(page_title="YOLO Annotation Reviewer", layout="centered")

REJECTED_FILE = "rejected_annotations.jsonl"

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
if "stopped" not in st.session_state:
    st.session_state.stopped = False

# Load previously saved rejections from file on app start
if os.path.exists(REJECTED_FILE) and not st.session_state.rejected:
    with open(REJECTED_FILE, "r") as f:
        for line in f:
            try:
                ann = json.loads(line.strip())
                st.session_state.rejected.append(ann)
            except json.JSONDecodeError:
                pass

def save_rejection(annotation):
    with open(REJECTED_FILE, "a") as f:
        f.write(json.dumps(annotation) + "\n")

# Stop session button
if st.button("⏹ Stop Session and Review Rejected Annotations"):
    st.session_state.stopped = True

# If stopped, show rejected annotations and download
if st.session_state.stopped:
    st.warning("Session stopped. You can review and download rejected annotations below.")
    if st.session_state.rejected:
        # Extract unique image file names with rejected annotations
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

# Advance indices to valid annotation before UI render
while True:
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

    label_path = label_files[st.session_state.image_index]
    with open(label_path) as f:
        lines = f.read().strip().splitlines()

    if st.session_state.annotation_index < len(lines):
        break  # valid annotation found, proceed to UI
    else:
        # No annotations left in this image, advance to next
        st.session_state.image_index += 1
        st.session_state.annotation_index = 0

# Load current image and annotation
img_path = image_files[st.session_state.image_index]
image = Image.open(img_path)
img_w, img_h = image.size

ann = lines[st.session_state.annotation_index]
class_id, x_center, y_center, w, h = map(float, ann.split())

# Convert YOLO bbox to pixel bbox
x = int((x_center - w / 2) * img_w)
y = int((y_center - h / 2) * img_h)
w = int(w * img_w)
h = int(h * img_h)

# Crop the annotation region
cropped = image.crop((x, y, x + w, y + h))

# Resize cropped image to max width 300px for mobile-friendly display
max_width = 300
w_cropped, h_cropped = cropped.size
if w_cropped > max_width:
    new_height = int(h_cropped * max_width / w_cropped)
    resized_cropped = cropped.resize((max_width, new_height))
else:
    resized_cropped = cropped

# Display class and buttons at the top
st.markdown(f"## Class: `{class_names[int(class_id)]}`")
col1, col2 = st.columns(2)
yes_clicked = col1.button("✅ Yes - Correct")
no_clicked = col2.button("❌ No - Incorrect")

# Show cropped image
st.image(resized_cropped, caption=f"{class_names[int(class_id)]}", use_container_width=False)

# Show progress
st.markdown(f"Image {st.session_state.image_index + 1} of {len(image_files)}")
st.markdown(f"Annotation {st.session_state.annotation_index + 1} of {len(lines)}")

# Handle user input and advance annotation index
if yes_clicked or no_clicked:
    if no_clicked:
        annotation = {
            "image": os.path.basename(img_path),
            "class_id": int(class_id),
            "class_name": class_names[int(class_id)],
            "bbox": [x, y, w, h],
            "split": split
        }
        st.session_state.rejected.append(annotation)
        save_rejection(annotation)
        st.write(f"Rejected count: {len(st.session_state.rejected)}")

    st.session_state.annotation_index += 1
    st.rerun()
