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
    prompt = (
        "Franz Kafka and Friedrich Nietzsche sitting across from each other "
        "at a wooden table, deep in an intense philosophical debate, dramatic "
        "moody lighting, dark academic study background, oil painting style, "
        "highly detailed, expressive faces"
    )
    response = requests.post(
        N8N_WEBHOOK,
        json={"prompt": prompt},
        timeout=120
    )
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
    topic = "Does suffering make you stronger—or destroy you?"
    clear_old_images()
    generate_image()
    run_video_pipeline(topic)