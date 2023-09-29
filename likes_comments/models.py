from django.db import models

# Create your models here.
from django.db import models
from posts.models import Post
from django.core.validators import MinLengthValidator
from users.models import User
import uuid

# Create your models here.


class Comments(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    users = models.ForeignKey(User, models.DO_NOTHING)
    user_post = models.ForeignKey(Post, models.DO_NOTHING)
    comment = models.TextField(validators=[MinLengthValidator(3)])
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # managed = False
        db_table = 'comments'


class Like(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    users = models.ForeignKey(User, models.DO_NOTHING)
    user_post = models.ForeignKey(Post, models.DO_NOTHING)
    like = models.BooleanField(null=False,)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # managed = False
        db_table = 'like'


class DisLike(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    users = models.ForeignKey(User, models.DO_NOTHING)
    user_post = models.ForeignKey(Post, models.DO_NOTHING)
    like = models.BooleanField(null=False,)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'dislikes'
