import os
import logging
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
        self.qualities = qualities or get_setting("QUALITIES")
        logging.info(f"[HLSGenerator] Initialized for media ID={media.id}, qualities={self.qualities}")

    def generate(self):
        logging.info(f"[HLSGenerator] Starting HLS generation for media ID={self.media.id}")
        os.makedirs(self.temp_dir, exist_ok=True)
        logging.debug(f"[HLSGenerator] Temporary directory created: {self.temp_dir}")

        key_manager = KeyManager(self.media.pk, self.temp_dir)
        key_path, key_bytes = key_manager.generate_key_file()
        keyinfo_path = key_manager.generate_keyinfo_file(key_path)
        logging.info(f"[HLSGenerator] Encryption key and keyinfo generated")

        try:
            with open(key_path, "rb") as f:
                self.media.key_file.save(
                    os.path.basename(key_path),
                    ContentFile(f.read()),
                    save=True
                )
            logging.info(f"[HLSGenerator] Key file saved to media instance")
        except Exception as e:
            logging.exception(f"[HLSGenerator] Failed to save key file: {e}")
            raise

        variant_playlists = []

        for quality in self.qualities:
            output_name = f"{quality}p.m3u8"
            output_path = os.path.join(self.temp_dir, output_name)

            video_height = int(quality)
            video_width = int(video_height * 16 / 9)

            logging.info(f"[HLSGenerator] Processing quality {quality}p")

            runner = FFmpegRunner(
                input_path=self.media.media.path,
                output_path=output_path,
                segment_duration=self.segment_duration,
                keyinfo_path=keyinfo_path,
                video_bitrate=self._get_bitrate_for_quality(quality),
                scale=f"{video_width}:{video_height}"
            )

            try:
                runner.run()
                logging.info(f"[HLSGenerator] FFmpeg finished for {quality}p")
            except Exception as e:
                logging.exception(f"[HLSGenerator] FFmpeg failed for {quality}p: {e}")
                continue

            # Save this quality's M3U8
            try:
                with open(output_path, "rb") as f:
                    self.media.hls_file.save(
                        output_name,
                        ContentFile(f.read()),
                        save=True
                    )
                logging.info(f"[HLSGenerator] Playlist {output_name} saved for {quality}p")
            except Exception as e:
                logging.exception(f"[HLSGenerator] Failed to save playlist for {quality}p: {e}")
                continue

            variant_playlists.append((quality, output_name))

            # Save segments
            ts_files = [f for f in os.listdir(self.temp_dir) if f.startswith(quality) and f.endswith(".ts")]
            logging.info(f"[HLSGenerator] Found {len(ts_files)} segment(s) for {quality}p")

            for ts_file in sorted(ts_files):
                path = os.path.join(self.temp_dir, ts_file)
                try:
                    with open(path, "rb") as f:
                        HLSMedia(stream_media=self.media).file.save(
                            ts_file,
                            ContentFile(f.read()),
                            save=True
                        )
                    logging.debug(f"[HLSGenerator] Segment saved: {ts_file}")
                except Exception as e:
                    logging.exception(f"[HLSGenerator] Failed to save segment {ts_file}: {e}")

        # Generate master playlist
        master_path = os.path.join(self.temp_dir, "master.m3u8")
        try:
            with open(master_path, "w") as f:
                f.write("#EXTM3U\n")
                for quality, playlist in variant_playlists:
                    f.write(f"#EXT-X-STREAM-INF:BANDWIDTH={self._get_bandwidth_for_quality(quality)},RESOLUTION={self._get_resolution(quality)}\n")
                    f.write(f"{playlist}\n")
            logging.info(f"[HLSGenerator] Master playlist generated")

            with open(master_path, "rb") as f:
                self.media.hls_file.save(
                    "master.m3u8",
                    ContentFile(f.read()),
                    save=True
                )
            logging.info(f"[HLSGenerator] Master playlist saved to media instance")
        except Exception as e:
            logging.exception(f"[HLSGenerator] Failed to generate/save master playlist: {e}")

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

    def _cleanup(self):
        logging.info(f"[HLSGenerator] Cleaning up temp files in {self.temp_dir}")
        for f in os.listdir(self.temp_dir):
            try:
                os.remove(os.path.join(self.temp_dir, f))
                logging.debug(f"[HLSGenerator] Deleted temp file: {f}")
            except Exception as e:
                logging.warning(f"[HLSGenerator] Could not delete file {f}: {e}")
        try:
            os.rmdir(self.temp_dir)
            logging.debug(f"[HLSGenerator] Removed temp directory")
        except Exception as e:
            logging.warning(f"[HLSGenerator] Could not remove temp directory: {e}")