import cloudinary
import cloudinary.uploader
import logging
from config import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET, WATERMARK_USERNAME, WATERMARK_POSITION, WATERMARK_STYLE

# ロギングの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CloudinaryUploader:
    def __init__(self):
        # Cloudinaryの設定
        cloudinary.config(
            cloud_name=CLOUDINARY_CLOUD_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET
        )
        logger.info("Cloudinary uploader initialized")

    def upload(self, image_path, username):
        try:
            options = {
                'folder': 'threadsapp_uploads'
            }
            
            if WATERMARK_USERNAME:
                options['transformation'] = [
                    {
                        'overlay': {
                            'font_family': 'Arial',
                            'font_size': WATERMARK_STYLE['font_size'],
                            'font_color': WATERMARK_STYLE['font_color'],
                            'text': username
                        },
                        'opacity': WATERMARK_STYLE['opacity'],
                        'gravity': 'center',
                        'x': int(WATERMARK_POSITION['x'] * 100),
                        'y': int(WATERMARK_POSITION['y'] * 100)
                    }
                ]

            response = cloudinary.uploader.upload(image_path, **options)
            logger.info(f"画像を正常にアップロードしました: {response['secure_url']}")

            return response['secure_url']

        except Exception as e:
            logger.error(f"画像のアップロード中にエラーが発生しました: {str(e)}")
            raise