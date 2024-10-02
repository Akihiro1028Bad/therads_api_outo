import requests
import logging
import json
import time

# ログの設定
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ThreadsClient:
    """
    Threads APIクライアントクラス
    
    このクラスは、Threads APIとの対話を管理し、画像投稿やカルーセル投稿などの
    機能を提供します。
    """

    def __init__(self, auth_token, username):
        """
        ThreadsClientの初期化
        
        :param auth_token: API認証用のトークン
        """
        self.auth_token = auth_token
        self.username = username
        self.base_url = 'https://graph.threads.net/v1.0'
        logger.info("ThreadsClient初期化完了")

    def _request(self, method, endpoint, params=None, data=None):
        """
        APIリクエストを送信する内部メソッド
        
        :param method: HTTPメソッド（GET, POST等）
        :param endpoint: APIエンドポイント
        :param params: GETパラメータ（オプション）
        :param data: POSTデータ（オプション）
        :return: APIレスポンスのJSONデータ
        """
        url = f"{self.base_url}/{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'application/json'
        }
        params = params or {}
        params['access_token'] = self.auth_token

        logger.info(f"送信 {method} リクエスト: {url}")
        logger.debug(f"パラメータ: {json.dumps(params, indent=2, ensure_ascii=False)}")
        if data:
            logger.debug(f"データ: {json.dumps(data, indent=2, ensure_ascii=False)}")

        try:
            response = requests.request(method, url, params=params, json=data, headers=headers)
            response.raise_for_status()
            logger.info(f"リクエスト成功. ステータスコード: {response.status_code}")
            logger.debug(f"レスポンス: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"リクエスト失敗: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"レスポンス内容: {e.response.text}")
            raise

    def create_media_container(self, media_type, image_url=None, video_url=None, text=None, is_carousel_item=False):
        """
        メディアコンテナを作成
        
        :param media_type: メディアタイプ（IMAGE, VIDEO, TEXT）
        :param image_url: 画像URL（画像の場合）
        :param video_url: 動画URL（動画の場合）
        :param text: 投稿テキスト
        :param is_carousel_item: カルーセルアイテムかどうか
        :return: 作成されたメディアコンテナのID
        """
        params = {
            'media_type': media_type,
            'is_carousel_item': 'true' if is_carousel_item else 'false'
        }
        if image_url:
            params['image_url'] = image_url
        if video_url:
            params['video_url'] = video_url
        if text:
            params['text'] = text

        logger.info(f"メディアコンテナ作成: タイプ={media_type}, カルーセルアイテム={is_carousel_item}")
        response = self._request('POST', f'/me/threads', params=params)
        logger.info(f"メディアコンテナ作成成功. ID: {response['id']}")
        return response['id']

    def create_carousel_container(self, children_ids, text=None):
        """
        カルーセルコンテナを作成
        
        :param children_ids: 子アイテムのID一覧
        :param text: 投稿テキスト
        :return: 作成されたカルーセルコンテナのID
        """
        params = {
            'media_type': 'CAROUSEL',
            'children': ','.join(children_ids)
        }
        if text:
            params['text'] = text

        logger.info(f"カルーセルコンテナ作成: 子アイテム数={len(children_ids)}")
        response = self._request('POST', f'/me/threads', params=params)
        logger.info(f"カルーセルコンテナ作成成功. ID: {response['id']}")
        return response['id']

    def publish_thread(self, container_id):
        """
        スレッドを公開
        
        :param container_id: 公開するコンテナのID
        :return: 公開されたスレッドのID
        """
        params = {'creation_id': container_id}
        logger.info(f"スレッド公開: コンテナID={container_id}")
        response = self._request('POST', f'/me/threads_publish', params=params)
        logger.info(f"スレッド公開成功. ID: {response['id']}")
        return response['id']

    def post_single_image(self, image_url, text=None):
        """
        単一画像の投稿
        
        :param image_url: 画像URL
        :param text: 投稿テキスト
        :return: 公開されたスレッドのID
        """
        logger.info(f"単一画像投稿開始: URL={image_url}")
        container_id = self.create_media_container('IMAGE', image_url=image_url, text=text)
        logger.info("サーバーの処理を待機中（30秒）")
        time.sleep(30)  # サーバーの処理を待機
        thread_id = self.publish_thread(container_id)
        logger.info(f"単一画像投稿完了. スレッドID: {thread_id}")
        return thread_id

    def post_carousel(self, image_urls, text=None):
        """
        カルーセル投稿
        
        :param image_urls: 画像URLのリスト
        :param text: 投稿テキスト
        :return: 公開されたカルーセルスレッドのID
        """
        if len(image_urls) < 2 or len(image_urls) > 10:
            logger.error(f"無効な画像数: {len(image_urls)}. カルーセルは2-10枚の画像が必要です。")
            raise ValueError("カルーセルは2-10枚の画像が必要です")

        logger.info(f"カルーセル投稿開始: 画像数={len(image_urls)}")
        children_ids = []
        for i, url in enumerate(image_urls):
            logger.info(f"カルーセルアイテム {i+1}/{len(image_urls)} 作成中")
            child_id = self.create_media_container('IMAGE', image_url=url, is_carousel_item=True)
            children_ids.append(child_id)
            logger.info("カルーセルアイテム間の短い待機（5秒）")
            time.sleep(5)  # アイテム作成間の短い待機

        carousel_id = self.create_carousel_container(children_ids, text)
        logger.info("サーバーの処理を待機中（30秒）")
        time.sleep(30)  # サーバーの処理を待機
        thread_id = self.publish_thread(carousel_id)
        logger.info(f"カルーセル投稿完了. スレッドID: {thread_id}")
        return thread_id

    def create_reply(self, reply_to_id: str, text: str, image_url: str = None) -> str:
        """
        返信コンテナを作成する

        :param reply_to_id: 返信先の投稿ID
        :param text: 返信テキスト
        :param image_url: 画像URL（オプション）
        :return: 作成された返信コンテナのID
        """
        logger.info(f"返信コンテナの作成を開始: 返信先ID={reply_to_id}")
        params = {
            'media_type': 'IMAGE' if image_url else 'TEXT',
            'text': text,
            'reply_to_id': reply_to_id
        }
        if image_url:
            params['image_url'] = image_url

        response = self._request('POST', f'/me/threads', params=params)
        logger.info(f"返信コンテナの作成が成功しました。ID: {response['id']}")
        return response['id']

    def publish_reply(self, container_id: str) -> str:
        """
        返信を公開する

        :param container_id: 公開する返信コンテナのID
        :return: 公開された返信のID
        """
        logger.info(f"返信の公開を開始: コンテナID={container_id}")
        params = {'creation_id': container_id}
        response = self._request('POST', f'/me/threads_publish', params=params)
        logger.info(f"返信の公開が成功しました。ID: {response['id']}")
        return response['id']

# 使用例
if __name__ == "__main__":
    client = ThreadsClient("THQWJYTWRGUE80Y1gyZAFkyTUgzS1NIaXNTU0QyZA29rd2JZAM3NWQlp1TmxyMGUtaGlvS1VMTWZAjUFJTbEg2cS1zb0cxTW9xVnF4X0RsMHJNRHVqZAzhGb20xTnJRdldNcm5VQ2czdkNVMHZA2R1FabXRWMFRIWnBmTUZALVFNVcWUzRzFsMmNYNnB3")

    try:
        # 単一の画像投稿
        single_image_id = client.post_single_image(
            "https://res.cloudinary.com/dbjqazddo/image/upload/v1723156706/samples/landscapes/beach-boat.jpg",
            "素敵な景色です！ #beautiful"
        )
        logger.info(f"単一画像投稿成功. ID: {single_image_id}")

        # カルーセル投稿
        carousel_id = client.post_carousel(
            [
                "https://res.cloudinary.com/dbjqazddo/image/upload/v1723156706/samples/people/bicycle.jpg",
                "https://res.cloudinary.com/dbjqazddo/image/upload/v1723156706/samples/landscapes/beach-boat.jpg",
                "https://res.cloudinary.com/dbjqazddo/image/upload/v1723156706/samples/landscapes/architecture-signs.jpg"
            ],
            "美しい風景の数々 #landscapes"
        )
        logger.info(f"カルーセル投稿成功. ID: {carousel_id}")

    except Exception as e:
        logger.error(f"エラーが発生しました: {e}")