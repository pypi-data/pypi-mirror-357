import os

from django.db import models
from django.core.validators import FileExtensionValidator

from django_hls.conf import get_setting


SEGMENT_DURATION = get_setting('SEGMENT_DURATION')
USE_CELERY = get_setting('USE_CELERY')
CELERY_QUEUE = get_setting('CELERY_QUEUE')


class HLSMedia(models.Model):
    stream_media = models.ForeignKey(
        "DjangoHLSMedia", on_delete=models.CASCADE, related_name="segments"
    )

    def upload_to_path(instance, filename):
        return os.path.join(
            "django_hls/hls",
            os.path.basename(instance.stream_media.media.name),
            filename,
        )

    file = models.FileField(upload_to=upload_to_path)


class DjangoHLSMedia(models.Model):
    media = models.FileField(
        upload_to="django_hls/uploads/",
        validators=[FileExtensionValidator(allowed_extensions=["mp4", "mp3", "m4a"])],
    )
    
    def upload_to_path(instance, filename):
        return os.path.join("django_hls/hls", os.path.basename(instance.media.name), filename)

    hls_file = models.FileField(upload_to=upload_to_path, blank=True, null=True)
    key_file = models.FileField(upload_to=upload_to_path, blank=True, null=True)
    generating_hls = False

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)

        if is_new:
            from django_hls.utils import is_celery_running, is_queue_available
            from django_hls.tasks import generate_hls
            if USE_CELERY and is_celery_running():
                queue = CELERY_QUEUE if is_queue_available(CELERY_QUEUE) else None
                generate_hls.apply_async(args=[self.id, SEGMENT_DURATION], queue=queue)
            else:
                from django_hls.services.hls_generator import HLSGenerator
                HLSGenerator(self).generate()