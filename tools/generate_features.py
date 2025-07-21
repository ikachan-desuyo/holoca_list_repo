import json
import cv2
import numpy as np
import requests
from io import BytesIO
from PIL import Image
from tqdm import tqdm
import os
import glob

CARD_DATA_PATH = '../json_file/card_data.json'
OUTPUT_DIR = '../public/'
BASE_FILENAME = 'features'
MAX_FILE_SIZE = 50 * 1024 * 1024

# 既存features*.jsonをすべて読み込む
existing_features = []
existing_names = set()
for path in sorted(glob.glob(os.path.join(OUTPUT_DIR, f'{BASE_FILENAME}*.json'))):
    with open(path, encoding='utf-8') as f:
        feats = json.load(f)
        existing_features.extend(feats)
        for feat in feats:
            existing_names.add(feat['name'])

print(f"既存features: {len(existing_features)}件")

# カードデータの読み込み
with open(CARD_DATA_PATH, encoding='utf-8') as f:
    card_data = json.load(f)

new_features = []
for card_id, card in tqdm(card_data.items()):
    name = card['name']
    image_url = card['image_url']

    if name in existing_names:
        continue  # 既存ならスキップ

    # 画像ダウンロード
    try:
        resp = requests.get(image_url, timeout=10)
        img = Image.open(BytesIO(resp.content)).convert('RGB')
        img_np = np.array(img)
        img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"画像取得失敗: {name} ({image_url}) {e}")
        continue

    # グレースケール変換
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

    # ORB特徴点・特徴量抽出
    orb = cv2.ORB_create()
    kps, descs = orb.detectAndCompute(gray, None)

    if descs is None or len(kps) == 0:
        print(f"特徴点抽出失敗: {name}")
        continue

    keypoints = [[float(kp.pt[0]), float(kp.pt[1]), kp.size, kp.angle, kp.response, kp.octave, kp.class_id] for kp in kps]
    descriptors = descs.tolist()

    card_feature = {
        "name": name,
        "image_url": image_url,
        "keypoints": keypoints,
        "descriptors": descriptors
    }
    new_features.append(card_feature)

print(f"新規features: {len(new_features)}件")

# 既存＋新規をまとめて分割保存
all_features = existing_features + new_features
file_count = 1
features_chunk = []

def save_features_chunk(features, file_count):
    out_path = os.path.join(OUTPUT_DIR, f'{BASE_FILENAME}{file_count}.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(features, f, ensure_ascii=False, indent=2)
    print(f"Saved {out_path} ({len(features)} cards)")

total = len(all_features)
for idx, feat in enumerate(all_features, 1):
    temp_features = features_chunk + [feat]
    temp_json = json.dumps(temp_features, ensure_ascii=False, indent=2)
    temp_size = len(temp_json.encode('utf-8'))
    if temp_size > MAX_FILE_SIZE and features_chunk:
        save_features_chunk(features_chunk, file_count)
        file_count += 1
        features_chunk = [feat]
        print(f"分割ファイル{file_count-1}まで保存完了 ({idx-1}/{total}件)")
    else:
        features_chunk.append(feat)
    # 進捗表示（100件ごと）
    if idx % 100 == 0 or idx == total:
        print(f"分割処理進捗: {idx}/{total}件")

if features_chunk:
    save_features_chunk(features_chunk, file_count)
    print(f"分割ファイル{file_count}まで保存完了 ({total}/{total}件)")

print(f"Done! {file_count} files generated.")