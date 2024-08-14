import cloudinary
import cloudinary.uploader
import logging
from config import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET

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

    def upload(self, image_path):
        """画像をCloudinaryにアップロードし、URLを返す"""
        try:
            logger.info(f"Uploading image: {image_path}")
            response = cloudinary.uploader.upload(image_path)
            logger.info(f"Image uploaded successfully: {response['secure_url']}")
            return response['secure_url']
        except Exception as e:
            logger.error(f"Error uploading image: {str(e)}")
            raise