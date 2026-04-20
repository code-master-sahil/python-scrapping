import csv
import glob

files = glob.glob("outputs/**/*.csv", recursive=True)

with open("final_output.csv", "w", newline="", encoding="utf-8") as fout:
    writer = csv.writer(fout)
    writer.writerow([
        "product_id",
        "competitor_id",
        "brand_id",
        "competitor_image_url",
        "1sb_image_url",
        "ssim_score",
        "match_type"
    ])

    for file in files:
        if "output_" not in file:
            continue

        with open(file, newline='', encoding='utf-8') as fin:
            reader = csv.reader(fin)
            next(reader, None)
            writer.writerows(reader)