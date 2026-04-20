import os
import csv
import requests
from PIL import Image
from io import BytesIO
import numpy as np
import cv2
from skimage.metrics import structural_similarity as ssim

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHUNK_DIR = os.path.join(BASE_DIR, "chunks")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

INPUT_FILE = os.environ.get("INPUT_FILE")


def download_image(url):
    try:
        r = requests.get(url, timeout=10)
        return Image.open(BytesIO(r.content)).convert("RGB")
    except:
        return None


def preprocess(img):
    img = np.array(img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    img = cv2.resize(img, (256, 256))
    return img


def compare(img1, img2):
    try:
        img1 = preprocess(img1)
        img2 = preprocess(img2)
        score, _ = ssim(img1, img2, full=True)
        return round(score, 4)
    except:
        return -1


def match_flag(score):
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
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    input_path = os.path.join(CHUNK_DIR, INPUT_FILE)
    output_path = os.path.join(OUTPUT_DIR, f"output_{INPUT_FILE}")

    results = []

    with open(input_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            img1 = download_image(row['competitor_image_url'])
            img2 = download_image(row['1sb_image_url'])

            score = compare(img1, img2) if img1 and img2 else -1

            results.append([
                row['product_id'],
                row['competitor_id'],
                row['brand_id'],
                row['competitor_image_url'],
                row['1sb_image_url'],
                score,
                match_flag(score)
            ])

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "product_id",
            "competitor_id",
            "brand_id",
            "competitor_image_url",
            "1sb_image_url",
            "ssim_score",
            "match_type"
        ])
        writer.writerows(results)


if __name__ == "__main__":
    process()