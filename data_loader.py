import os
import json
from PIL import Image

def load_all_images():
    images_dir = os.path.join("dataset", "train", "images")
    image_files = [f for f in os.listdir(images_dir) if f.endswith('.jpg')]
    images = []
    for filename in image_files:
        image_path = os.path.join(images_dir, filename)
        images.append(Image.open(image_path))
    return images

def load_all_annotations():
    labels_dir = os.path.join("dataset", "train", "labels")
    annotation_files = [f for f in os.listdir(labels_dir) if f.endswith('.json')]
    annotations_list = []
    for filename in annotation_files:
        annotation_path = os.path.join(labels_dir, filename)
        with open(annotation_path, "r") as f:
            annotations = json.load(f)
            annotations_list.append(annotations)
    return annotations_list

def total_images():
    images_dir = os.path.join("dataset", "train", "images")
    return len([f for f in os.listdir(images_dir) if f.endswith('.jpg')])
