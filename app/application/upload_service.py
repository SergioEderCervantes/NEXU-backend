import cloudinary.uploader
import logging

logger = logging.getLogger("app")

class UploadService:
    """
    Provides a service to handle file uploads to a cloud provider (Cloudinary).
    """
    def upload_avatar(self, file, user_id: str) -> str:
        """
        Uploads a user's avatar to Cloudinary.

        It overwrites any existing avatar for the same user by using the user's ID
        as the public_id. It also invalidates the old cached image.

        Args:
            file: The file object to upload.
            user_id: The ID of the user, used as the public identifier in Cloudinary.

        Returns:
            The secure URL of the uploaded image.
        """
        logger.info(f"Uploading avatar for user_id: {user_id}")
        upload_result = cloudinary.uploader.upload(
            file,
            folder="users",
            resource_type="image",
            public_id=user_id,
            overwrite=True,
            invalidate=True
        )
        return upload_result["secure_url"]

upload_service = UploadService()