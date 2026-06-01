import io

import torch
import torchvision

from fastapi import UploadFile
from fastapi.responses import StreamingResponse

from PIL import Image
from PIL import ImageDraw

from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor


MODEL_PATH = "./waldo_model.pth"
CONFIDENCE_THRESHOLD = 0.8
PADDING = 200    
BOX_PADDING = 12


device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Using device:", device)


model = fasterrcnn_resnet50_fpn(weights=None)

in_features = model.roi_heads.box_predictor.cls_score.in_features

model.roi_heads.box_predictor = FastRCNNPredictor(
    in_features,
    num_classes=2
)

model.load_state_dict(
    torch.load(MODEL_PATH, map_location=device)
)

model.to(device)
model.eval()

print("Model loaded!")


async def detect_waldo(file: UploadFile):

    image_bytes = await file.read()

    original_image = Image.open(
        io.BytesIO(image_bytes)
    ).convert("RGB")

    img_w, img_h = original_image.size

    image_tensor = torchvision.transforms.functional.to_tensor(
        original_image
    ).to(device)

    with torch.no_grad():
        predictions = model([image_tensor])

    prediction = predictions[0]

    boxes = prediction["boxes"]
    scores = prediction["scores"]

    valid_detections = [
        (box, score.item())
        for box, score in zip(boxes, scores)
        if score.item() >= CONFIDENCE_THRESHOLD
    ]

    found_count = len(valid_detections)

    if found_count == 0:
        output = io.BytesIO()
        original_image.save(output, format="PNG")
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="image/png",
            headers={"X-Exist-Waldo": "false"}
        )

    crops = []

    for box, score in valid_detections:
        x1, y1, x2, y2 = map(int, box.tolist())

        crop_x1 = max(0, x1 - PADDING)
        crop_y1 = max(0, y1 - PADDING)
        crop_x2 = min(img_w, x2 + PADDING)
        crop_y2 = min(img_h, y2 + PADDING)

        crop = original_image.crop((crop_x1, crop_y1, crop_x2, crop_y2))

        draw = ImageDraw.Draw(crop)
        rel_x1 = x1 - crop_x1
        rel_y1 = y1 - crop_y1
        rel_x2 = x2 - crop_x1
        rel_y2 = y2 - crop_y1

        draw.rectangle(
            [
                max(0, rel_x1 - BOX_PADDING),
                max(0, rel_y1 - BOX_PADDING),
                rel_x2 + BOX_PADDING,
                rel_y2 + BOX_PADDING,
            ],
            outline="red",
            width=4
        )

        draw.text(
            (max(0, rel_x1 - BOX_PADDING), max(0, rel_y1 - BOX_PADDING - 22)),
            f"Waldo {score:.2f}",
            fill="red"
        )

        crops.append(crop)

    print(f"Waldos found: {found_count}, returning {len(crops)} crop(s)")

    if len(crops) == 1:
        result_image = crops[0]
    else:
        total_width = sum(c.width for c in crops) + (len(crops) - 1) * 8  
        max_height = max(c.height for c in crops)
        result_image = Image.new("RGB", (total_width, max_height), color=(30, 30, 30))

        x_offset = 0
        for crop in crops:
            y_offset = (max_height - crop.height) // 2
            result_image.paste(crop, (x_offset, y_offset))
            x_offset += crop.width + 8

    output = io.BytesIO()
    result_image.save(output, format="PNG")
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="image/png",
        headers={"X-Exist-Waldo": "true"}
    )
