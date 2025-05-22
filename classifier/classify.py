from torchvision import models, transforms
from PIL import Image
import torch

model = models.mobilenet_v2(pretrained=True)
model.eval()

def classify_image(image_path):
    image = Image.open(image_path).convert('RGB')
    preprocess = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor()
    ])
    input_tensor = preprocess(image).unsqueeze(0)

    with torch.no_grad():
        output = model(input_tensor)
        predicted_class = torch.argmax(output).item()
    return predicted_class
