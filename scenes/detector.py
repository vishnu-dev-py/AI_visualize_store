import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection

MODEL_ID = "IDEA-Research/grounding-dino-tiny"

device = "cuda" if torch.cuda.is_available() else "cpu"

processor = AutoProcessor.from_pretrained(MODEL_ID)
model = AutoModelForZeroShotObjectDetection.from_pretrained(MODEL_ID).to(device)

TEXT_LABELS = [["bed", "sofa", "chair", "table", "lamp", "pillow", "frame", "plant"]]

ALLOWED_LABELS = {"bed", "sofa", "chair", "table", "lamp", "pillow", "frame", "plant"}


def normalize_label(label: str) -> str:
    label = str(label).lower().strip()

    if "couch" in label:
        return "sofa"
    if "sofa" in label:
        return "sofa"
    if "chair" in label:
        return "chair"
    if "bed" in label:
        return "bed"
    if "table" in label:
        return "table"
    if "lamp" in label:
        return "lamp"
    if "pillow" in label or "cushion" in label:
        return "pillow"
    if "frame" in label or "picture" in label or "photo" in label:
        return "frame"
    if "plant" in label or "potted plant" in label:
        return "plant"

    return label


def resize_for_detection(image: Image.Image, max_size=960):
    original_width, original_height = image.size

    if max(original_width, original_height) <= max_size:
        return image, 1.0, 1.0

    if original_width >= original_height:
        new_width = max_size
        new_height = int((original_height / original_width) * max_size)
    else:
        new_height = max_size
        new_width = int((original_width / original_height) * max_size)

    resized = image.resize((new_width, new_height))
    scale_x = original_width / new_width
    scale_y = original_height / new_height

    return resized, scale_x, scale_y


def detect_objects(image_path: str):
    original_image = Image.open(image_path).convert("RGB")
    resized_image, scale_x, scale_y = resize_for_detection(original_image, max_size=960)

    inputs = processor(images=resized_image, text=TEXT_LABELS, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model(**inputs)

    results = processor.post_process_grounded_object_detection(
        outputs,
        inputs.input_ids,
        threshold=0.32,
        text_threshold=0.22,
        target_sizes=[resized_image.size[::-1]]
    )

    result = results[0]
    detections = []

    text_labels = result.get("text_labels", None)

    for i, (box, score) in enumerate(zip(result["boxes"], result["scores"])):
        x1, y1, x2, y2 = box.tolist()

        # scale back to original image size
        x1 *= scale_x
        y1 *= scale_y
        x2 *= scale_x
        y2 *= scale_y

        if (x2 - x1) < 25 or (y2 - y1) < 25:
            continue

        raw_label = ""
        if text_labels and i < len(text_labels):
            label_item = text_labels[i]
            if isinstance(label_item, list):
                raw_label = " ".join(label_item)
            else:
                raw_label = str(label_item)
        else:
            raw_label = str(result["labels"][i])

        mapped_label = normalize_label(raw_label)

        if mapped_label not in ALLOWED_LABELS:
            continue

        detections.append({
            "raw_label": raw_label,
            "label": mapped_label,
            "confidence": round(float(score.item()), 4),
            "x1": round(x1, 2),
            "y1": round(y1, 2),
            "x2": round(x2, 2),
            "y2": round(y2, 2),
        })

    # keep only one best object per category
    best_by_label = {}
    for item in detections:
        label = item["label"]
        if label not in best_by_label:
            best_by_label[label] = item
        else:
            if item["confidence"] > best_by_label[label]["confidence"]:
                best_by_label[label] = item

    final_detections = list(best_by_label.values())

    order = {
        "bed": 1,
        "sofa": 2,
        "chair": 3,
        "table": 4,
        "lamp": 5,
        "pillow": 6,
        "frame": 7,
        "plant": 8,
    }
    final_detections.sort(key=lambda x: order.get(x["label"], 99))

    return final_detections