import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import io
import os

# --- Configuration ---
# Must match your training/test script EXACTLY
MODEL_PATH = "best_banana_ripeness_resnet.pth"
NUM_CLASSES = 8
DEVICE = "cpu" # Web servers usually don't have GPUs

# Standard ImageNet Normalization
MEAN = [0.485, 0.456, 0.406] 
STD = [0.229, 0.224, 0.225]
INPUT_SIZE = (224, 224) 

RIPENESS_MAPPING = {
    0: {"class": "degree1 (Green/Unripe)", "days_left": "10 - 14 days", "message": "High shelf life remaining. Ideal for long-term storage."},
    1: {"class": "degree2 (Slight Yellow)", "days_left": "8 - 10 days", "message": "Ready to eat soon. Good for storage."},
    2: {"class": "degree3 (More Yellow)", "days_left": "5 - 7 days", "message": "Optimal balance of sweetness and firmness. Enjoy now or store briefly."},
    3: {"class": "degree4 (Fully Yellow)", "days_left": "3 - 4 days", "message": "Perfectly ripe and sweet! Eat soon."},
    4: {"class": "degree5 (Small Spots)", "days_left": "2 - 3 days", "message": "Very sweet. Best for immediate consumption or quick recipes."},
    5: {"class": "degree6 (Half Brown Spots)", "days_left": "1 - 2 days", "message": "Starting to soften. Excellent for baking, smoothies, or freezing."},
    6: {"class": "degree7 (Mostly Brown)", "days_left": "0 - 1 day", "message": "Use immediately. Ideal for pureed desserts or banana bread."},
    7: {"class": "degree8 (Fully Brown/Black)", "days_left": "0 days", "message": "Overripe. Safe for consumption, but best used in cooked/baked goods."}
}

class RipenessPredictor:
    def __init__(self, model_path: str):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
            
        print(f"Loading PyTorch model from: {model_path}")
        
        # 1. Define Model Architecture (Must match training!)
        # We use the same logic as your test script: ResNet50 with a modified FC layer
        self.model = models.resnet50(weights=None)
        num_ftrs = self.model.fc.in_features
        self.model.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(num_ftrs, NUM_CLASSES)
        )
        
        # 2. Load Weights
        # Map location is critical for CPU deployment
        state_dict = torch.load(model_path, map_location=torch.device(DEVICE))
        self.model.load_state_dict(state_dict)
        self.model.to(DEVICE)
        self.model.eval() # Set to evaluation mode
        
        # 3. Define Transform
        # Matches your test script exactly
        self.transform = transforms.Compose([
            transforms.Resize(INPUT_SIZE),
            transforms.ToTensor(),
            transforms.Normalize(MEAN, STD)
        ])

    def preprocess(self, image_bytes: bytes) -> torch.Tensor:
        image = Image.open(io.BytesIO(image_bytes))
        if image.mode != "RGB":
            image = image.convert("RGB")
            
        # Transform and add batch dimension
        return self.transform(image).unsqueeze(0).to(DEVICE)

    def predict(self, image_bytes: bytes) -> dict:
        input_tensor = self.preprocess(image_bytes)
        
        with torch.no_grad():
            output_logits = self.model(input_tensor)
            
        # Post-Processing
        probabilities = torch.softmax(output_logits, dim=1)[0]
        predicted_index = torch.argmax(probabilities).item()
        confidence = probabilities[predicted_index].item()
        
        result = RIPENESS_MAPPING.get(predicted_index, {"class": "Unknown", "days_left": "?", "message": "Error"})
        result['confidence'] = confidence
        
        # Optional: Print debug info to console
        print(f"[DEBUG] Prediction: {result['class']} ({confidence:.2%})")
        
        return result

# Initialize
try:
    PREDICTOR = RipenessPredictor(MODEL_PATH)
except Exception as e:
    print(f"Error loading model: {e}")
    PREDICTOR = None