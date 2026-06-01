import os
import torch
import torchvision

import xml.etree.ElementTree as ET

from PIL import Image

from torch.utils.data import Dataset
from torch.utils.data import DataLoader

from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor


class WaldoDataset(Dataset):

    def __init__(self, image_dir, annotation_dir):

        self.image_dir = image_dir
        self.annotation_dir = annotation_dir

        self.images = sorted([
            file
            for file in os.listdir(image_dir)
            if file.endswith((".jpg", ".jpeg", ".png"))
        ])

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):

        image_name = self.images[idx]

        image_path = os.path.join(
            self.image_dir,
            image_name
        )

        annotation_path = os.path.join(
            self.annotation_dir,
            image_name.replace(".jpg", ".xml")
        )


        image = Image.open(image_path).convert("RGB")

        boxes = []
        labels = []

        if os.path.exists(annotation_path):

            tree = ET.parse(annotation_path)

            root = tree.getroot()

            for obj in root.findall("object"):

                label = obj.find("name").text

                bbox = obj.find("bndbox")

                xmin = int(bbox.find("xmin").text)
                ymin = int(bbox.find("ymin").text)
                xmax = int(bbox.find("xmax").text)
                ymax = int(bbox.find("ymax").text)

                boxes.append([xmin, ymin, xmax, ymax])

                # waldo = 1
                labels.append(1)


        if len(boxes) == 0:

            boxes = torch.zeros((0, 4), dtype=torch.float32)

            labels = torch.zeros((0,), dtype=torch.int64)

        else:

            boxes = torch.as_tensor(
                boxes,
                dtype=torch.float32
            )

            labels = torch.as_tensor(
                labels,
                dtype=torch.int64
            )

        target = {
            "boxes": boxes,
            "labels": labels
        }

        image = torchvision.transforms.functional.to_tensor(image)

        return image, target


dataset = WaldoDataset(
    image_dir="./dataset/dataset_roboflow/train",
    annotation_dir="./dataset/dataset_roboflow/train"
)

train_loader = DataLoader(
    dataset,
    batch_size=2,
    shuffle=True,
    collate_fn=lambda x: tuple(zip(*x))
)


model = fasterrcnn_resnet50_fpn(pretrained=True)

in_features = model.roi_heads.box_predictor.cls_score.in_features

model.roi_heads.box_predictor = FastRCNNPredictor(
    in_features,
    num_classes=2
)

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Using device:", device)

model.to(device)

optimizer = torch.optim.Adam(
    model.parameters(),
    lr=0.0001
)

num_epochs = 10

for epoch in range(num_epochs):

    model.train()

    total_loss = 0

    for images, targets in train_loader:

        images = [
            img.to(device)
            for img in images
        ]

        targets = [
            {
                k: v.to(device)
                for k, v in t.items()
            }
            for t in targets
        ]

        loss_dict = model(images, targets)

        losses = sum(
            loss
            for loss in loss_dict.values()
        )

        optimizer.zero_grad()

        losses.backward()

        optimizer.step()

        total_loss += losses.item()

    print(
        f"Epoch {epoch+1}/{num_epochs} "
        f"Loss: {total_loss:.4f}"
    )


#Mixed precision para diminuir o tamanho do modelo, 
#e por ventura, conseguir subir ele no github.
model.half()
for param in model.parameters():
    param.data = param.data.half()

torch.save(
    model.state_dict(),
    "waldo_model.pth"
)

print("Model saved!")
