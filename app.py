import streamlit as st
import json

# Initialize session state for index and rejected list
if 'idx' not in st.session_state:
    st.session_state.idx = 0
if 'rejected' not in st.session_state:
    st.session_state.rejected = []

# Example annotations list (replace with your actual data)
annotations = [
    {"image_path": "img1.jpg", "class": "player"},
    {"image_path": "img2.jpg", "class": "ball"},
    {"image_path": "img3.jpg", "class": "referee"},
]

def next_annotation():
    if st.session_state.idx < len(annotations) - 1:
        st.session_state.idx += 1

def prev_annotation():
    if st.session_state.idx > 0:
        st.session_state.idx -= 1

def mark_no():
    current = annotations[st.session_state.idx]
    st.session_state.rejected.append(current)
    next_annotation()

# Show current annotation
current = annotations[st.session_state.idx]
st.write(f"Annotation {st.session_state.idx + 1} / {len(annotations)}")
st.write(f"Class: {current['class']}")
st.image(current['image_path'])  # Or however you load the image

# Buttons for yes/no
col1, col2, col3 = st.columns([1,1,1])
with col1:
    if st.button("Previous"):
        prev_annotation()
with col2:
    if st.button("Yes"):
        next_annotation()
with col3:
    if st.button("No"):
        mark_no()

# Show count of rejected annotations so far
st.write(f"Rejected annotations count: {len(st.session_state.rejected)}")

# Provide download button for rejected annotations JSON
if st.session_state.rejected:
    rejected_json = json.dumps(st.session_state.rejected, indent=2)
    st.download_button(
        label="Download rejected annotations JSON",
        data=rejected_json,
        file_name="rejected_annotations.json",
        mime="application/json"
    )

