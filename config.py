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

# ユーザー名を画像に印字する機能のオン/オフ
WATERMARK_USERNAME = False

# ユーザー名の印字位置（中心からの相対位置）
WATERMARK_POSITION = {
    'x': 0.6,  # 中心からやや右に
    'y': 0.5   # 垂直方向の中央
}

# ユーザー名の印字スタイル
WATERMARK_STYLE = {
    'font_size': 20,
    'font_color': 'white',
    'opacity': 70
}

REPLIES_PARENT_FOLDER = 'user_replies'