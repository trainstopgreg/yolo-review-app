import streamlit as st
import numpy as np
import io
from data_loader import get_dataset, load_image, load_annotation

# Load dataset once
dataset = get_dataset()
total_imgs = len(dataset)

# Initialize session state
if 'current_image_index' not in st.session_state:
    st.session_state.current_image_index = 0
if 'flagged_items' not in st.session_state:
    st.session_state.flagged_items = {}
if 'current_annotation_idx' not in st.session_state:
    st.session_state.current_annotation_idx = 0
if 'last_image_index' not in st.session_state:
    st.session_state.last_image_index = -1

def draw_single_annotation_on_resized_image(image, annotation):
    from PIL import ImageDraw
    # Resize image
    resized_image = image.resize((390, 390))
    draw = ImageDraw.Draw(resized_image)
    class_id, x_center, y_center, box_width, box_height = annotation
    # Scale coords to resized image
    x_center, y_center = x_center * 390, y_center * 390
    box_width, box_height = box_width * 390, box_height * 390
    x1 = int(x_center - box_width / 2)
    y1 = int(y_center - box_height / 2)
    x2 = int(x_center + box_width / 2)
    y2 = int(y_center + box_height / 2)
    draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
    draw.text((x1, y1 - 10), f"Class: {class_id}", fill="red")
    return resized_image

def main():
    st.set_page_config(page_title="YOLO Annotation Review", layout="wide")
    # Navigation for images
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("◀️ Previous", use_container_width=True):
            st.session_state.current_image_index = max(0, st.session_state.current_image_index - 1)
    with col2:
        st.write(f"Image {st.session_state.current_image_index + 1} / {total_imgs}")
    with col3:
        if st.button("Next ▶️", use_container_width=True):
            st.session_state.current_image_index = min(total_imgs - 1, st.session_state.current_image_index + 1)

    idx = st.session_state.current_image_index
    entry = dataset[idx]

    # Load image and annotations
    image = load_image(entry)
    annotations = load_annotation(entry)

    # Handle annotation index reset when switching images
    if st.session_state.last_image_index != idx:
        st.session_state.current_annotation_idx = 0
        st.session_state.last_image_index = idx

    # If no annotations, inform and exit
    if not annotations:
        st.write("No annotations for this image.")
        return

    max_ann_idx = len(annotations) - 1

    # Navigation for annotations
    col_prev, col_next = st.columns([1, 1])
    with col_prev:
        if st.button("Previous Annotation"):
            st.session_state.current_annotation_idx = max(0, st.session_state.current_annotation_idx - 1)
    with col_next:
        if st.button("Next Annotation"):
            st.session_state.current_annotation_idx = min(max_ann_idx, st.session_state.current_annotation_idx + 1)

    ann_idx = st.session_state.current_annotation_idx
    annotation = annotations[ann_idx]

    # Draw only current annotation on resized image
    img_with_box = draw_single_annotation_on_resized_image(image, annotation)

    # Show the image
    st.image(img_with_box, use_container_width=True)

    # Flag for current annotation
    flag_key = f"{idx}_ann_{ann_idx}"
    if st.checkbox("Flag this annotation for review", key=flag_key):
        if idx not in st.session_state.flagged_items:
            st.session_state.flagged_items[idx] = []
        if ann_idx not in st.session_state.flagged_items[idx]:
            st.session_state.flagged_items[idx].append(ann_idx)
            st.success("Annotation flagged!")

    # Show flagged items
    with st.expander("Flagged Items"):
        flagged = st.session_state.flagged_items
        if flagged:
            for img_idx, flags in flagged.items():
                if flags == "entire_image":
                    st.write(f"Image {img_idx + 1} flagged.")
                else:
                    st.write(f"Image {img_idx + 1} has annotations flagged: {', '.join(map(str, flags))}")
        else:
            st.write("No items have been flagged yet.")

if __name__ == "__main__":
    main()
