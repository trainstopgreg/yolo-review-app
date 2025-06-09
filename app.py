import os
import streamlit as st
from PIL import Image, ImageDraw
import pandas as pd

# Set your directories here
IMAGE_DIR = 'dataset/test/images/'
ANNOTATION_DIR = 'dataset/test/labels/'

# List image files
images = [f for f in os.listdir(IMAGE_DIR) if f.endswith(('.jpg', '.png'))]

# Streamlit app title
st.title("YOLO Annotation Review Tool")

# Select an image
selected_image = st.selectbox("Select an image", images)

if selected_image:
    # Load image
    img_path = os.path.join(IMAGE_DIR, selected_image)
    image = Image.open(img_path)
    img_width, img_height = image.size

    # Load annotations
    def load_annotations(image_name):
        txt_path = os.path.join(ANNOTATION_DIR, image_name.rsplit('.', 1)[0] + '.txt')
        if os.path.exists(txt_path):
            data = []
            with open(txt_path, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 5:
                        class_id, x_center, y_center, width, height = parts
                        data.append({
                            'class_id': class_id,
                            'x_center': float(x_center),
                            'y_center': float(y_center),
                            'width': float(width),
                            'height': float(height),
                            'review': None  # To store 'correct' or 'incorrect'
                        })
            return pd.DataFrame(data)
        else:
            return pd.DataFrame(columns=['class_id', 'x_center', 'y_center', 'width', 'height', 'review'])

    # Load the annotations for the selected image
    annotations_df = load_annotations(selected_image)

    # Function to draw bounding boxes on the image
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

    # Display the image with bounding boxes
    annotated_image = draw_bboxes(image, annotations_df)
    st.image(annotated_image, caption=selected_image)

    st.markdown("### Annotations")
    # For each annotation, show class and buttons to mark correctness
    for idx, row in annotations_df.iterrows():
        st.write(f"Annotation {idx} - Class: {row['class_id']}")
        col1, col2 = st.beta_columns(2)
        with col1:
            if st.button(f"Mark Correct", key=f"correct_{idx}"):
                annotations_df.at[idx, 'review'] = 'correct'
        with col2:
            if st.button(f"Mark Incorrect", key=f"incorrect_{idx}"):
                annotations_df.at[idx, 'review'] = 'incorrect'
        # Show current review status
        status = annotations_df.at[idx, 'review']
        if status:
            st.write(f"Status: {status}")

    # Button to save the review results
    if st.button("Save Reviews"):
        save_path = os.path.join('reviews', selected_image + '_review.csv')
        os.makedirs('reviews', exist_ok=True)
        annotations_df.to_csv(save_path, index=False)
        st.success(f"Review saved to {save_path}")
