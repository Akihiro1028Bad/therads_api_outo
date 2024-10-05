import os
import json
import logging
from config import IMAGE_PAIRS_FOLDER, IMAGE_PAIRS_JSON
import random
from typing import List, Dict

# ロギングの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImagePairManager:
    def __init__(self, image_pairs_folder: str):
        self.image_pairs_folder = image_pairs_folder


    def get_user_posts(self, username: str) -> List[Dict[str, str]]:
        """指定されたユーザーの全ての投稿を取得する"""
        user_folder = os.path.join(self.image_pairs_folder, username)
        posts = []
        if os.path.exists(user_folder):
            for post_folder in os.listdir(user_folder):
                post_path = os.path.join(user_folder, post_folder)
                if os.path.isdir(post_path):
                    post = self._load_post(post_path)
                    if post:
                        posts.append(post)
        return posts
    
    def _load_post(self, post_path: str) -> Dict[str, str]:
        """投稿フォルダから投稿情報を読み込む"""
        caption_file = os.path.join(post_path, 'caption.txt')
        image1_file = os.path.join(post_path, 'image1.jpg')
        image2_file = os.path.join(post_path, 'image2.jpg')

        if os.path.exists(caption_file) and os.path.exists(image1_file) and os.path.exists(image2_file):
            with open(caption_file, 'r', encoding='utf-8') as f:
                caption = f.read().strip()
            return {
                "caption": caption,
                "image1": image1_file,
                "image2": image2_file
            }
        else:
            logger.warning(f"Invalid post folder structure: {post_path}")
            return {}
        
    def get_random_post(self, username: str) -> Dict[str, str]:
        """指定されたユーザーのランダムな投稿を取得する"""
        posts = self.get_user_posts(username)
        if posts:
            return random.choice(posts)
        else:
            logger.warning(f"No posts found for user: {username}")
            return {}

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

    #def update_json(self):
        #"""JSONファイルを更新する"""
        #image_pairs = self.scan_image_pairs()
        #try:
            #with open(self.image_pairs_json, 'w', encoding='utf-8') as f:
                #json.dump(image_pairs, f, indent=2, ensure_ascii=False)
            #logger.info(f"Updated {self.image_pairs_json} with {len(image_pairs)} image pairs")
        #except Exception as e:
            #logger.error(f"Error updating JSON file: {str(e)}")
            #raise

    #def get_image_pairs(self):
        #"""JSONファイルから画像ペア情報を読み込む"""
        #try:
            #with open(self.image_pairs_json, 'r', encoding='utf-8') as f:
                #pairs = json.load(f)
            #logger.info(f"Loaded {len(pairs)} image pairs from {self.image_pairs_json}")
            #return pairs
        #except FileNotFoundError:
            #logger.warning(f"{self.image_pairs_json} not found. Creating new file.")
            #self.update_json()
            #return self.get_image_pairs()
        #except Exception as e:
            #logger.error(f"Error loading image pairs: {str(e)}")
            #raise