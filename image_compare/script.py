import os
import csv
import requests
from PIL import Image
from io import BytesIO
import numpy as np
import cv2
from skimage.metrics import structural_similarity as ssim

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, "input.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "output.csv")

START = int(os.environ.get("START", 0))
END = int(os.environ.get("END", 0))


def download_image(url):
    try:
        response = requests.get(url, timeout=10)
        return Image.open(BytesIO(response.content)).convert("RGB")
    except:
        return None


def preprocess_image(pil_img, size=(256, 256)):
    """Convert PIL → grayscale numpy + resize"""
    img = np.array(pil_img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    img = cv2.resize(img, size)
    return img


def compare_images_ssim(img1, img2):
    try:
        img1 = preprocess_image(img1)
        img2 = preprocess_image(img2)

        score, _ = ssim(img1, img2, full=True)
        return round(score, 4)  # 0 to 1
    except:
        return -1


def get_match_flag(score):
    """Adjust threshold based on your data"""
    if score == -1:
        return "ERROR"
    elif score >= 0.95:
        return "EXACT"
    elif score >= 0.85:
        return "SIMILAR"
    elif score >= 0.70:
        return "PARTIAL"
    else:
        return "DIFFERENT"


def process():
    results = []

    with open(INPUT_FILE, newline='', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))
        subset = reader[START:END] if END > 0 else reader

        for row in subset:
            product_id = row['product_id']
            competitor_id = row['competitor_id']
            comp_url = row['competitor_image_url']
            sb_url = row['1sb_image_url']

            img1 = download_image(comp_url)
            img2 = download_image(sb_url)

            if img1 and img2:
                score = compare_images_ssim(img1, img2)
            else:
                score = -1

            match_flag = get_match_flag(score)

            results.append([
                product_id,
                competitor_id,
                score,
                match_flag
            ])

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "product_id",
            "competitor_id",
            "ssim_score",
            "match_type"
        ])
        writer.writerows(results)


if __name__ == "__main__":
    process()