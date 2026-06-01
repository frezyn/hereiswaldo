import torch
import torchvision

from PIL import Image
from PIL import ImageDraw
from PIL import ImageEnhance

from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor


MODEL_PATH = "./waldo_model.pth"
IMAGE_PATH = "./imagetest/Flou23_jpg.rf.da02c4cafbc3956f56642da90c2cc6f6.jpg"
CONFIDENCE_THRESHOLD = 0.8


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


original_image = Image.open(
    IMAGE_PATH
).convert("RGB")

image_tensor = torchvision.transforms.functional.to_tensor(
    original_image
).to(device)


with torch.no_grad():
    predictions = model([image_tensor])

prediction = predictions[0]

boxes = prediction["boxes"]
scores = prediction["scores"]


dark_image = ImageEnhance.Brightness(
    original_image
).enhance(0.12)

result_image = dark_image.copy()

draw = ImageDraw.Draw(result_image)

found_count = 0


for index, (box, score) in enumerate(zip(boxes, scores)):

    score = score.item()

    print(f"Detection #{index}")
    print("Score:", score)

    if score < CONFIDENCE_THRESHOLD:
        continue

    found_count += 1

    x1, y1, x2, y2 = map(int, box.tolist())

    print(
        f"Waldo found at: {x1}, {y1}, {x2}, {y2}"
    )

    waldo_crop = original_image.crop(
        (x1, y1, x2, y2)
    )

    result_image.paste(
        waldo_crop,
        (x1, y1)
    )

    draw.rectangle(
        [x1, y1, x2, y2],
        outline="red",
        width=4
    )

    draw.text(
        (x1, y1 - 25),
        f"Waldo {score:.2f}",
        fill="red"
    )


if found_count > 0:

    print(f"\n✅ {found_count} Waldos found!")
    result_image.show()

else:

    print("\n❌ No Waldo found.")
