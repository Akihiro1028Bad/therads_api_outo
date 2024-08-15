import logging
from user_manager import UserManager
from multi_user_poster import MultiUserPoster
from image_pair_manager import ImagePairManager

# ロギングの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("複数ユーザー画像ペア投稿プロセスを開始します。")
    
    # JSONファイルを更新
    image_pair_manager = ImagePairManager()
    image_pair_manager.update_json()
    
    # ユーザーマネージャーを初期化
    user_manager = UserManager("users.json")
    
    # 複数ユーザー投稿機能を実行
    multi_poster = MultiUserPoster(user_manager)
    results = multi_poster.post_for_all_users()
    
    # 結果を表示
    for result in results:
        if result['status'] == 'success':
            logger.info(f"ユーザー '{result['username']}' の投稿が成功しました。スレッドID: {result['thread_id']}")
        else:
            logger.error(f"ユーザー '{result['username']}' の投稿が失敗しました。エラー: {result['message']}")
    
    logger.info("複数ユーザー画像ペア投稿プロセスが完了しました。")

if __name__ == "__main__":
    main()