import json
import logging
from typing import List, Dict
import os

# ロギングの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UserManager:
    def __init__(self, users_file: str, replies_parent_folder: str):
        """
        UserManagerクラスのコンストラクタ

        :param users_file: ユーザー情報が格納されているJSONファイルのパス
        :param replies_parent_folder: リプライ用フォルダの親フォルダのパス
        """
        self.users_file = users_file
        self.replies_parent_folder = replies_parent_folder
        self.users: List[Dict[str, str]] = []
        self._load_users()

    def _load_users(self) -> None:
        """
        JSONファイルからユーザー情報を読み込み、リプライフォルダの存在を確認する
        """
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                self.users = json.load(f)
            logger.info(f"{len(self.users)}人のユーザー情報を正常に読み込みました。")
            
            # リプライの親フォルダが存在しない場合は作成
            if not os.path.exists(self.replies_parent_folder):
                os.makedirs(self.replies_parent_folder)
                logger.info(f"リプライの親フォルダを作成しました: {self.replies_parent_folder}")

            # 各ユーザーのリプライフォルダの存在を確認
            for user in self.users:
                reply_folder = os.path.join(self.replies_parent_folder, user['username'])
                if os.path.exists(reply_folder):
                    user['has_reply_folder'] = True
                    logger.info(f"ユーザー '{user['username']}' のリプライフォルダが見つかりました: {reply_folder}")
                else:
                    user['has_reply_folder'] = False
                    logger.info(f"ユーザー '{user['username']}' のリプライフォルダが見つかりません。リプライは行いません。")

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