import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
from user_manager import UserManager
from image_pair_poster import ImagePairPoster

# ロギングの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MultiUserPoster:
    def __init__(self, user_manager: UserManager):
        """
        MultiUserPosterクラスのコンストラクタ

        :param user_manager: UserManagerインスタンス
        """
        self.user_manager = user_manager

    def post_for_all_users(self) -> List[Dict[str, str]]:
        """
        すべてのユーザーに対して投稿を実行する

        :return: 各ユーザーの投稿結果のリスト
        """
        users = self.user_manager.get_users()
        results = []

        # ThreadPoolExecutorを使用して並列処理を実行
        with ThreadPoolExecutor(max_workers=1) as executor:
            future_to_user = {executor.submit(self._post_for_user, user): user for user in users}
            for future in as_completed(future_to_user):
                user = future_to_user[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    logger.error(f"ユーザー '{user['username']}' の投稿中にエラーが発生しました: {exc}")
                    results.append({"username": user['username'], "status": "error", "message": str(exc)})

        return results

    def _post_for_user(self, user: Dict[str, str]) -> Dict[str, str]:
        """
        単一ユーザーに対して投稿を実行する

        :param user: ユーザー情報の辞書
        :return: 投稿結果の辞書
        """
        logger.info(f"ユーザー '{user['username']}' の投稿を開始します。")
        try:
            poster = ImagePairPoster(user['access_token'])
            thread_id = poster.post_image_pair()
            logger.info(f"ユーザー '{user['username']}' の投稿が成功しました。Thread ID: {thread_id}")
            return {"username": user['username'], "status": "success", "thread_id": thread_id}
        except Exception as e:
            logger.error(f"ユーザー '{user['username']}' の投稿中にエラーが発生しました: {str(e)}")
            return {"username": user['username'], "status": "error", "message": str(e)}

# 使用例
if __name__ == "__main__":
    user_manager = UserManager("users.json")
    multi_poster = MultiUserPoster(user_manager)
    results = multi_poster.post_for_all_users()
    print(results)