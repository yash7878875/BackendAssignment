from django.db import models
from users.models import *
from categorys.models import *
import uuid
from django.contrib.postgres.fields import ArrayField

# Create your models here.


class Post(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    multiid = models.UUIDField(
        editable=False,
        null=True
    )
    user = models.ForeignKey(User, related_name='user_id',
                             on_delete=models.CASCADE, null=False)
    images = ArrayField(models.FileField(max_length=1000, null=False))
    type = models.CharField(max_length=264, null=True)

    tool = models.CharField(max_length=264,null=True)
    category = models.ForeignKey(
        Category, related_name='category_id', on_delete=models.CASCADE, null=False)
    caption = models.CharField(max_length=264)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.images

    class Meta:
        db_table = 'post'
