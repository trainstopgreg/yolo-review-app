import streamlit as st
import io
from data_loader import load_image, load_annotation, Dataset  # Corrected import
from PIL import Image
import os
import yaml  # Import the YAML library

# --- CONFIGURATION ---
IMAGE_SIZE = 390  # Size to resize images for display
NUM_CLASSES = 3  # Replace with the actual number of classes in your dataset (can be read from yaml)
BUTTON_WIDTH = 75  # Set button width in pixels
CENTER_COL_WIDTH = 240  # Set center column width in pixels
ROW_HEIGHT = 40 #pixels - adjust this!

# Use environment variables for directory paths, with defaults
IMAGES_DIR = os.environ.get("IMAGES_DIR", "dataset/train/images")
LABELS_DIR = os.environ.get("LABELS_DIR", "dataset/train", "labels")
DATA_YAML_PATH = os.path.join("dataset", "data.yaml")  # Path to your data.yaml file

# Load class names from data.yaml
try:
    with open(DATA_YAML_PATH, 'r') as f:
        data = yaml.safe_load(f)
        CLASS_NAMES = data['names']  # Assuming class names are under the 'names' key
        NUM_CLASSES = len(CLASS_NAMES)  # Get the number of classes
except FileNotFoundError:
    st.error(f"Error: data.yaml not found at {DATA_YAML_PATH}.  Please make sure the file exists.")
    st.stop()
except KeyError:
    st.error(f"Error: 'names' key not found in {DATA_YAML_PATH}.  Please make sure the file has a list of class names.")
    st.stop()
except yaml.YAMLError as e:
    st.error(f"Error: Could not parse data.yaml. Please check the YAML syntax. Error details: {e}")
    st.stop()
except Exception as e:
    st.error(f"An unexpected error occurred while loading class names from data.yaml: {e}")
    st.stop()


# --- DATA LOADING ---
try:
    dataset_obj = Dataset(IMAGES_DIR, LABELS_DIR)
    dataset = dataset_obj.get_dataset()  # Access get_dataset through the object
    total_imgs = dataset_obj.total_images()
except Exception as e:
    st.error(f"Error loading dataset: {e}.  Check IMAGES_DIR and LABELS_DIR.")
    st.stop()  # Stop the app if dataset loading fails


# --- SESSION STATE INITIALIZATION ---
if 'current_image_index' not in st.session_state:
    st.session_state.current_image_index = 0
if 'flagged_items' not in st.session_state:
    st.session_state.flagged_items = {}
if 'current_annotation_idx' not in st.session_state:
    st.session_state.current_annotation_idx = 0
if 'last_image_index' not in st.session_state:
    st.session_state.last_image_index = -1


# --- HELPER FUNCTIONS ---
def resize_with_padding(image, target_size=IMAGE_SIZE):
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
        # Ensure new_height is at least 1 to avoid errors
        new_height = max(1, new_height)
    else:
        # Taller image or square
        new_height = target_size
        new_width = int(target_size * aspect_ratio)
        # Ensure new_width is at least 1 to avoid errors
        new_width = max(1, new_width)

    # Resize the image
    resized_img = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Create black background
    new_img = Image.new("RGB", (target_size, target_size), (0, 0, 0))
    # Center the resized image
    paste_x = (target_size - new_width) // 2
    paste_y = (target_size - new_height) // 2
    new_img.paste(resized_img, (paste_x, paste_y))
    return new_img


def get_annotation_crop(image, annotation):
    """
    Crops an annotation from the original image, resizes it with padding,
    and returns the resulting image.
    """
    # Calculate bbox coordinates in the original image
    class_id, x_center, y_center, box_width, box_height = annotation
    img_width, img_height = image.size  # Get original image dimensions

    x1 = int((x_center - box_width / 2) * img_width)
    y1 = int((y_center - box_height / 2) * img_height)
    x2 = int((x_center + box_width / 2) * img_width)
    y2 = int((y_center + box_height / 2) * img_height)

    # Ensure coordinates are within image bounds
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(img_width, x2)
    y2 = min(img_height, y2)

    # Crop the annotation area
    crop_box = (x1, y1, x2, y2)
    try:
        annotation_img = image.crop(crop_box)
    except Exception as e:
        st.error(f"Error cropping image: {e}")
        return None  # Or handle the error as appropriate

    # Resize annotation crop with padding to maintain aspect ratio
    display_img = resize_with_padding(annotation_img, target_size=IMAGE_SIZE)
    return display_img


# --- MAIN STREAMLIT APP ---
def main():
    st.set_page_config(page_title="YOLO Annotation Review", layout="wide")

    # --- Inject CSS to control button size, text alignment, and vertical alignment ---
    st.markdown(f"""
        <style>
        .streamlit-button {{
            font-family: "Source Sans Pro", sans-serif;
            font-size: 16px;
            font-weight: 400;
            width: {BUTTON_WIDTH}px !important;
            height: {ROW_HEIGHT}px !important; /* Consistent height for buttons */
            display: flex; /* Use flexbox for vertical alignment */
            justify-content: center; /*Center horizontally*/
            align-items: center; /* Center text vertically */

        }}
        .normal-text {{
            font-family: "Source Sans Pro", sans-serif;
            font-size: 16px;
            font-weight: 400;
            text-align: center;
            height: {ROW_HEIGHT}px !important; /* Consistent height for text */
            display: flex; /* Use flexbox for vertical alignment */
            justify-content: center; /*Center horizontally*/
            align-items: center; /* Center text vertically */
        }}
        </style>
    """, unsafe_allow_html=True)

    # --- NAVIGATION ---
    col1, col2, col3 = st.columns([BUTTON_WIDTH, CENTER_COL_WIDTH, BUTTON_WIDTH])  # Fixed column widths
    current_image_index = st.session_state.current_image_index + 1  # 1-indexed
    with col1:
        if st.button("◀️ Prev", key="prev_image"):
            st.session_state.current_image_index = max(0, st.session_state.current_image_index - 1)
    with col2:
        st.markdown(f"<p class='normal-text'>Image {current_image_index}/{total_imgs}</p>", unsafe_allow_html=True)
    with col3:
        if st.button("Next ▶️", key="next_image"):
            st.session_state.current_image_index = min(total_imgs - 1, st.session_state.current_image_index + 1)

    idx = st.session_state.current_image_index
    entry = dataset[idx]

    # --- LOAD IMAGE & ANNOTATIONS ---
    original_image = load_image(entry)
    if original_image is None:
        st.error(f"Failed to load image: {entry['image_path']}")
        return  # Skip to the next image

    annotations = load_annotation(entry, num_classes=NUM_CLASSES)

    # --- ANNOTATION NAVIGATION ---
    col_prev, col_class, col_next = st.columns([BUTTON_WIDTH, CENTER_COL_WIDTH, BUTTON_WIDTH])  # Fixed column widths
    ann_idx = st.session_state.current_annotation_idx
    annotation = annotations[ann_idx]
    class_id = annotation[0]  # Get the class ID
    class_name = CLASS_NAMES[class_id]  # Look up the class name - use direct indexing

    with col_prev:
        if st.button("◀️ Prev", key="prev_annotation"):
            st.session_state.current_annotation_idx = max(0, st.session_state.current_annotation_idx - 1)
    with col_class:
        st.markdown(f"<p class='normal-text'>{class_name}</p>", unsafe_allow_html=True) # Use paragraph tag with normal-text class
    with col_next:
        if st.button("Next ▶️", key="next_annotation"):
            if ann_idx == max_ann_idx and st.session_state.current_image_index < total_imgs - 1: #Last annotation and not last image
                st.session_state.current_image_index = min(total_imgs - 1, st.session_state.current_image_index + 1)
            else:
                st.session_state.current_annotation_idx = min(max_ann_idx, st.session_state.current_annotation_idx + 1)


    # --- DISPLAY ANNOTATION CROP ---
    display_img = get_annotation_crop(original_image, annotation)

    if display_img is None:
        st.error("Failed to create annotation crop.")
        return

    # Display the cropped annotation image with aspect ratio maintained and black bars
    st.image(display_img, caption=f"Annotation {ann_idx + 1}", use_container_width=True)

    # --- FLAGGING ---
    flag_key = f"{idx}_ann_{ann_idx}"
    if st.checkbox("Flag this annotation for review", key=flag_key):
        if idx not in st.session_state.flagged_items:
            st.session_state.flagged_items[idx] = []
        if ann_idx not in st.session_state.flagged_items[idx]:
            st.session_state.flagged_items[idx].append(ann_idx)
            st.success("Annotation flagged!")
    else:
        # Remove flag if unchecked
        if idx in st.session_state.flagged_items and ann_idx in st.session_state.flagged_items[idx]:
            st.session_state.flagged_items[idx].remove(ann_idx)
            st.success("Annotation unflagged!")
            if not st.session_state.flagged_items[idx]:
                del st.session_state.flagged_items[idx]


    # --- SHOW FLAGGED ITEMS ---
    with st.expander("Flagged Items"):
        flagged = st.session_state.flagged_items
        if flagged:
            for img_idx, flags in flagged.items():
                if isinstance(flags, str) and flags == "entire_image":
                    st.write(f"Image {img_idx + 1} flagged.")
                else:
                    flagged_ann_str = ', '.join(str(f) for f in flags)
                    st.write(f"Image {img_idx + 1} has annotations flagged: {flagged_ann_str}")
        else:
            st.write("No items have been flagged yet.")

# --- RUN MAIN APP ---
if __name__ == "__main__":
    main()
