import os
from django.utils import timezone
from django.core.files.base import ContentFile

from django_hls.models import DjangoHLSMedia, HLSMedia
from django_hls.conf import get_setting
from django_hls.services.key_manager import KeyManager
from django_hls.services.ffmpeg_runner import FFmpegRunner


class HLSGenerator:
    def __init__(self, media: DjangoHLSMedia, qualities=None):
        self.media = media
        self.segment_duration = get_setting("SEGMENT_DURATION")
        self.temp_dir = os.path.abspath(
            os.path.join("hls_temp_dir", timezone.now().strftime("%Y-%m-%d_%H-%M-%S"))
        )
        self.qualities = qualities or get_setting("HLS_QUALITIES")

    def generate(self):
        os.makedirs(self.temp_dir, exist_ok=True)

        key_manager = KeyManager(self.media.pk, self.temp_dir)
        key_path, key_bytes = key_manager.generate_key_file()
        keyinfo_path = key_manager.generate_keyinfo_file(key_path)

        self.media.key_file.save(
            os.path.basename(key_path),
            ContentFile(open(key_path, "rb").read()),
            save=True
        )

        variant_playlists = []

        for quality in self.qualities:
            output_name = f"{quality}p.m3u8"
            output_path = os.path.join(self.temp_dir, output_name)

            video_height = int(quality)
            video_width = int(video_height * 16 / 9)

            runner = FFmpegRunner(
                input_path=self.media.media.path,
                output_path=output_path,
                segment_duration=self.segment_duration,
                keyinfo_path=keyinfo_path,
                video_bitrate=self._get_bitrate_for_quality(quality),
                scale=f"{video_width}:{video_height}"
            )
            runner.run()

            # Save this quality's M3U8
            self.media.hls_file.save(
                output_name,
                ContentFile(open(output_path, "rb").read()),
                save=True
            )
            variant_playlists.append((quality, output_name))

            # Save segments
            for file in sorted(f for f in os.listdir(self.temp_dir) if file.startswith(quality) and file.endswith(".ts")):
                path = os.path.join(self.temp_dir, file)
                HLSMedia(stream_media=self.media).file.save(
                    file,
                    ContentFile(open(path, "rb").read()),
                    save=True
                )

        # Generate master playlist
        master_path = os.path.join(self.temp_dir, "master.m3u8")
        with open(master_path, "w") as f:
            f.write("#EXTM3U\n")
            for quality, playlist in variant_playlists:
                f.write(f"#EXT-X-STREAM-INF:BANDWIDTH={self._get_bandwidth_for_quality(quality)},RESOLUTION={self._get_resolution(quality)}\n")
                f.write(f"{playlist}\n")

        self.media.hls_file.save(
            "master.m3u8",
            ContentFile(open(master_path, "rb").read()),
            save=True
        )

        self._cleanup()

    def _get_bitrate_for_quality(self, quality):
        return {
            "360": "800k",
            "480": "1200k",
            "720": "2500k",
            "1080": "5000k"
        }.get(quality, "1200k")

    def _get_bandwidth_for_quality(self, quality):
        return {
            "360": 1000000,
            "480": 1500000,
            "720": 3000000,
            "1080": 5500000
        }.get(quality, 1500000)

    def _get_resolution(self, quality):
        h = int(quality)
        w = int(h * 16 / 9)
        return f"{w}x{h}"
