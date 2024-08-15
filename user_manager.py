import json
import logging
from typing import List, Dict

# ロギングの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UserManager:
    def __init__(self, users_file: str):
        """
        UserManagerクラスのコンストラクタ

        :param users_file: ユーザー情報が格納されているJSONファイルのパス
        """
        self.users_file = users_file
        self.users: List[Dict[str, str]] = []
        self._load_users()

    def _load_users(self) -> None:
        """
        JSONファイルからユーザー情報を読み込む
        """
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                self.users = json.load(f)
            logger.info(f"{len(self.users)}人のユーザー情報を正常に読み込みました。")
        except FileNotFoundError:
            logger.error(f"ユーザーファイル '{self.users_file}' が見つかりません。")
            raise
        except json.JSONDecodeError:
            logger.error(f"ユーザーファイル '{self.users_file}' の解析に失敗しました。正しいJSON形式であることを確認してください。")
            raise

    def get_users(self) -> List[Dict[str, str]]:
        """
        ユーザーリストを返す

        :return: ユーザー情報のリスト
        """
        return self.users

    def add_user(self, username: str, access_token: str) -> None:
        """
        新しいユーザーを追加する

        :param username: ユーザー名
        :param access_token: アクセストークン
        """
        new_user = {"username": username, "access_token": access_token}
        self.users.append(new_user)
        self._save_users()
        logger.info(f"新しいユーザー '{username}' を追加しました。")

    def remove_user(self, username: str) -> None:
        """
        指定されたユーザーを削除する

        :param username: 削除するユーザーの名前
        """
        self.users = [user for user in self.users if user["username"] != username]
        self._save_users()
        logger.info(f"ユーザー '{username}' を削除しました。")

    def _save_users(self) -> None:
        """
        ユーザー情報をJSONファイルに保存する
        """
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, indent=2, ensure_ascii=False)
            logger.info(f"ユーザー情報を '{self.users_file}' に保存しました。")
        except IOError:
            logger.error(f"ユーザー情報の保存中にエラーが発生しました。")
            raise

# 使用例
if __name__ == "__main__":
    user_manager = UserManager("users.json")
    print(user_manager.get_users())
    user_manager.add_user("new_user", "new_token")
    print(user_manager.get_users())
    user_manager.remove_user("new_user")
    print(user_manager.get_users())