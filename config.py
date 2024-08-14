import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# Cloudinary設定
CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')

# Threads API設定
THREADS_AUTH_TOKEN = os.getenv('THREADS_AUTH_TOKEN')

# 画像ペア設定
IMAGE_PAIRS_FOLDER = 'image_pairs'
IMAGE_PAIRS_JSON = 'image_pairs.json'