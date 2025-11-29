from django.shortcuts import render, redirect
from django.utils import timezone
from .models import FileUpload
from .forms import UploadForm
from datetime import timedelta
from .crypto_utils import encrypt_file, decrypt_file
from django.http import HttpResponse, Http404
import uuid

def upload_file(request):
    if request.method == "POST":
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded = request.FILES['file']
            expiry_minutes = form.cleaned_data['expiry_minutes']

            encrypted = encrypt_file(uploaded.read())

            obj = FileUpload.objects.create(
                token=str(uuid.uuid4()),
                file_name=uploaded.name,
                file_type=uploaded.content_type,
                encrypted_data=encrypted,
                expiry_datetime=timezone.now() + timedelta(minutes=expiry_minutes)
            )
            return redirect("show_link", token=obj.token)
    else:
        form = UploadForm()

    return render(request, "upload.html", {"form": form})


def show_link(request, token):
    file_obj = FileUpload.objects.get(token=token)
    download_url = request.build_absolute_uri(f"/download/{token}/")
    return render(request, "link.html", {'file': file_obj, 'download_url': download_url})


def download_file(request, token):
    try:
        obj = FileUpload.objects.get(token=token)
    except FileUpload.DoesNotExist:
        raise Http404("Invalid link")

    # Check expiry
    if obj.expiry_datetime < timezone.now():
        obj.delete()
        return render(request, "expired.html")

    # Decrypt file
    decrypted_bytes = decrypt_file(obj.encrypted_data)

    response = HttpResponse(decrypted_bytes, content_type=obj.file_type)
    response['Content-Disposition'] = f'attachment; filename=\"{obj.file_name}\"'
    return response

