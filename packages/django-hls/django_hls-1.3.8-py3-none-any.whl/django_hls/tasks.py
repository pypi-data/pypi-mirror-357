from celery import shared_task
from django_hls.models import DjangoHLSMedia
from django_hls.services.hls_generator import HLSGenerator
from django_hls.conf import get_setting


@shared_task(bind=True)
def generate_hls(self, media_id: int, segment_duration: int, qualities=None):
    try:
        media = DjangoHLSMedia.objects.get(id=media_id)
        from django.conf import settings
        HLSGenerator(media, qualities or get_setting("QUALITIES")).generate()
    except Exception as e:
        import logging
        logging.exception(f"HLS generation failed for media {media_id}: {e}")