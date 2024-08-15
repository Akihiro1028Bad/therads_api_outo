import logging
from user_manager import UserManager
from scheduler import Scheduler
from image_pair_manager import ImagePairManager

# ロギングの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("スケジュールされた画像ペア投稿プロセスを開始します。")
    
    # ユーザーマネージャーを初期化
    user_manager = UserManager("users.json")

    # JSONファイルを更新
    image_pair_manager = ImagePairManager()
    image_pair_manager.update_json()
    
    # スケジューラーを初期化して実行
    scheduler = Scheduler("schedule_config.json", user_manager)
    scheduler.run()

if __name__ == "__main__":
    main()