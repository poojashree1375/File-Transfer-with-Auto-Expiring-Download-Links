from django.db import models
import uuid

class FileUpload(models.Model):
    token=models.CharField(max_length=100,unique=True,default=uuid.uuid4)
    expiry_datetime=models.DateTimeField()
    uploaded_at=models.DateTimeField(auto_now_add=True)
    file_name=models.CharField(max_length=255)
    file_type=models.CharField(max_length=100)
    encrypted_data=models.BinaryField()

    def __str__(self):
        return f"EncryptedFile(token={self.token})"
    