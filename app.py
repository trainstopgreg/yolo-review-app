import os
import glob
import streamlit as st
from PIL import Image

st.set_page_config(page_title="YOLO Annotation Reviewer", layout="centered")

# --- Load class names ---
with open("classes.txt") as f:
    class_names = f.read().splitlines()

# --- Select dataset split ---
split = st.selectbox("Dataset", ["train", "valid", "test"])

# --- Load image and label paths ---
image_files = sorted(glob.glob(f"dataset/{split}/images/*.jpg"))
label_files = sorted(glob.glob(f"dataset/{split}/labels/*.txt"))

# --- Initialize session state ---
if "image_index" not in st.session_state:
    st.session_state.image_index = 0
if "rejected" not in st.session_state:
    st.session_state.rejected = []

# --- Stop if all images are reviewed ---
if st.session_state.image_index >= len(image_files):
    st.header("Review Complete ✅")
    st.write("Rejected Annotations:")
    for item in st.session_state.rejected:
        st.text(item)
    st.download_button("Download Rejected List", data="\n".join(st.session_state.rejected), file_name="rejected.txt")
    st.stop()

# --- Load current image and annotation ---
image_path = image_files[st.session_state.image_index]
label_path = label_files[st.session_state.image_index]

img = Image.open(image_path)

# --- Parse annotation ---
with open(label_path) as f:
    annotations = [line.strip().split() for line in f.readlines()]

# --- Load annotation crop (first one only for now) ---
if annotations:
    class_id, x_center, y_center, w, h = map(float, annotations[0])
    class_id = int(class_id)
    class_name = class_names[class_id]

    width, height = img.size
    x = int((x_center - w/2) * width)
    y = int((y_center - h/2) * height)
    w = int(w * width)
    h = int(h * height)
    cropped = img.crop((x, y, x + w, y + h))
else:
    class_name = "No annotations"
    cropped = img

# --- Show custom buttons CSS ---
st.markdown("""
<style>
.custom-button {
    display: inline-block;
    padding: 12px 30px;
    font-size: 18px;
    border: 2px solid #ccc;
    border-radius: 10px;
    margin: 5px;
    cursor: pointer;
    transition: 0.3s;
    text-align: center;
}
.custom-yes:hover {
    border-color: green;
    color: green;
}
.custom-no:hover {
    border-color: red;
    color: red;
}
.button-row {
    display: flex;
    justify-content: center;
    gap: 20px;
    flex-wrap: wrap;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# --- Custom buttons ---
with st.form("annotation_form"):
    st.markdown(f"<div class='button-row'>\n    <button type='submit' name='response' value='yes' class='custom-button custom-yes'>✅ Yes</button>\n    <button type='submit' name='response' value='no' class='custom-button custom-no'>❌ No</button>\n    </div>", unsafe_allow_html=True)
    st.markdown(f"### `{class_name}`")
    st.image(cropped, caption=os.path.basename(image_path), use_container_width=True)
    response = st.form_submit_button()

# --- Handle response (requires workaround because HTML buttons don't return values directly) ---
if response:
    # Hack: Look at the query string to infer which button was clicked isn't possible here
    # For now, simulate based on hidden state
    # Assume NO if class_name is empty or not valid
    if class_name != "No annotations":
        # This would normally come from request context; here we add manual logic as placeholder
        if st.query_params.get("response") == "no":
            st.session_state.rejected.append(os.path.basename(label_path))

    st.session_state.image_index += 1
    st.rerun()

# --- Progress and stop session ---
st.markdown(f"### {st.session_state.image_index + 1} / {len(image_files)} reviewed")
if st.button("🚫 Stop Session"):
    st.header("Session Stopped")
    st.write("Rejected Annotations:")
    for item in st.session_state.rejected:
        st.text(item)
    st.download_button("Download Rejected List", data="\n".join(st.session_state.rejected), file_name="rejected.txt")
    st.stop()
