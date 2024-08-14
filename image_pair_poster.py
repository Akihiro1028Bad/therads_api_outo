import random
import os
import logging
from base_post import ThreadsClient
from cloudinary_uploader import CloudinaryUploader
from image_pair_manager import ImagePairManager
from config import THREADS_AUTH_TOKEN, IMAGE_PAIRS_FOLDER

# ロギングの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImagePairPoster:
    def __init__(self):
        self.threads_client = ThreadsClient(THREADS_AUTH_TOKEN)
        self.cloudinary_uploader = CloudinaryUploader()
        self.image_pair_manager = ImagePairManager()
        logger.info("ImagePairPoster initialized")

    def select_random_pair(self):
        """ランダムに画像ペアを選択する"""
        pairs = self.image_pair_manager.get_image_pairs()
        selected_pair = random.choice(pairs)
        logger.info(f"Randomly selected pair: {selected_pair['folder']}")
        return selected_pair

    def post_image_pair(self):
        """画像ペアを選択、アップロード、投稿する"""
        pair = self.select_random_pair()
        folder = pair['folder']
        caption = pair['caption']

        image1_path = os.path.join(IMAGE_PAIRS_FOLDER, folder, 'image1.jpg')
        image2_path = os.path.join(IMAGE_PAIRS_FOLDER, folder, 'image2.jpg')

        try:
            image1_url = self.cloudinary_uploader.upload(image1_path)
            image2_url = self.cloudinary_uploader.upload(image2_path)

            # ThreadsClientを使用してカルーセル投稿
            thread_id = self.threads_client.post_carousel([image1_url, image2_url], caption)
            logger.info(f"Image pair posted successfully. Thread ID: {thread_id}")
            return thread_id
        except Exception as e:
            logger.error(f"Error posting image pair: {str(e)}")
            raise

    def run(self):
        """メイン実行関数"""
        try:
            self.image_pair_manager.update_json()  # JSONファイルを更新
            thread_id = self.post_image_pair()
            logger.info(f"Process completed successfully. Thread ID: {thread_id}")
        except Exception as e:
            logger.error(f"Error in run process: {str(e)}")