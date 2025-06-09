import os
from PIL import Image
import logging

# Configure logging (optional, but recommended)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_data(images_dir, labels_dir, label_extension=".txt", image_extensions=('.jpg', '.jpeg', '.png')):
    """
    Loads image and label data from specified directories.

    Args:
        images_dir: Path to the directory containing images.
        labels_dir: Path to the directory containing label files.
        label_extension: Extension of the label files (default: ".txt").
        image_extensions: Tuple of allowed image file extensions (default: ('.jpg', '.jpeg', '.png')).

    Returns:
        A list of dictionaries, where each dictionary represents an image and its corresponding label file.  Returns an empty list if there's a fundamental problem (e.g., images_dir doesn't exist).
    """

    dataset = []

    # Check if the image directory exists
    if not os.path.exists(images_dir):
        logging.error(f"Image directory not found: {images_dir}")
        return dataset  # Return empty list, not an error

    # Check if the label directory exists
    if not os.path.exists(labels_dir):
        logging.warning(f"Label directory not found: {labels_dir}. Continuing without labels.")

    for img_filename in os.listdir(images_dir):
        if img_filename.lower().endswith(image_extensions):
            base_name = os.path.splitext(img_filename)[0]
            label_filename = base_name + label_extension
            label_path = os.path.join(labels_dir, label_filename)  # Correctly join paths
            image_path = os.path.join(images_dir, img_filename)  # Correctly join paths

            dataset.append({
                'image_path': image_path,
                'label_path': label_path,
                'filename': img_filename
            })

    return dataset


def load_image(entry):
    """Load image from file using the dataset entry."""
    try:
        return Image.open(entry['image_path'])
    except FileNotFoundError:
        logging.error(f"Image file not found: {entry['image_path']}")
        return None  # Or raise the exception, depending on how you want to handle it
    except Exception as e:
        logging.error(f"Error loading image {entry['image_path']}: {e}")
        return None


def load_annotation(entry, num_classes=80):  # Example: 80 classes (COCO)
    """Load annotations from label file (YOLO format assumed)."""
    annotations = []
    # Check if the 'label_path' key exists and is not None
    if 'label_path' not in entry or not entry['label_path']:
        logging.warning(f"No label path provided for image: {entry.get('image_path', 'Unknown')}")
        return annotations  # Return empty list if no label path

    try:
        with open(entry['label_path'], 'r') as f:
            lines = f.readlines()

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
    except FileNotFoundError:
        logging.warning(f"Label file not found: {entry['label_path']}")
        return annotations  # Return empty list if label file doesn't exist
    except Exception as e:
        logging.error(f"Error loading annotations from {entry['label_path']}: {e}")
        return annotations

    return annotations


class Dataset:
    def __init__(self, images_dir, labels_dir, label_extension=".txt", image_extensions=('.jpg', '.jpeg', '.png')):
        self.images_dir = images_dir # Store the directories
        self.labels_dir = labels_dir
        self.dataset = load_data(images_dir, labels_dir, label_extension, image_extensions)

    def get_dataset(self):
        """Return the dataset list of dicts."""
        return self.dataset

    def total_images(self):
        """Return total number of images."""
        return len(self.dataset)


# Example Usage (for testing purposes)
if __name__ == '__main__':
    # Define your directories (replace with your actual paths)
    images_dir = os.path.join("dataset", "train", "images")
    labels_dir = os.path.join("dataset", "train", "labels")

    # Create dataset
    try:
        dataset_obj = Dataset(images_dir, labels_dir)
        dataset = dataset_obj.get_dataset()

        # Now you can use dataset in your Streamlit app
        # Example:
        print(f"Total images: {dataset_obj.total_images()}")
        if dataset:
            print(f"First image path: {dataset[0]['image_path']}")
            annotations = load_annotation(dataset[0])
            print(f"Annotations for first image: {annotations}")
        else:
            print("No images found in the specified directories.")

    except FileNotFoundError as e:
        print(f"Error: {e}.  Please make sure the directories exist.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
