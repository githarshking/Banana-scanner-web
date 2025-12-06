import requests
import json
import os

# --- CONFIGURATION ---
# REPLACE THIS with the path to a real banana image on your computer
TEST_IMAGE_PATH = r"C:\Users\sudha\Downloads\istockphoto-1251478344-612x612.jpg"
API_URL = "http://127.0.0.1:8000/predict"

def test_prediction():
    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"Error: Test image not found at: {TEST_IMAGE_PATH}")
        print("Please edit 'TEST_IMAGE_PATH' in this script to point to a valid jpg/png file.")
        return

    print(f"Sending image to API: {TEST_IMAGE_PATH}...")
    
    try:
        # Open the image in binary mode
        with open(TEST_IMAGE_PATH, "rb") as f:
            # Create the multipart/form-data payload
            # The key 'file' must match the parameter name in your FastAPI app
            files = {"file": (os.path.basename(TEST_IMAGE_PATH), f, "image/jpeg")}
            
            # Send POST request
            response = requests.post(API_URL, files=files)
            
        # Check status
        if response.status_code == 200:
            print("\n✅ SUCCESS! Prediction received:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"\n❌ Error: API returned status code {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ Connection Failed: {e}")
        print("Make sure your 'app.py' server is running in another terminal!")

if __name__ == "__main__":
    test_prediction()