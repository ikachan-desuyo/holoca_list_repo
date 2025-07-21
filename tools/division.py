import json
import os

INPUT_PATH = '../public/_features4.json'
OUTPUT_DIR = 'public/'
BASE_FILENAME = 'features'
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(INPUT_PATH, encoding='utf-8') as f:
    data = json.load(f)

# 1件あたりの平均サイズをサンプルで計算
sample_n = min(100, len(data))
sample_json = json.dumps(data[:sample_n], ensure_ascii=False, indent=2)
avg_size = len(sample_json.encode('utf-8')) / sample_n
max_count = max(1, int(MAX_FILE_SIZE // avg_size))

print(f"1ファイルあたり最大{max_count}件で分割します")

file_count = 1
total = len(data)
for i in range(0, total, max_count):
    chunk = data[i:i+max_count]
    out_path = os.path.join(OUTPUT_DIR, f'{BASE_FILENAME}{file_count}.json')
    with open(out_path, 'w', encoding='utf-8') as f_out:
        json.dump(chunk, f_out, ensure_ascii=False, indent=2)
    print(f"Saved {out_path} ({len(chunk)} items, {min(i+len(chunk), total)}/{total})")
    file_count += 1

print(f"Done! {file_count-1} files generated.")