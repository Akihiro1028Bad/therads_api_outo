from image_pair_poster import ImagePairPoster
from image_pair_manager import ImagePairManager
import logging

# ロギングの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting the image pair posting process")
    
    # JSONファイルを更新
    image_pair_manager = ImagePairManager()
    image_pair_manager.update_json()
    
    # 画像ペアを投稿
    poster = ImagePairPoster()
    poster.run()
    
    logger.info("Image pair posting process completed")

if __name__ == "__main__":
    main()