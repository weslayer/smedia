import boto3
import os
import magic
from fastapi import HTTPException, UploadFile
from uuid import uuid4

class S3Handler:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.getenv('AWS_BUCKET_NAME')

    async def upload_file(self, file: UploadFile, file_type: str = "resume") -> str:
        try:
            # Read file content
            content = await file.read()
            
            # Verify file type
            mime = magic.Magic(mime=True)
            detected_type = mime.from_buffer(content)
            
            if file_type == "resume" and not detected_type == "application/pdf":
                raise HTTPException(
                    status_code=400,
                    detail="Invalid file type. Only PDF files are allowed for resumes."
                )
            elif file_type == "image" and not detected_type.startswith('image/'):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid file type. Only images are allowed for profile pictures."
                )

            # Generate unique filename
            file_extension = ".pdf" if file_type == "resume" else os.path.splitext(file.filename)[1]
            unique_filename = f"{file_type}/{uuid4()}{file_extension}"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=unique_filename,
                Body=content,
                ContentType=detected_type
            )
            
            # Generate URL
            url = f"https://{self.bucket_name}.s3.amazonaws.com/{unique_filename}"
            return url

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error uploading file: {str(e)}"
            )

    def delete_file(self, url: str):
        try:
            if not url:
                return
                
            # Extract key from URL
            key = url.split('/')[-1]
            
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting file: {str(e)}"
            )

s3_handler = S3Handler() 