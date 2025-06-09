import os
from PIL import Image
import logging

# Configure logging
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

def load_data(images_dir, labels_dir, label_extension=".txt", image_extensions=('.jpg', '.jpeg', '.png')):
    """
    Loads image and label data from specified directories.

    Args:
        images_dir: Path to the directory containing images.
        labels_dir: Path to the directory containing label files.
        label_extension: Extension of the label files (default: ".txt").
        image_extensions: Tuple of allowed image file extensions (default: ('.jpg', '.jpeg', '.png')).

    Returns:
        A list of dictionaries, where each dictionary represents an image and its corresponding label file.
    """
    dataset = []

    for img_filename in os.listdir(images_dir):
        if img_filename.lower().endswith(image_extensions):
            base_name = os.path.splitext(img_filename)[0]
            label_filename = base_name + label_extension
            label_path = os.path.join(labels_dir, label_filename)
            image_path = os.path.join(images_dir, img_filename)

            dataset.append({
                'image_path': image_path,
                'label_path': label_path,
                'filename': img_filename
            })
    return dataset


def load_image(entry):
    """Load image from file using the dataset entry."""
    return Image.open(entry['image_path'])


def load_annotation(entry, num_classes=80):  # Example: 80 classes (COCO)
    """Load annotations from label file (YOLO format assumed)."""
    try:
        with open(entry['label_path'], 'r') as f:
            lines = f.readlines()
        annotations = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) != 5:
                logging.warning(f"Skipping malformed line in {entry['label_path']}: {line}")
                continue
            try:
                class_id = int(parts[0])
                x_center = float(parts[1])
                y_center = float(parts[2])
                box_width = float(parts[3])
                box_height = float(parts[4])
            except ValueError:
                logging.warning(f"Skipping line with invalid number format in {entry['label_path']}: {line}")
                continue

            if not (0 <= class_id < num_classes and 0 <= x_center <= 1 and 0 <= y_center <= 1 and 0 <= box_width <= 1 and 0 <= box_height <= 1):
                logging.warning(f"Skipping invalid annotation in {entry['label_path']}: {line}")
                continue

            annotations.append([class_id, x_center, y_center, box_width, box_height])
        return annotations
    except FileNotFoundError:
        logging.warning(f"Label file not found: {entry['label_path']}")
        return []  # If label file doesn't exist, return empty list


class Dataset:
    def __init__(self, images_dir, labels_dir, label_extension=".txt", image_extensions=('.jpg', '.jpeg', '.png')):
        self.dataset = load_data(images_dir, labels_dir, label_extension, image_extensions)

    def get_dataset(self):
        """Return the dataset list of dicts."""
        return self.dataset

    def total_images(self):
        """Return total number of images."""
        return len(self.dataset)

# Example Usage
if __name__ == '__main__':
    # Define your directories
    images_dir = os.path.join("dataset", "train", "images")
    labels_dir = os.path.join("dataset", "train", "labels")

    # Create dataset
    dataset_obj = Dataset(images_dir, labels_dir)
    dataset = dataset_obj.get_dataset()

    # Now you can use dataset in your Streamlit app
    # Example:
    print(f"Total images: {dataset_obj.total_images()}")
    if dataset:
        print(f"First image path: {dataset[0]['image_path']}")
        annotations = load_annotation(dataset[0])
        print(f"Annotations for first image: {annotations}")
