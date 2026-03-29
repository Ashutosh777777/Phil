import requests
import time
import glob
import os
import subprocess

IMAGE_FOLDER = "/mnt/d/AI_Projects/GH/Phil/assets"
N8N_WEBHOOK = "http://localhost:5678/webhook/a3267b49-21b4-47a2-8bfd-c27cbf7a528e"

def clear_old_images():
    for f in glob.glob(f"{IMAGE_FOLDER}\\*.png") + glob.glob(f"{IMAGE_FOLDER}\\*.jpg"):
        os.remove(f)
        print(f"Deleted old image: {f}")

def generate_image():
    print("Generating new background image...")
    response = requests.post(N8N_WEBHOOK, timeout=120)
    if response.status_code == 200:
        image_path = os.path.join(IMAGE_FOLDER, "background.png")
        with open(image_path, "wb") as f:
            f.write(response.content)
        print(f"Image saved to {image_path}")
    else:
        raise Exception(f"Failed: {response.text}")

def run_video_pipeline(topic):
    subprocess.run(["python3", "multipart_pipeline.py", topic])

if __name__ == "__main__":
    topic = "The nature of existence"
    clear_old_images()
    generate_image()
    run_video_pipeline(topic)