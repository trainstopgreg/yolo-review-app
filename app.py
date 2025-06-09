import os
import zipfile
import io
import pandas as pd
from PIL import Image, ImageDraw
import streamlit as st

# Title
st.title("YOLO v1.1 ZIP Upload & Annotation Review Tool")

# Upload ZIP containing images and annotations
uploaded_zip = st.file_uploader("Upload ZIP with images and YOLO annotations", type=["zip"])

# Initialize data holders
images_data = {}
annotations_data = {}

if uploaded_zip:
    # Read ZIP file into memory
    with zipfile.ZipFile(uploaded_zip) as z:
        # List all file names
        file_list = z.namelist()
        # Filter image files
        image_files = [f for f in file_list if f.lower().endswith(('.jpg', '.png'))]
        # Find all annotation files
        annotation_files = [f for f in file_list if f.lower().endswith('.txt')]

        # Load images into dictionary
        for img_file in image_files:
            with z.open(img_file) as img_f:
                img_bytes = img_f.read()
                image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                images_data[img_file] = image

        # Load annotations into dictionary
        for ann_file in annotation_files:
            df = pd.DataFrame(columns=['class_id', 'x_center', 'y_center', 'width', 'height', 'review'])
            with z.open(ann_file) as ann_f:
                for line in ann_f:
                    line_str = line.decode('utf-8').strip()
                    if line_str:
                        parts = line_str.split()
                        if len(parts) == 5:
                            class_id, x_c, y_c, w, h = parts
                            df = df.append({'class_id': class_id,
                                            'x_center': float(x_c),
                                            'y_center': float(y_c),
                                            'width': float(w),
                                            'height': float(h),
                                            'review': None}, ignore_index=True)
            # Save annotation with a key matching image filename
            base_name = os.path.basename(ann_file).replace('.txt', '')
            annotations_data[base_name] = df

    st.success(f"Loaded {len(images_data)} images and {len(annotations_data)} annotation files.")

# Let user select image from uploaded data
if images_data:
    image_names = list(images_data.keys())
    selected_image_name = st.selectbox("Select an image to review", image_names)

    if selected_image_name:
        image = images_data[selected_image_name]
        img_width, img_height = image.size

        # Load annotations for this image
        ann_df = annotations_data.get(selected_image_name, pd.DataFrame(
            columns=['class_id', 'x_center', 'y_center', 'width', 'height', 'review']
        ))

        # Function to draw bounding boxes
        def draw_bboxes(img, df):
            img_draw = img.copy()
            draw = ImageDraw.Draw(img_draw)
            for _, row in df.iterrows():
                xmin = int((row['x_center'] - row['width'] / 2) * img_width)
                xmax = int((row['x_center'] + row['width'] / 2) * img_width)
                ymin = int((row['y_center'] - row['height'] / 2) * img_height)
                ymax = int((row['y_center'] + row['height'] / 2) * img_height)
                color = 'blue'
                if row['review'] == 'correct':
                    color = 'green'
                elif row['review'] == 'incorrect':
                    color = 'red'
                draw.rectangle([xmin, ymin, xmax, ymax], outline=color, width=2)
            return img_draw

        # Display annotated image
        annotated_img = draw_bboxes(image, ann_df)
        st.image(annotated_img, caption=selected_image_name)

        st.markdown("### Annotations Review")
        # For each annotation, provide check buttons to mark correct/incorrect
        for idx, row in ann_df.iterrows():
            st.write(f"Annotation {idx} - Class: {row['class_id']}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Mark Correct", key=f"correct_{selected_image_name}_{idx}"):
                    ann_df.at[idx,
