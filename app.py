import streamlit as st
import io
from data_loader import get_dataset, load_image, load_annotation
from PIL import Image

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

def get_annotation_crop(image, annotation):
    # Calculate bbox in resized image (390x390)
    class_id, x_center, y_center, box_width, box_height = annotation
    x_center, y_center = x_center * 390, y_center * 390
    box_width, box_height = box_width * 390, box_height * 390
    x1 = int(x_center - box_width / 2)
    y1 = int(y_center - box_height / 2)
    x2 = int(x_center + box_width / 2)
    y2 = int(y_center + box_height / 2)
    # Resize original image to 390x390
    resized_image = image.resize((390, 390))
    # Crop the bounding box area
    crop_box = (x1, y1, x2, y2)
    annotation_img = resized_image.crop(crop_box)
    return annotation_img

def main():
    st.set_page_config(page_title="YOLO Annotation Review", layout="wide")

    # Navigation to move through images
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

    # Load original image
    original_image = load_image(entry)
    # Load annotations
    annotations = load_annotation(entry)

    # Reset annotation index if changing images
    if st.session_state.last_image_index != idx:
        st.session_state.current_annotation_idx = 0
        st.session_state.last_image_index = idx

    if not annotations:
        st.write("No annotations for this image.")
        return

    max_ann_idx = len(annotations) - 1

    # Annotation navigation
    col_prev, col_next = st.columns([1, 1])
    with col_prev:
        if st.button("Previous Annotation"):
            st.session_state.current_annotation_idx = max(0, st.session_state.current_annotation_idx - 1)
    with col_next:
        if st.button("Next Annotation"):
            st.session_state.current_annotation_idx = min(max_ann_idx, st.session_state.current_annotation_idx + 1)

    ann_idx = st.session_state.current_annotation_idx
    annotation = annotations[ann_idx]

    # Get crop of annotation
    annotation_img = get_annotation_crop(original_image, annotation)

    # Display the cropped annotation image
    st.image(annotation_img, caption=f"Annotation {ann_idx + 1}", use_column_width=True)

    # Flagging
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
