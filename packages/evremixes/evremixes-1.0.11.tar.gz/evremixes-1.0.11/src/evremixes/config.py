from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

from polykit.paths import PolyPath

from evremixes.menu_helper import MenuHelper

if TYPE_CHECKING:
    from pathlib import Path

    from evremixes.types import AudioFormat, TrackVersions


@dataclass
class DownloadConfig:
    """Configuration for the downloader."""

    TRACKLIST_URL: ClassVar[str] = (
        "https://raw.githubusercontent.com/dannystewart/evremixes/refs/heads/main/evtracks.json"
    )
    ONEDRIVE_SUBFOLDER: ClassVar[str] = "Music/Danny Stewart/Evanescence Remixes"
    ANALYTICS_ENDPOINT: ClassVar[str] = "https://bots.dannystewart.com/web/api/evremixes/analytics"

    # Path helper
    paths: PolyPath = field(init=False)

    # Whether to download as admin (all tracks and formats direct to OneDrive)
    is_admin: bool

    # User choices made at runtime
    versions: TrackVersions | None = None
    audio_format: AudioFormat | None = None
    location: Path | None = None

    def __post_init__(self):
        self.paths = PolyPath("evremixes")

    @property
    def onedrive_folder(self) -> Path:
        """Get the OneDrive folder path for admin downloads."""
        return self.paths.from_onedrive(self.ONEDRIVE_SUBFOLDER)

    @classmethod
    def create(cls, is_admin: bool = False) -> DownloadConfig:
        """Create a new download configuration."""
        config = cls(is_admin=is_admin)

        if not is_admin:
            menu = MenuHelper(config)
            config.versions = menu.prompt_for_versions()
            config.audio_format = menu.prompt_for_format()
            config.location = menu.prompt_for_location()

        return config
