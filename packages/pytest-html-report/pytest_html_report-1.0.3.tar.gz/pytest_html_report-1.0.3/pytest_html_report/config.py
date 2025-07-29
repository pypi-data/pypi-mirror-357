import os
import yaml
from pathlib import Path

_config = None
_config_search_paths = [
    "pytest_html_report.yml",
    "pytest_html_report.yaml",
    ".pytest_html_report.yml",
    "config/pytest_html_report.yml",
    "tests/pytest_html_report.yml"
]


def find_config_file():
    """Search for configuration file in common locations"""
    # Start from current working directory
    cwd = Path.cwd()

    # Check each search path
    for config_name in _config_search_paths:
        config_path = cwd / config_name
        if config_path.exists():
            return str(config_path)

    # Check parent directories (up to 3 levels)
    for parent_level in range(1, 4):
        parent_dir = cwd.parents[parent_level - 1] if len(cwd.parents) >= parent_level else None
        if parent_dir:
            for config_name in _config_search_paths:
                config_path = parent_dir / config_name
                if config_path.exists():
                    return str(config_path)

    return None


def load_config():
    """Load configuration from YAML file"""
    global _config

    default_config = {
        'report': {
            'title': 'Test Report',
            'img_url': 'https://via.placeholder.com/50',
            'report_dir': 'reports',
            'test_environment': 'Development'
        },
        'theme': {
            'primary_color': '#0052CC',
            'primary_hover': '#0747A6',
            'success_bg': '#E3FCEF',
            'success_text': '#00875A',
            'error_bg': '#FFEBE6',
            'error_text': '#DE350B',
            'warning_bg': '#FFFAE6',
            'warning_text': '#974F0C',
            'info_bg': '#DEEBFF',
            'info_text': '#0747A6'
        },
        'functional_specs': {},
        'categories': {
            'regression': 'Regression Tests',
            'smoke': 'Smoke Tests',
            'integration': 'Integration Tests',
            'unit': 'Unit Tests',
            'manual': 'Manual Tests',
            'optional': 'Optional Tests',
            'performance': 'Performance Tests'
        },
        'logging': {
            'step_level': 24,
            'assertion_level': 25
        }
    }

    # Try to find config file
    config_path = find_config_file()

    if config_path and os.path.exists(config_path):
        print(f"Loading pytest-html-report config from: {config_path}")
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f) or {}
            # Deep merge with defaults
            _config = deep_merge(default_config, config)
    else:
        print("No pytest-html-report config found, using defaults")
        _config = default_config

    return _config


def deep_merge(default, override):
    """Deep merge two dictionaries"""
    result = default.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def get_config():
    """Get the loaded configuration"""
    global _config
    if _config is None:
        load_config()
    return _config