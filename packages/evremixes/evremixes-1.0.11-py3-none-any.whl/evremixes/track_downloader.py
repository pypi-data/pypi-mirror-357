from __future__ import annotations

import contextlib
import os
import platform
import shutil
import string
import subprocess
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import requests
from halo import Halo
from polykit.cli import handle_interrupt
from polykit.formatters import color, print_color
from polykit.log import PolyLog

from evremixes.analytics import AnalyticsHelper
from evremixes.metadata_helper import MetadataHelper
from evremixes.types import AudioFormat, TrackVersions

if TYPE_CHECKING:
    from logging import Logger

    from evremixes.config import DownloadConfig
    from evremixes.types import AlbumInfo


class TrackDownloader:
    """Helper class for downloading tracks."""

    def __init__(self, config: DownloadConfig) -> None:
        self.config = config
        self.metadata = MetadataHelper(config)
        self.analytics = AnalyticsHelper(config)
        self.logger: Logger = PolyLog.get_logger()

    @handle_interrupt()
    def download_tracks(self, album_info: AlbumInfo, config: DownloadConfig) -> None:
        """Download tracks according to configuration.

        Raises:
            ValueError: If the configuration is incomplete.
        """
        if config.versions is None or config.audio_format is None or config.location is None:
            msg = "Download configuration is incomplete"
            raise ValueError(msg)

        # Sanitize album name for folder creation
        valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
        album_name = "".join(c for c in album_info.album_name if c in valid_chars)

        # Get base output folder
        base_folder = config.location / album_name
        overall_success = True

        match config.versions:
            case TrackVersions.ORIGINAL:
                overall_success &= self._download_and_move_set(
                    album_info, base_folder, config.audio_format, is_instrumental=False
                )
            case TrackVersions.INSTRUMENTAL:
                overall_success &= self._download_and_move_set(
                    album_info, base_folder, config.audio_format, is_instrumental=True
                )
            case TrackVersions.BOTH:
                overall_success &= self._download_and_move_set(
                    album_info, base_folder, config.audio_format, is_instrumental=False
                )
                print()
                overall_success &= self._download_and_move_set(
                    album_info,
                    base_folder / "Instrumentals",
                    config.audio_format,
                    is_instrumental=True,
                )
            case _:
                return

        if overall_success and not config.is_admin:
            print_color("\nEnjoy!", "green")
            self.open_folder_in_os(base_folder)
        elif not overall_success:
            print_color("\nSome downloads were not completed successfully.", "yellow")

    def _download_and_move_set(
        self,
        album_info: AlbumInfo,
        final_folder: Path,
        file_format: AudioFormat,
        is_instrumental: bool,
    ) -> bool:
        """Download a track set to temp location and move to final location if successful."""
        display_folder = self.format_path_for_display(final_folder)
        print_color(f"Downloading in {file_format.display_name} to {display_folder}...\n", "cyan")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_folder = Path(temp_dir) / final_folder.name

            # Download to temp location
            if self._download_track_set(
                album_info, temp_folder, file_format, is_instrumental, display_folder
            ):
                # Only remove previous downloads after successful download to temp
                self.remove_previous_downloads(final_folder)
                self._move_files_to_destination(temp_folder, final_folder)
                return True

            print_color(
                "\nDownload incomplete. No changes were made to your existing files.", "yellow"
            )
            return False

    def _move_files_to_destination(self, source_dir: Path, dest_dir: Path) -> None:
        """Move files from temporary location to final destination."""
        if not source_dir.exists():
            return

        # Create destination directory if it doesn't exist
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Copy all files and directories
        for item in source_dir.glob("*"):
            dest_path = dest_dir / item.name

            if item.is_dir():
                # Recursively copy directories
                shutil.copytree(item, dest_path, dirs_exist_ok=True)
            else:
                # Copy files
                shutil.copy2(item, dest_path)

    @handle_interrupt()
    def _download_track_set(
        self,
        album_info: AlbumInfo,
        output_folder: Path,
        file_format: AudioFormat,
        is_instrumental: bool,
        display_folder: str,
    ) -> bool:
        """Download a single complete set of tracks. Returns True if all downloads succeeded."""
        output_folder.mkdir(parents=True, exist_ok=True)

        # Choose cover art based on track type
        cover_url = album_info.inst_art_url if is_instrumental else album_info.cover_art_url
        cover_data = self.metadata.get_cover_art(cover_url)

        spinner = Halo(spinner="dots")
        total_tracks = len(album_info.tracks)
        all_successful = True

        for index, track in enumerate(album_info.tracks, start=1):
            track_number = f"{track.track_number:02d}"
            track_name = track.track_name

            if is_instrumental:
                file_url = track.inst_url.rsplit(".", 1)[0] + f".{file_format.extension}"
                if not track_name.endswith(" (Instrumental)"):
                    track_name += " (Instrumental)"
            else:
                file_url = track.file_url.rsplit(".", 1)[0] + f".{file_format.extension}"

            output_path = output_folder / f"{track_number} - {track_name}.{file_format.extension}"

            spinner.text = color(f"Downloading {track_name}... ({index}/{total_tracks})", "cyan")
            spinner.start()

            try:
                # Add analytics headers to track downloads
                headers = self.analytics.get_analytics_headers(
                    track_name,
                    file_format,
                    TrackVersions.ORIGINAL if not is_instrumental else TrackVersions.INSTRUMENTAL,
                )
                response = requests.get(file_url, stream=True, timeout=30, headers=headers)
                response.raise_for_status()
                output_path.write_bytes(response.content)

                spinner.text = color("Applying metadata...", "cyan")
                success = self.metadata.apply_metadata(
                    track, album_info, output_path, cover_data, is_instrumental
                )

                if not success:
                    spinner.fail(color(f"Failed to add metadata to {track_name}.", "red"))
                    all_successful = False
                    continue

                spinner.succeed(color(f"Downloaded {track_name}", "green"))
                self.analytics.track_track_download(track, file_format)

            except requests.RequestException:
                spinner.fail(color(f"Failed to download {track_name}.", "red"))
                all_successful = False

        spinner.stop()

        end_message = (
            f"All {total_tracks} {'instrumentals' if is_instrumental else 'remixes'} "
            f"downloaded in {file_format.display_name} to {display_folder}."
        )
        print_color(f"\n{end_message}", "green")

        return all_successful

    @handle_interrupt()
    def download_tracks_for_admin(self, album_info: AlbumInfo) -> None:
        """Download all track versions to the custom OneDrive location."""
        base_path = self.config.onedrive_folder
        overall_success = True

        # Download all combinations, each as a separate operation
        for file_format in AudioFormat:
            # Original tracks
            final_folder = base_path / file_format.display_name
            success = self._download_and_move_set(
                album_info, final_folder, file_format, is_instrumental=False
            )
            overall_success &= success
            print()

            # Instrumental tracks
            final_folder = base_path / f"Instrumentals {file_format.display_name}"
            success = self._download_and_move_set(
                album_info, final_folder, file_format, is_instrumental=True
            )
            overall_success &= success
            print()

        if overall_success:
            print_color("All downloads completed successfully!", "green")
            self.open_folder_in_os(base_path)
        else:
            print_color("Some downloads were not completed successfully.", "yellow")

    def remove_previous_downloads(self, output_folder: str | Path) -> None:
        """Remove any existing files with the specified file extension in the output folder."""
        output_folder = Path(output_folder)
        if not output_folder.exists():
            return

        file_extensions = (".flac", ".m4a")

        # Remove matching files
        for file_path in output_folder.rglob("*"):
            if file_path.suffix.lower() in file_extensions:
                try:
                    file_path.unlink()
                except Exception as e:
                    self.logger.error("Failed to delete %s: %s", file_path, str(e))

        # Remove empty directories from bottom up
        for dirpath in sorted(
            output_folder.rglob("*"), key=lambda x: len(str(x.resolve()).split("/")), reverse=True
        ):
            if dirpath.is_dir():
                with contextlib.suppress(OSError):
                    dirpath.rmdir()

    def open_folder_in_os(self, output_folder: str | Path) -> None:
        """Open the output folder in the OS file browser."""
        with contextlib.suppress(Exception):
            output_folder = Path(output_folder).resolve()
            os_type = platform.system()

            if os_type == "Windows":
                subprocess.run(["explorer", str(output_folder)], check=False)
            elif os_type == "Darwin":
                subprocess.run(["open", str(output_folder)], check=False)
            elif os_type == "Linux" and "DISPLAY" in os.environ:
                subprocess.run(["xdg-open", str(output_folder)], check=False)

    def format_path_for_display(self, path: Path) -> str:
        """Convert a path to a user-friendly display format with ~ for home directory."""
        path_delimiter = "/" if platform.system() != "Windows" else "\\"
        try:
            return f"~{path_delimiter}{path.relative_to(Path.home())}"
        except ValueError:
            return str(path)
