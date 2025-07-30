import json
import os
from typing import Any, Dict


def default_config() -> Dict[str, Any]:
    """Return the default configuration"""
    return {
        "region_id": "cn-shanghai",
        "endpoint": "wuyingai.cn-shanghai.aliyuncs.com",
        "timeout_ms": 300000,
    }


def load_config() -> Dict[str, Any]:
    """Load configuration from file"""
    # First check if the config file path is specified in environment variables
    config_path = os.getenv("AGENTBAY_CONFIG_PATH")
    if not config_path:
        # Try to find the config file by traversing up from the current directory
        try:
            dir_path = os.getcwd()
            found = False

            # Start from current directory and traverse up to find .config.json
            # This will check current dir, parent, grandparent, etc. up to filesystem root
            for _ in range(10):  # Limit search depth to prevent infinite loop
                possible_config_path = os.path.join(dir_path, ".config.json")
                if os.path.exists(possible_config_path):
                    config_path = possible_config_path
                    found = True
                    print(f"Found config file at: {possible_config_path}")
                    break

                # Move up one directory
                parent_dir = os.path.dirname(dir_path)
                if parent_dir == dir_path:
                    # We've reached the filesystem root
                    break
                dir_path = parent_dir

            if not found:
                # Config file not found, return default config
                print("Warning: Configuration file not found, using default values")
                return default_config()
        except Exception as e:
            print(
                f"Warning: Failed to search for configuration file: {e}, using default values"
            )
            return default_config()

    try:
        # Read the config file
        with open(config_path, "r") as f:
            config = json.load(f)
    except Exception as e:
        print(f"Warning: Failed to read configuration file: {e}, using default values")
        return default_config()

    # Allow environment variables to override config file values
    if region_id := os.getenv("AGENTBAY_REGION_ID"):
        config["region_id"] = region_id
    if endpoint := os.getenv("AGENTBAY_ENDPOINT"):
        config["endpoint"] = endpoint

    return config
