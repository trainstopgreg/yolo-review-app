import os

def load_image(index):
    image_path = os.path.join("dataset", "train", "images", f"image_{index+1:03d}.jpg")
    return Image.open(image_path)

def load_annotations(index):
    annotation_path = os.path.join("dataset", "train", "labels", f"image_{index+1:03d}.json")
    with open(annotation_path, "r") as f:
        annotations = json.load(f)
    return annotations

def total_images():
    return len(os.listdir(os.path.join("data", "images")))
