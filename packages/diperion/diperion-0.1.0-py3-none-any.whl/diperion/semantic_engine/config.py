"""
Configuration management for Diperion SDK.

This module handles URL resolution, environment detection, and configuration loading.
"""

import os
import json
from typing import Dict, Optional, Any
from pathlib import Path


class DiperionConfig:
    """
    Centralized configuration management for Diperion SDK.
    
    Supports multiple configuration sources:
    1. Environment variables
    2. Configuration files (.diperion.json, diperion.config.json)
    3. Default values
    """
    
    # Default configuration
    DEFAULTS = {
        "urls": {
            "development": "http://localhost:8080",
            "production": "https://api.diperion.com",
            "staging": "https://staging-api.diperion.com"
        },
        "timeout": 30,
        "environment": "development"
    }
    
    # Configuration file names (searched in order)
    CONFIG_FILES = [
        ".diperion.json",
        "diperion.config.json",
        ".diperion.config.json"
    ]
    
    def __init__(self):
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from all sources."""
        config = self.DEFAULTS.copy()
        
        # 1. Load from config files
        file_config = self._load_from_files()
        if file_config:
            config.update(file_config)
        
        # 2. Override with environment variables
        env_config = self._load_from_env()
        config.update(env_config)
        
        return config
    
    def _load_from_files(self) -> Dict[str, Any]:
        """Load configuration from JSON files."""
        # Search in current directory and home directory
        search_paths = [
            Path.cwd(),
            Path.home(),
            Path.home() / ".config" / "diperion"
        ]
        
        for search_path in search_paths:
            for config_file in self.CONFIG_FILES:
                config_path = search_path / config_file
                if config_path.exists():
                    try:
                        with open(config_path, 'r') as f:
                            return json.load(f)
                    except (json.JSONDecodeError, IOError):
                        continue
        
        return {}
    
    def _load_from_env(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        config = {}
        
        # Environment detection
        if os.getenv("DIPERION_ENVIRONMENT"):
            config["environment"] = os.getenv("DIPERION_ENVIRONMENT")
        
        # URL configuration
        if os.getenv("DIPERION_API_URL"):
            config["api_url"] = os.getenv("DIPERION_API_URL")
        
        if os.getenv("DIPERION_BASE_URL"):
            config["base_url"] = os.getenv("DIPERION_BASE_URL")
        
        # Timeout configuration
        if os.getenv("DIPERION_TIMEOUT"):
            try:
                config["timeout"] = int(os.getenv("DIPERION_TIMEOUT"))
            except ValueError:
                pass
        
        # Custom URLs for environments
        for env in ["development", "production", "staging"]:
            env_var = f"DIPERION_{env.upper()}_URL"
            if os.getenv(env_var):
                if "urls" not in config:
                    config["urls"] = {}
                config["urls"][env] = os.getenv(env_var)
        
        return config
    
    def get_base_url(self, explicit_url: str = None, environment: str = None) -> str:
        """
        Resolve the base URL using the priority system.
        
        Priority:
        1. Explicit URL parameter
        2. DIPERION_API_URL environment variable
        3. DIPERION_BASE_URL environment variable
        4. Environment-specific URL from config
        5. Default environment URL
        """
        # 1. Explicit parameter has highest priority
        if explicit_url:
            return explicit_url
        
        # 2. Check for explicit API URL in config
        if self._config.get("api_url"):
            return self._config["api_url"]
        
        # 3. Check for base URL in config
        if self._config.get("base_url"):
            return self._config["base_url"]
        
        # 4. Determine environment
        target_env = environment or self._config.get("environment", "development")
        
        # 5. Get URL for environment
        urls = self._config.get("urls", {})
        return urls.get(target_env, urls.get("development", self.DEFAULTS["urls"]["development"]))
    
    def get_timeout(self) -> int:
        """Get configured timeout."""
        return self._config.get("timeout", self.DEFAULTS["timeout"])
    
    def get_environment(self) -> str:
        """Get current environment."""
        return self._config.get("environment", self.DEFAULTS["environment"])
    
    def update_production_url(self, new_url: str) -> None:
        """
        Update the production URL (useful for SDK updates).
        
        This method can be called by the SDK to update URLs
        when new deployments are detected.
        """
        if "urls" not in self._config:
            self._config["urls"] = {}
        self._config["urls"]["production"] = new_url
    
    def create_example_config_file(self, path: str = ".diperion.json") -> None:
        """Create an example configuration file."""
        example_config = {
            "environment": "production",
            "timeout": 30,
            "urls": {
                "development": "http://localhost:8080",
                "production": "https://api.diperion.com",
                "staging": "https://staging-api.diperion.com"
            }
        }
        
        with open(path, 'w') as f:
            json.dump(example_config, f, indent=2)


# Global configuration instance
_config = DiperionConfig()


def get_config() -> DiperionConfig:
    """Get the global configuration instance."""
    return _config


def reload_config() -> DiperionConfig:
    """Reload configuration from all sources."""
    global _config
    _config = DiperionConfig()
    return _config
