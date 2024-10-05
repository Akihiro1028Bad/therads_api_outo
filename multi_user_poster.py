import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
from user_manager import UserManager
from image_pair_poster import ImagePairPoster
from reply_poster import ReplyPoster
from image_pair_manager import ImagePairManager
import random
import time
from config import REPLIES_PARENT_FOLDER, IMAGE_PAIRS_FOLDER

# ロギングの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MultiUserPoster:
    def __init__(self, user_manager: UserManager, image_pair_manager: ImagePairManager):
        self.user_manager = user_manager
        self.image_pair_manager = image_pair_manager

    def post_for_all_users(self) -> List[Dict[str, str]]:
        """
        すべてのユーザーに対して投稿を実行する

        :return: 各ユーザーの投稿結果のリスト
        """
        users = self.user_manager.get_users()
        results = []

        # 1分から60分の間でランダムに待機時間を設定
        wait_time = random.randint(60, 3600)  # 60秒（1分）から3600秒（60分）の間
        logger.info(f"投稿開始前に {wait_time} 秒間待機します。")
        #time.sleep(wait_time)

        # アカウントごとに順番に処理を実行
        results = []
        for i, user in enumerate(users):
            try:
                result = self._post_and_reply_for_user(user)
                results.append(result)
                logger.info(f"ユーザー '{user['username']}' の投稿と返信が完了しました。")
            except Exception as exc:
                logger.error(f"ユーザー '{user['username']}' の投稿中にエラーが発生しました: {exc}")
                results.append({"username": user['username'], "status": "error", "message": str(exc)})
            
            # 最後のユーザーでない場合のみ待機
            if i < len(users) - 1:
                wait_time = random.randint(60, 600)  # 60秒（1分）から600秒（10分）の間
                logger.info(f"次のユーザーの処理まで {wait_time} 秒間待機します。")
                #time.sleep(wait_time)

        return results

    def _post_for_user(self, user: Dict[str, str]) -> Dict[str, str]:
        """
        単一ユーザーに対して投稿を実行する

        :param user: ユーザー情報の辞書
        :return: 投稿結果の辞書
        """
        logger.info(f"ユーザー '{user['username']}' の投稿を開始します。")
        try:
            poster = ImagePairPoster(user['access_token'], user['username'])
            thread_id = poster.post_image_pair()
            logger.info(f"ユーザー '{user['username']}' の投稿が成功しました。Thread ID: {thread_id}")
            return {"username": user['username'], "status": "success", "thread_id": thread_id}
        except Exception as e:
            logger.error(f"ユーザー '{user['username']}' の投稿中にエラーが発生しました: {str(e)}")
            return {"username": user['username'], "status": "error", "message": str(e)}


    def _post_and_reply_for_user(self, user: Dict[str, str]) -> Dict[str, str]:
        """
        単一ユーザーに対して投稿と返信を実行する

        :param user: ユーザー情報の辞書
        :return: 投稿と返信の結果を含む辞書
        """
        logger.info(f"ユーザー '{user['username']}' の処理を開始します。")
        result = {
            "username": user['username'],
            "status": "success",
            "thread_id": None,
            "reply_id": None
        }

        try:
            # 画像ペアの投稿
            poster = ImagePairPoster(user['access_token'], user['username'], IMAGE_PAIRS_FOLDER)
            thread_id = poster.post_image_pair()
            result["thread_id"] = thread_id
            logger.info(f"ユーザー '{user['username']}' の画像ペア投稿が成功しました。スレッドID: {thread_id}")

            # リプライフォルダが存在する場合のみ返信を投稿
            if user.get('has_reply_folder', False):
                reply_poster = ReplyPoster(user['access_token'], user['username'], REPLIES_PARENT_FOLDER)
                reply_id = reply_poster.post_reply(thread_id)
                if reply_id:
                    result["reply_id"] = reply_id
                    logger.info(f"ユーザー '{user['username']}' の返信が成功しました。返信ID: {reply_id}")
                else:
                    logger.info(f"ユーザー '{user['username']}' の返信は行われませんでした。")
            else:
                logger.info(f"ユーザー '{user['username']}' はリプライフォルダを持っていないため、返信は行いません。")

        except Exception as e:
            logger.error(f"ユーザー '{user['username']}' の処理中にエラーが発生しました: {str(e)}")
            result["status"] = "error"
            result["message"] = str(e)

        return result


# 使用例
if __name__ == "__main__":
    user_manager = UserManager("users.json")
    multi_poster = MultiUserPoster(user_manager)
    results = multi_poster.post_for_all_users()
    print(results)