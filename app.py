# --- CONFIGURATION ---
MAX_ANNOTATION_SIZE = 300  # Reduced max size for annotation crops
BUTTON_WIDTH = 60  # Reduced button width in pixels
CENTER_COL_WIDTH = 180  # Reduced center column width in pixels
ROW_HEIGHT = 40  # pixels - adjust this!
CONTAINER_WIDTH = 300  # Reduced container width in pixels.

# --- MAIN STREAMLIT APP ---
def main():
    # Declare CONTAINER_WIDTH as a global variable
    global CONTAINER_WIDTH

    # --- Inject CSS to control image stretching and alignment ---
    st.markdown(f"""
        <style>
        .container {{
            width: {CONTAINER_WIDTH}px !important;
            margin: 0 auto; /* Center the container */
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        img {{
            max-width: 100%; /* Ensure images don't exceed their container */
            height: auto;    /* Maintain aspect ratio */
            display: block;  /* Remove extra space below image */
            margin: 0 auto;   /*Center the image */
        }}
        .nav-container {{
            width: {CONTAINER_WIDTH}px !important;
            display: flex;
            flex-direction: row;
            justify-content: space-between;
            align-items: center;
            flex-wrap: nowrap; /* Prevent wrapping of elements */
            white-space: nowrap; /* Prevent text wrapping */
        }}

        .streamlit-button {{
            font-family: "Source Sans Pro", sans-serif;
            font-size: 14px; /* Reduced font size for smaller screens */
            font-weight: 400;
            width: {BUTTON_WIDTH}px !important;
            height: {ROW_HEIGHT}px !important;
            text-align: center;
            flex-shrink: 0; /* Prevent buttons from shrinking */
        }}

        .normal-text {{
            font-family: "Source Sans Pro", sans-serif;
            font-size: 14px; /* Reduced font size for smaller screens */
            font-weight: 400;
            text-align: center;
            width: {CENTER_COL_WIDTH}px !important;
            height: {ROW_HEIGHT}px !important;
            flex-shrink: 0; /* Prevent text from shrinking */
            white-space: nowrap; /* Prevent text wrapping */
        }}
        </style>
    """, unsafe_allow_html=True)

    # --- NAVIGATION ---
    with st.container():
        col_prev, col_center, col_next = st.columns([BUTTON_WIDTH, CENTER_COL_WIDTH, BUTTON_WIDTH])
        
        with col_prev:
            if st.button("◀️ Prev", key="prev_image"):
                st.session_state.current_image_index = max(0, st.session_state.current_image_index - 1)
        
        with col_center:
            st.markdown(f"<p class='normal-text'>Image {st.session_state.current_image_index + 1}/{total_imgs}</p>", unsafe_allow_html=True)
        
        with col_next:
            if st.button("Next ▶️", key="next_image"):
                st.session_state.current_image_index = min(total_imgs - 1, st.session_state.current_image_index + 1)

    # --- LOAD IMAGE & ANNOTATIONS ---
    idx = st.session_state.current_image_index
    entry = dataset[idx]

    original_image = load_image(entry)

    if original_image is None:
        st.error(f"Failed to load image: {entry['image_path']}")
        return  # Skip to the next image

    annotations = load_annotation(entry, num_classes=NUM_CLASSES)

    # --- ANNOTATION INDEX RESET ---
    if st.session_state.last_image_index != idx:
        st.session_state.current_annotation_idx = 0
        st.session_state.last_image_index = idx

    if not annotations:
        st.warning("No annotations for this image.")
        # Display the full image even without annotations
        st.image(original_image, caption="Original Image", use_container_width=True)
        return

    max_ann_idx = len(annotations) - 1

    # Initialize class_name to a default value
    class_name = "No Annotations"
    ann_idx = 0
    # --- ANNOTATION NAVIGATION ---
    with st.container():  # ADD THE CONTAINER HERE
        col_prev, col_class, col_next = st.columns([BUTTON_WIDTH, CENTER_COL_WIDTH, BUTTON_WIDTH])
        if annotations:
            ann_idx = st.session_state.current_annotation_idx
            annotation = annotations[ann_idx]
            class_id = annotation[0]  # Get the class ID
            class_name = CLASS_NAMES[class_id]  # Look up the class name - use direct indexing

        with col_prev:
            if st.button("◀️ Prev", key="prev_annotation"):
                st.session_state.current_annotation_idx = max(0,极 st.session_state.current_annotation_idx - 1)
        with col_class:
            st.markdown(f"<p class='normal-text'>{class_name}</p>", unsafe_allow_html=True)  # Use paragraph tag with normal-text class
        with col_next:
            if st.button("Next ▶️", key="next_annotation"):
                if annotations:
                    if ann_idx == max_ann_idx and st.session_state.current_image_index < total_imgs - 1:  # Last annotation and not last image
                        st.session_state.current_image_index = min(total_imgs - 1, st.session_state.current_image_index + 1)
                    else:
                        st.session_state.current_annotation_idx = min(max_ann_idx, st.session_state.current_annotation_idx + 1)

    # --- DISPLAY ANNOTATION CROP ---
    display_img = get_annotation_crop(original_image, annotation)

    if display_img is None:
        st.error("Failed to create annotation crop.")
        return

    # Display the cropped annotation image with aspect ratio maintained and black bars
    st.image(display_img, caption=f"Annotation {ann_idx + 1}", width=CONTAINER_WIDTH)

    # --- FLAGGING ---
    flag_key = f"{idx}_ann_{ann_idx}"
    if极 st.checkbox("Flag this annotation for review", key=flag_key):
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
