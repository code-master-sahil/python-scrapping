import os
import csv
import requests
from PIL import Image
from io import BytesIO
import imagehash

INPUT_FILE = os.environ.get("INPUT_FILE", "input.csv")
OUTPUT_FILE = os.environ.get("OUTPUT_FILE", "output.csv")

START = int(os.environ.get("START", 0))
END = int(os.environ.get("END", 0))


def download_image(url):
    try:
        response = requests.get(url, timeout=10)
        return Image.open(BytesIO(response.content)).convert("RGB")
    except:
        return None


def compare_images(img1, img2):
    try:
        hash1 = imagehash.phash(img1)
        hash2 = imagehash.phash(img2)
        return hash1 - hash2  # lower = more similar
    except:
        return -1


def process():
    results = []

    with open(INPUT_FILE, newline='', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))
        subset = reader[START:END]

        for row in subset:
            product_id = row['product_id']
            competitor_id = row['competitor_id']
            comp_url = row['competitor_image_url']
            sb_url = row['1sb_image_url']

            img1 = download_image(comp_url)
            img2 = download_image(sb_url)

            if img1 and img2:
                score = compare_images(img1, img2)
            else:
                score = -1

            results.append([
                product_id,
                competitor_id,
                score
            ])

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["product_id", "competitor_id", "similarity_score"])
        writer.writerows(results)


if __name__ == "__main__":
    process()