"""
Deployment Manifest Model for Project Astra OS.
Represents version manifests, build metadata, platform targets, and release channels.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional
import time


class ReleaseChannel(str, Enum):
    STABLE = "stable"
    BETA = "beta"
    NIGHTLY = "nightly"


class TargetPlatform(str, Enum):
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"


@dataclass
class DeploymentManifest:
    """
    App release deployment manifest model.
    """
    version: str = "1.0.0"
    build_number: int = 100
    release_channel: ReleaseChannel = ReleaseChannel.STABLE
    target_platform: TargetPlatform = TargetPlatform.WINDOWS
    download_url: Optional[str] = None
    checksum_sha256: Optional[str] = None
    release_notes: str = "Astra OS release"
    built_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "build_number": self.build_number,
            "release_channel": self.release_channel.value if isinstance(self.release_channel, ReleaseChannel) else self.release_channel,
            "target_platform": self.target_platform.value if isinstance(self.target_platform, TargetPlatform) else self.target_platform,
            "download_url": self.download_url,
            "checksum_sha256": self.checksum_sha256,
            "release_notes": self.release_notes,
            "built_at": self.built_at
        }
