from ultralytics import YOLO

model = YOLO("yolov8m.pt")

def normalize_label(label):
    label = label.lower()

    mapping = {
        "sofa": ["couch", "sofa"],
        "chair": ["chair"],
        "bed": ["bed"],
        "table": ["table", "dining table"],
        "plant": ["plant", "potted plant"],
        "lamp": ["lamp", "light"]
    }

    for normalized, keywords in mapping.items():
        if any(word in label for word in keywords):
            return normalized

    return None


def detect_objects_yolo(image_path):
    results = model(image_path)

    best_by_label = {}

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            conf = float(box.conf[0])

            print(f"RAW DETECTION: label={label}, conf={conf:.3f}")

            if conf < 0.1:
                continue

            mapped = normalize_label(label)
            print(f"  mapped -> {mapped}")

            if not mapped:
                continue

            x1, y1, x2, y2 = box.xyxy[0].tolist()

            obj = {
                "label": mapped,
                "confidence": round(conf, 3),
                "x1": round(x1, 2),
                "y1": round(y1, 2),
                "x2": round(x2, 2),
                "y2": round(y2, 2),
            }

            if mapped not in best_by_label or conf > best_by_label[mapped]["confidence"]:
                best_by_label[mapped] = obj

    return list(best_by_label.values())
