import os
from datetime import datetime

def get_image_path_from_folder(img_folder):
    """
    Get image paths from a folder
    """
    image_paths = []
    extensions = ['.jpg', '.jpeg']
    for imgname in os.listdir(img_folder):
        img_path = os.path.join(img_folder, imgname)
        if os.path.isfile(img_path) and any(imgname.lower().endswith(ext) for ext in extensions):
                image_paths.append(img_path)
    
    return image_paths


def save_images(dir_path, result):    
    """
    Save detection results in a desired folder
    """
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
    path_gen = os.path.join(dir_path, f'detections_{timestamp}')
    print(path_gen)
    os.makedirs(path_gen, exist_ok=True)
    result.save(save_dir=path_gen, exist_ok=True)

    return path_gen


def calculate_iou_custom(box1, box2):
    """
    Calculate IoU between two bounding boxes
    boxes format: [x1, y1, x2, y2]
    """
    iou = 0.0
    if box1 and box2:
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        
        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
        box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
        
        union = box1_area + box2_area - intersection
        iou = intersection / union if union > 0 else 0
    
    return iou


# iou based classification

def hand_grasp_object_mark(result, detections, save_dir):
    """
    Mark each interaction as 'hand grasp object' or 'no grasp' based on iou score and hand, object existence
    """
    hands = []
    objects = []

    hand_interactions = []
    iou = 0.0
    iou_threshold = 0.01
    hand_confidence = 0
    object_confidence = 0

    for det in detections:
        x1, y1, x2, y2, conf, class_id = det
        class_name = result.names[int(class_id)]
        
        detection = {
            'box': [x1, y1, x2, y2],
            'confidence': conf,
            'class': class_name
        }
        
        if class_name == 'hand':
            hands.append(detection)
        else:
            objects.append(detection)

    hand_box = []
    if len(hands) >= 1:
        for i, hand in enumerate(hands):
            hand_confidence = hand['confidence']
            hand_box = hand['box']
    
    object_box = []
    if len(objects) >= 1:
        for j, object in enumerate(objects):
            object_confidence = object['confidence']
            object_box = object['box']

    path_gen = save_images(save_dir, result)
    img_path = os.path.join(path_gen, result.files[0])
    
    iou = calculate_iou_custom(hand_box, object_box)
    hand_interactions.append({
        'img_name': img_path,
        'hand_confidence': hand_confidence,
        'object_confidence': object_confidence,
        'iou_score': iou,
        'result (iou > 0.01)': 'hand grasp object' if iou >= iou_threshold else 'no grasp'
    })

    return hand_interactions