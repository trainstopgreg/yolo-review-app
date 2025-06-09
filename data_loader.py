import os
from PIL import Image

# Define your directories
images_dir = os.path.join("dataset", "train", "images")
labels_dir = os.path.join("dataset", "train", "labels")

# Build a list of all image files
dataset = []

for img_filename in os.listdir(images_dir):
    if img_filename.endswith('.jpg'):
        base_name = os.path.splitext(img_filename)[0]
        label_filename = base_name + ".txt"  # Or ".json" if your labels are in JSON format
        dataset.append({
            'image_path': os.path.join(images_dir, img_filename),
            'label_path': os.path.join(labels_dir, label_filename),
            'filename': img_filename
        })

def load_image(entry):
    """Load image from file using the dataset entry."""
    return Image.open(entry['image_path'])

def load_annotation(entry):
    """Load annotations from label file (YOLO format assumed)."""
    try:
        with open(entry['label_path'], 'r') as f:
            lines = f.readlines()
        annotations = []
        for line in lines:
            parts = line.strip().split()
            class_id = int(parts[0])
            x_center = float(parts[1])
            y_center = float(parts[2])
            box_width = float(parts[3])
            box_height = float(parts[4])
            annotations.append([class_id, x_center, y_center, box_width, box_height])
        return annotations
    except FileNotFoundError:
        return []  # If label file doesn't exist, return empty list

def get_dataset():
    """Return the dataset list of dicts."""
    return dataset

def total_images():
    """Return total number of images."""
    return len(dataset)
