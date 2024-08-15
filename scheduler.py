import schedule
import time
import json
import logging
from typing import List, Dict
from datetime import datetime, timedelta
from multi_user_poster import MultiUserPoster
from user_manager import UserManager

# ロギングの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Scheduler:
    def __init__(self, config_file: str, user_manager: UserManager):
        """
        Schedulerクラスのコンストラクタ

        :param config_file: スケジュール設定が格納されているJSONファイルのパス
        :param user_manager: UserManagerインスタンス
        """
        self.config_file = config_file
        self.user_manager = user_manager
        self.schedule_config: List[Dict[str, str]] = []
        self.multi_user_poster = MultiUserPoster(user_manager)
        self._load_config()

    def _load_config(self) -> None:
        """
        JSONファイルからスケジュール設定を読み込む
        """
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.schedule_config = config['schedule']
            logger.info(f"スケジュール設定を正常に読み込みました: {self.schedule_config}")
        except FileNotFoundError:
            logger.error(f"設定ファイル '{self.config_file}' が見つかりません。")
            raise
        except json.JSONDecodeError:
            logger.error(f"設定ファイル '{self.config_file}' の解析に失敗しました。正しいJSON形式であることを確認してください。")
            raise

    def _job(self) -> None:
        """
        スケジュールされたジョブを実行する
        """
        logger.info("スケジュールされたジョブを開始します。")
        try:
            results = self.multi_user_poster.post_for_all_users()
            for result in results:
                if result['status'] == 'success':
                    logger.info(f"ユーザー '{result['username']}' の投稿が成功しました。スレッドID: {result['thread_id']}")
                else:
                    logger.error(f"ユーザー '{result['username']}' の投稿が失敗しました。エラー: {result['message']}")
        except Exception as e:
            logger.error(f"ジョブの実行中にエラーが発生しました: {str(e)}")

    def run(self) -> None:
        """
        スケジューラーを設定し、実行する
        """
        for schedule_item in self.schedule_config:
            schedule.every().day.at(schedule_item['time']).do(self._job)
            logger.info(f"スケジュール設定: 毎日 {schedule_item['time']} に実行")

        logger.info("スケジューラーを開始します。Ctrl+Cで停止できます。")
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("スケジューラーを停止します。")

    def add_schedule(self, time: str) -> None:
        """
        新しいスケジュールを追加する

        :param time: 追加する時刻（HH:MM形式）
        """
        self.schedule_config.append({"time": time})
        self._save_config()
        schedule.every().day.at(time).do(self._job)
        logger.info(f"新しいスケジュールを追加しました: 毎日 {time} に実行")

    def remove_schedule(self, time: str) -> None:
        """
        指定された時刻のスケジュールを削除する

        :param time: 削除する時刻（HH:MM形式）
        """
        self.schedule_config = [item for item in self.schedule_config if item["time"] != time]
        self._save_config()
        schedule.clear(time)
        logger.info(f"スケジュールを削除しました: {time}")

    def _save_config(self) -> None:
        """
        現在のスケジュール設定をJSONファイルに保存する
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump({"schedule": self.schedule_config}, f, indent=2)
            logger.info(f"スケジュール設定を '{self.config_file}' に保存しました。")
        except IOError:
            logger.error(f"スケジュール設定の保存中にエラーが発生しました。")
            raise

# 使用例
if __name__ == "__main__":
    user_manager = UserManager("users.json")
    scheduler = Scheduler("schedule_config.json", user_manager)
    scheduler.run()