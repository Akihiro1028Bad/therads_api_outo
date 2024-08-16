import random
import os
import logging
from typing import List, Dict
from base_post import ThreadsClient
from cloudinary_uploader import CloudinaryUploader
from image_pair_manager import ImagePairManager
from config import IMAGE_PAIRS_FOLDER

# ロギングの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImagePairPoster:
    def __init__(self, auth_token: str, username: str):
        """
        ImagePairPosterクラスのコンストラクタ

        :param auth_token: Threads APIの認証トークン
        """
        self.threads_client = ThreadsClient(auth_token, username)
        self.cloudinary_uploader = CloudinaryUploader()
        self.image_pair_manager = ImagePairManager()
        logger.info("ImagePairPosterが初期化されました。")

    def select_random_pair(self) -> Dict[str, str]:
        """
        ランダムに画像ペアを選択する

        :return: 選択された画像ペアの情報
        """
        pairs = self.image_pair_manager.get_image_pairs()
        selected_pair = random.choice(pairs)
        logger.info(f"ランダムに選択された画像ペア: {selected_pair['folder']}")
        return selected_pair

    def post_image_pair(self) -> str:
        """
        画像ペアを選択、アップロード、投稿する

        :return: 投稿されたスレッドのID
        """
        pair = self.select_random_pair()
        folder = pair['folder']
        caption = pair['caption']
        username = self.threads_client.username  # ユーザー名を取得

        image1_path = os.path.join(IMAGE_PAIRS_FOLDER, folder, 'image1.jpg')
        image2_path = os.path.join(IMAGE_PAIRS_FOLDER, folder, 'image2.jpg')

        try:
            image1_url = self.cloudinary_uploader.upload(image1_path, username)
            image2_url = self.cloudinary_uploader.upload(image2_path, username)

            # ThreadsClientを使用してカルーセル投稿
            thread_id = self.threads_client.post_carousel([image1_url, image2_url], caption)
            logger.info(f"画像ペアが正常に投稿されました。スレッドID: {thread_id}")
            return thread_id
        except Exception as e:
            logger.error(f"画像ペアの投稿中にエラーが発生しました: {str(e)}")
            raise

    def run(self) -> str:
        """
        メイン実行関数

        :return: 投稿されたスレッドのID
        """
        try:
            self.image_pair_manager.update_json()  # JSONファイルを更新
            thread_id = self.post_image_pair()
            logger.info(f"処理が正常に完了しました。スレッドID: {thread_id}")
            return thread_id
        except Exception as e:
            logger.error(f"実行プロセス中にエラーが発生しました: {str(e)}")
            raise

# 使用例
if __name__ == "__main__":
    from config import THREADS_AUTH_TOKEN
    poster = ImagePairPoster(THREADS_AUTH_TOKEN)
    thread_id = poster.run()
    print(f"投稿されたスレッドID: {thread_id}")