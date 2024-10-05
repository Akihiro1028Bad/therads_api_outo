import random
import os
import logging
from typing import List, Dict
from base_post import ThreadsClient
from cloudinary_uploader import CloudinaryUploader
from image_pair_manager import ImagePairManager
from config import IMAGE_PAIRS_FOLDER
from reply_poster import ReplyPoster
from config import REPLIES_PARENT_FOLDER

# ロギングの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImagePairPoster:
    def __init__(self, auth_token: str, username: str, image_pairs_folder: str):
        """
        ImagePairPosterクラスのコンストラクタ

        :param auth_token: Threads APIの認証トークン
        """
        self.threads_client = ThreadsClient(auth_token, username)
        self.cloudinary_uploader = CloudinaryUploader()
        self.image_pair_manager = ImagePairManager(image_pairs_folder)
        self.username = username
        self.reply_poster = ReplyPoster(auth_token, username, REPLIES_PARENT_FOLDER)

        logger.info("ImagePairPosterが初期化されました。")

    #def select_random_pair(self) -> Dict[str, str]:
        #"""
        #ランダムに画像ペアを選択する

        #:return: 選択された画像ペアの情報
        #"""
        #pairs = self.image_pair_manager.get_image_pairs()
        #selected_pair = random.choice(pairs)
        #logger.info(f"ランダムに選択された画像ペア: {selected_pair['folder']}")
        #return selected_pair

    def post_image_pair(self) -> str:
        """ランダムに選択した画像ペアを投稿する"""
        post = self.image_pair_manager.get_random_post(self.username)
        if not post:
            raise ValueError(f"No posts available for user: {self.username}")

        try:
            image1_url = self.cloudinary_uploader.upload(post['image1'], self.username)
            image2_url = self.cloudinary_uploader.upload(post['image2'], self.username)

            thread_id = self.threads_client.post_carousel([image1_url, image2_url], post['caption'])
            logger.info(f"画像ペアが正常に投稿されました。スレッドID: {thread_id}")
            return thread_id
        except Exception as e:
            logger.error(f"画像ペアの投稿中にエラーが発生しました: {str(e)}")
            raise

    def post_image_pair_with_reply(self) -> Dict[str, str]:
        """
        ランダムに選択した画像ペアを投稿し、その投稿にリプライする

        :return: 投稿されたスレッドIDと返信IDを含む辞書
        """
        logger.info(f"ユーザー '{self.username}' の画像ペアの投稿とリプライを開始します。")
        result = {
            "username": self.username,
            "status": "success",
            "thread_id": None,
            "reply_id": None
        }

        try:
            # ランダムな投稿を選択
            post = self.image_pair_manager.get_random_post(self.username)
            if not post:
                raise ValueError(f"ユーザー '{self.username}' の投稿が見つかりません。")

            # 画像をアップロード
            image1_url = self.cloudinary_uploader.upload(post['image1'], self.username)
            image2_url = self.cloudinary_uploader.upload(post['image2'], self.username)

            # 画像ペアを投稿
            thread_id = self.threads_client.post_carousel([image1_url, image2_url], post['caption'])
            result["thread_id"] = thread_id
            logger.info(f"ユーザー '{self.username}' の画像ペア投稿が成功しました。スレッドID: {thread_id}")

            # リプライを投稿
            reply_id = self.reply_poster.post_reply(thread_id)
            if reply_id:
                result["reply_id"] = reply_id
                logger.info(f"ユーザー '{self.username}' のリプライが成功しました。リプライID: {reply_id}")
            else:
                logger.info(f"ユーザー '{self.username}' のリプライは行われませんでした。")

        except Exception as e:
            logger.error(f"ユーザー '{self.username}' の処理中にエラーが発生しました: {str(e)}")
            result["status"] = "error"
            result["message"] = str(e)

        return result

# 使用例
if __name__ == "__main__":
    from config import THREADS_AUTH_TOKEN
    poster = ImagePairPoster(THREADS_AUTH_TOKEN)
    thread_id = poster.run()
    print(f"投稿されたスレッドID: {thread_id}")