import logging
from user_manager import UserManager
from scheduler import Scheduler
from image_pair_manager import ImagePairManager
from config import REPLIES_PARENT_FOLDER, IMAGE_PAIRS_FOLDER

# ロギングの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("スケジュールされた画像ペア投稿プロセスを開始します。")
    
    # ユーザーマネージャーを初期化
    user_manager = UserManager("users.json", REPLIES_PARENT_FOLDER)

    # ImagePairManagerを初期化
    image_pair_manager = ImagePairManager(IMAGE_PAIRS_FOLDER)
    
    # スケジューラーを初期化して実行
    scheduler = Scheduler("schedule_config.json", user_manager, image_pair_manager)
    scheduler.run()

if __name__ == "__main__":
    main()