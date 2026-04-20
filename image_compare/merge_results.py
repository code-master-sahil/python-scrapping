import csv
import glob

files = glob.glob("outputs/*.csv")

with open("final_output.csv", "w", newline="", encoding="utf-8") as fout:
    writer = csv.writer(fout)
    writer.writerow(["product_id", "competitor_id", "similarity_score"])

    for file in files:
        with open(file, newline='', encoding='utf-8') as fin:
            reader = csv.reader(fin)
            next(reader)  # skip header
            writer.writerows(reader)