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

def resize_with_padding(image, target_size=390):
    """
    Resize an image to fit within (target_size x target_size)
    maintaining aspect ratio, adding black bars if needed.
    """
    original_width, original_height = image.size
    aspect_ratio = original_width / original_height

    if aspect_ratio > 1:
        # Wider image
        new_width = target_size
        new_height = int(target_size / aspect_ratio)
    else:
        # Taller image
        new_height = target_size
        new_width = int(target_size * aspect_ratio)
    resized_img = image.resize((new_width, new_height), Image.ANTIALIAS)

    # Create black background
    new_img = Image.new("RGB", (target_size, target_size), (0, 0, 0))
    # Center the resized image
    paste_x = (target_size - new_width) // 2
    paste_y = (target_size - new_height) // 2
    new_img.paste(resized_img, (paste_x, paste_y))
    return new_img

def get_annotation_crop(image, annotation):
    # Calculate bbox coordinates in the resized image (390x390)
    class_id, x_center, y_center, box_width, box_height = annotation
    x_center, y_center = x_center * 390, y_center * 390
    box_width, box_height = box_width * 390, box_height * 390
    x1 = int(x_center - box_width / 2)
    y1 = int(y_center - box_height / 2)
    x2 = int(x_center + box_width / 2)
    y2 = int(y_center + box_height / 2)

    # Resize original image to 390x390
    resized_image = image.resize((390, 390))
    # Crop the annotation area
    crop_box = (x1, y1, x2, y2)
    annotation_img = resized_image.crop(crop_box)
    # Resize annotation crop with padding to maintain aspect ratio
    display_img = resize_with_padding(annotation_img, target_size=390)
    return display_img

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

    # Load image & annotations
    original_image = load_image(entry)
    annotations = load_annotation(entry)

    # Reset annotation index when switching images
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

    # Get and display annotation crop with padding
    display_img = get_annotation_crop(original_image, annotation

    # Display the cropped annotation image with aspect ratio maintained and black bars
    st.image(display_img, caption=f"Annotation {ann_idx + 1}", use_container_width=True)

    # Flag this annotation
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
                    flagged_ann_str = ', '.join(str(f) for f in flags)
                    st.write(f"Image {img_idx + 1} has annotations flagged: {flagged_ann_str}")
        else:
            st.write("No items have been flagged yet.")


if __name__ == "__main__":
    main()

