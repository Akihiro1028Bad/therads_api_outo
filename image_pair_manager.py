import os
import json
import logging
from config import IMAGE_PAIRS_FOLDER, IMAGE_PAIRS_JSON

# ロギングの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImagePairManager:
    def __init__(self):
        self.image_pairs_folder = IMAGE_PAIRS_FOLDER
        self.image_pairs_json = IMAGE_PAIRS_JSON

    def read_caption(self, folder_path):
        """フォルダ内のcaption.txtファイルからキャプションを読み取る"""
        caption_file = os.path.join(folder_path, 'caption.txt')
        try:
            with open(caption_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            logger.warning(f"Caption file not found in {folder_path}. Using default caption.")
            return f"This is a default caption for {os.path.basename(folder_path)}"
        except Exception as e:
            logger.error(f"Error reading caption file in {folder_path}: {str(e)}")
            return f"This is a default caption for {os.path.basename(folder_path)}"

    def scan_image_pairs(self):
        """image_pairsフォルダをスキャンし、画像ペア情報を取得する"""
        image_pairs = []
        for folder_name in os.listdir(self.image_pairs_folder):
            folder_path = os.path.join(self.image_pairs_folder, folder_name)
            if os.path.isdir(folder_path):
                if 'image1.jpg' in os.listdir(folder_path) and 'image2.jpg' in os.listdir(folder_path):
                    caption = self.read_caption(folder_path)
                    image_pairs.append({
                        "folder": folder_name,
                        "caption": caption
                    })
        logger.info(f"Scanned {len(image_pairs)} image pairs from {self.image_pairs_folder}")
        return image_pairs

    def update_json(self):
        """JSONファイルを更新する"""
        image_pairs = self.scan_image_pairs()
        try:
            with open(self.image_pairs_json, 'w', encoding='utf-8') as f:
                json.dump(image_pairs, f, indent=2, ensure_ascii=False)
            logger.info(f"Updated {self.image_pairs_json} with {len(image_pairs)} image pairs")
        except Exception as e:
            logger.error(f"Error updating JSON file: {str(e)}")
            raise

    def get_image_pairs(self):
        """JSONファイルから画像ペア情報を読み込む"""
        try:
            with open(self.image_pairs_json, 'r', encoding='utf-8') as f:
                pairs = json.load(f)
            logger.info(f"Loaded {len(pairs)} image pairs from {self.image_pairs_json}")
            return pairs
        except FileNotFoundError:
            logger.warning(f"{self.image_pairs_json} not found. Creating new file.")
            self.update_json()
            return self.get_image_pairs()
        except Exception as e:
            logger.error(f"Error loading image pairs: {str(e)}")
            raise