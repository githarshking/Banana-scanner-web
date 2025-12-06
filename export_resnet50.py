import torch
import torch.nn as nn
import torch.onnx
import os
from torchvision import models

# --- CONFIGURATION ---
# IMPORTANT: Make sure this matches the filename you used in your successful test script
MODEL_WEIGHTS_PATH = "best_banana_ripeness_resnet.pth" 
ONNX_OUTPUT_PATH = "model.onnx"
NUM_CLASSES = 8

def export_model():
    if not os.path.exists(MODEL_WEIGHTS_PATH):
        print(f"Error: Weights file not found at {MODEL_WEIGHTS_PATH}")
        return

    print(f"1. Creating ResNet50 model architecture...")
    # Initialize ResNet50 (The same architecture used in your test script)
    model = models.resnet50(weights=None)
    
    # Replace the final layer to match your 8 classes
    num_ftrs = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(0.5),
        nn.Linear(num_ftrs, NUM_CLASSES)
    )

    print(f"2. Loading weights from {MODEL_WEIGHTS_PATH}...")
    # Load the trained weights
    try:
        state_dict = torch.load(MODEL_WEIGHTS_PATH, map_location=torch.device('cpu'))
        model.load_state_dict(state_dict)
        model.eval()
        print("   Weights loaded successfully.")
    except Exception as e:
        print(f"   Error loading weights: {e}")
        return

    # Create dummy input for tracing (Batch Size 1, RGB 3, 224x224)
    dummy_input = torch.randn(1, 3, 224, 224, requires_grad=True)
    
    print(f"3. Exporting to ONNX ({ONNX_OUTPUT_PATH})...")
    
    # Export with dynamic axes for flexibility
    torch.onnx.export(
        model, 
        dummy_input, 
        ONNX_OUTPUT_PATH, 
        verbose=False,
        input_names=["input_image"], 
        output_names=["output_logits"],
        dynamic_axes={'input_image': {0: 'batch'}, 'output_logits': {0: 'batch'}},
        opset_version=17  # Use a modern opset
    )
    
    print(f"\n✅ SUCCESS! Model exported to '{ONNX_OUTPUT_PATH}'")
    print("   (If a .data file was created, keep it in the same folder)")

if __name__ == "__main__":
    export_model()