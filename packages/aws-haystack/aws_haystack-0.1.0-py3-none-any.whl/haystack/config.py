"""Configuration management for Haystack."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class HaystackConfig:
    """Manages Haystack configuration and caching."""

    def __init__(self) -> None:
        self.config_dir = Path.home() / ".haystack"
        self.config_file = self.config_dir / "config.json"
        self.cache_dir = self.config_dir / "cache"

        # Ensure directories exist
        self.config_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)

        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    config_data = json.load(f)
                    return config_data if isinstance(config_data, dict) else {}
            except Exception:
                pass
        return {}

    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self._config, f, indent=2)
        except Exception:
            pass

    def get_sso_config(self) -> Optional[Dict[str, str]]:
        """Get saved SSO configuration."""
        sso_config = self._config.get("sso")
        if sso_config is None or not isinstance(sso_config, dict):
            return None
        # Ensure all values are strings
        if all(isinstance(v, str) for v in sso_config.values()):
            return Dict[str, str](sso_config)
        return None

    def set_sso_config(self, start_url: str, region: str = "us-east-1") -> None:
        """Save SSO configuration."""
        self._config["sso"] = {"start_url": start_url, "region": region}
        self._save_config()

    def get_token_cache_path(self, start_url: str) -> str:
        """Get path for token cache file."""
        import hashlib

        url_hash = hashlib.sha256(start_url.encode()).hexdigest()[:16]
        return str(self.cache_dir / f"sso-token-{url_hash}.json")

    def clear_config(self) -> None:
        """Clear all configuration and cache."""
        if self.config_file.exists():
            self.config_file.unlink()

        # Clear cache files
        for cache_file in self.cache_dir.glob("sso-token-*.json"):
            cache_file.unlink()

        self._config = {}
