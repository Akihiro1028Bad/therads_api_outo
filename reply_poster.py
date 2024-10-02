import logging
import time
from typing import Dict, Optional
import os
from base_post import ThreadsClient
from cloudinary_uploader import CloudinaryUploader

# ロギングの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ReplyPoster:
    def __init__(self, auth_token: str, username: str, replies_parent_folder: str):
        """
        ReplyPosterクラスのコンストラクタ

        :param auth_token: Threads APIの認証トークン
        :param username: ユーザー名
        :param replies_parent_folder: リプライ用フォルダの親フォルダのパス
        """
        self.threads_client = ThreadsClient(auth_token, username)
        self.cloudinary_uploader = CloudinaryUploader()
        self.username = username
        self.replies_parent_folder = replies_parent_folder
        self.reply_folder = os.path.join(replies_parent_folder, username)
        logger.info(f"ReplyPosterが初期化されました。ユーザー: {username}, リプライフォルダ: {self.reply_folder}")

    def _load_reply_content(self) -> Dict[str, Optional[str]]:
        """
        リプライフォルダから返信内容を読み込む

        :return: 返信テキストと画像パスを含む辞書
        """
        reply_text_path = os.path.join(self.reply_folder, 'reply.txt')
        reply_image_path = os.path.join(self.reply_folder, 'reply_image.jpg')

        reply_text = None
        reply_image = None

        # テキストファイルの読み込み
        if os.path.exists(reply_text_path):
            with open(reply_text_path, 'r', encoding='utf-8') as f:
                reply_text = f.read().strip()
            logger.info(f"リプライテキストを読み込みました: {reply_text[:30]}...")
        else:
            logger.warning(f"リプライテキストファイルが見つかりません: {reply_text_path}")

        # 画像ファイルの確認
        if os.path.exists(reply_image_path):
            reply_image = reply_image_path
            logger.info(f"リプライ画像を見つけました: {reply_image}")
        else:
            logger.info("リプライ画像が見つかりません。テキストのみの返信を行います。")

        return {"text": reply_text, "image_path": reply_image}

    def post_reply(self, thread_id: str) -> Optional[str]:
        """
        指定されたスレッドに返信を投稿する

        :param thread_id: 返信先のスレッドID
        :return: 投稿された返信のID、またはNone（リプライフォルダが存在しない場合）
        """
        if not os.path.exists(self.reply_folder):
            logger.info(f"ユーザー '{self.username}' のリプライフォルダが見つかりません。リプライは行いません。")
            return None

        logger.info(f"返信の投稿を開始: スレッドID={thread_id}")
        
        reply_content = self._load_reply_content()
        
        if not reply_content['text']:
            logger.error("返信テキストが見つかりません。返信を投稿できません。")
            return None

        image_url = None
        if reply_content['image_path']:
            try:
                image_url = self.cloudinary_uploader.upload(reply_content['image_path'], self.username)
                logger.info(f"画像のアップロードに成功しました: {image_url}")
            except Exception as e:
                logger.error(f"画像のアップロード中にエラーが発生しました: {str(e)}")
                # 画像アップロードに失敗しても、テキストのみで返信を続行
                logger.info("画像なしで返信を続行します。")

        try:
            reply_container_id = self.threads_client.create_reply(thread_id, reply_content['text'], image_url)
            logger.info("返信コンテナの作成に成功しました。公開前に30秒待機します。")
            time.sleep(30)  # サーバーの処理を待機

            reply_id = self.threads_client.publish_reply(reply_container_id)
            logger.info(f"返信の投稿に成功しました。返信ID: {reply_id}")
            return reply_id
        except Exception as e:
            logger.error(f"返信の投稿中にエラーが発生しました: {str(e)}")
            raise

# 使用例
if __name__ == "__main__":
    from config import THREADS_AUTH_TOKEN
    reply_poster = ReplyPoster(THREADS_AUTH_TOKEN, "test_user")
    thread_id = "existing_thread_id"  # 既存の投稿のIDを指定
    reply_id = reply_poster.post_reply(thread_id, "これは返信テストです。", "path/to/image.jpg")
    print(f"返信ID: {reply_id}")