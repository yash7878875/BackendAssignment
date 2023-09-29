import subprocess
import boto3
from django.conf import settings
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys, os
import tempfile
from moviepy.editor import *
aws_access_key_id = ""
aws_secret_access_key =  ""
region_name = ""

def get_s3_files(status,key):
    url = None
    S3_BUCKET_NAME = "s"
    session = boto3.Session(aws_access_key_id=aws_access_key_id,
                            aws_secret_access_key=aws_secret_access_key,
                            region_name=region_name) 
    s3_client = session.client('s3')
    list_files = s3_client.list_objects(Bucket=S3_BUCKET_NAME)["Contents"]
    s3= [key for i in list_files if i["Key"]==key]
    if s3:
        url = f"{settings.S3_MEDIA_URL}/{key}"
    return url
    
def upload_s3(objs,user):
    s3_urls = []
    session = boto3.Session(aws_access_key_id=aws_access_key_id,
                            aws_secret_access_key=aws_secret_access_key,
                            region_name=region_name) 
    s3 = session.client('s3')
    for obj in objs:
        if user is not None:
            user_name = user.email
            user_id = user.id
        image_name = obj.name
        content_type = obj.content_type
        key = f"media/{user_name}/{user_id}/{image_name}" if user is not None else f"media/admin/admin/{image_name}"
        status = s3.put_object(Bucket="s", Key=key,  ContentType=content_type, Body=obj)
        if status["ResponseMetadata"]["HTTPStatusCode"]==200:
            url = get_s3_files(status, key)
            if url:
                s3_urls.append(url)
        else:
            s3_urls=[]
    return s3_urls

def upload_s3_video_audio(objs, user):
    s3_urls = []
    session = boto3.Session(aws_access_key_id=aws_access_key_id,
                            aws_secret_access_key=aws_secret_access_key,
                            region_name=region_name)
    s3 = session.client('s3')
    for obj in objs:
        if user is not None:
            user_name = user.email
            user_id = user.id
        file_name = obj['name']
        content_type = obj['content_type']
        key = f"media/{user_name}/{user_id}/{file_name}" if user is not None else f"media/admin/admin/{file_name}"
        try:
            if content_type.startswith('video/'):
                video = obj.pop('video')
                compressed_video_path = compressVideo(video)
                status = s3.put_object(Bucket="s", Key=key, ContentType=content_type, Body=compressed_video_path)
            elif content_type.startswith('audio/'):
                audio = obj.pop('audio')
                compressed_audio_path = compressAudio(audio)
                status = s3.put_object(Bucket="s", Key=key, ContentType=content_type, Body=compressed_audio_path)

            else:
                continue
            if status["ResponseMetadata"]["HTTPStatusCode"]==200:
                url = get_s3_files(status, key)
                if url:
                    s3_urls.append(url)
        except Exception as e:
            print(e)
            s3_urls = []
            break
    return s3_urls

def delete_object_from_bucket(file_name):
    session = boto3.Session(aws_access_key_id=aws_access_key_id,
                            aws_secret_access_key=aws_secret_access_key,
                            region_name=region_name)
    s3_client = session.client("s3")
    response = s3_client.delete_object(Bucket="s", Key=file_name)
    print(response)
    if response["ResponseMetadata"]["HTTPStatusCode"]==200:
        return True
    else:
        return False  

def compressImage(images):
    image_split = images.name.split('.')
    imageTemproary = Image.open(images)
    imageTemproary = imageTemproary.convert("RGB")
    outputIoStream = BytesIO()
    imageTemproary.save(outputIoStream, 'JPEG', optimize=True, quality=60)
    outputIoStream.seek(0)
    images = InMemoryUploadedFile(
        outputIoStream,
         "%s.webm ", "%s.webp " % image_split[0], 'image/webm', 'image/webp', sys.getsizeof(outputIoStream)
    )
    return images

def compressVideo(video):
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_output_file:
        temp_output_path = temp_output_file.name
        with open(temp_output_path, "wb") as output_file:
            output_file.write(video.read())
        clip = VideoFileClip(temp_output_path)
        compressed_clip = clip.resize(height=480)
        compressed_video_path = f"{temp_output_path}_compressed.mp4"
        compressed_clip.write_videofile(compressed_video_path, codec="libx264", audio_codec="aac")
        return compressed_video_path
    


def compressAudio(audio):
    audio_name = audio.name
    audio_path = os.path.join("/posts/audio/", audio_name)
    compressed_audio_path = os.path.join("/posts/audio_compress", audio_name)
    with open(audio_path, 'wb') as temp_file:
        temp_file.write(audio.read())
    subprocess.call(["C:/ffmpeg/bin/ffmpeg.exe", '-i', audio_path, '-b:a', '64k', compressed_audio_path])
    with open(compressed_audio_path, 'rb') as f:
        compressed_audio = f.read()
    os.remove(audio_path)
    os.remove(compressed_audio_path)
    return compressed_audio






