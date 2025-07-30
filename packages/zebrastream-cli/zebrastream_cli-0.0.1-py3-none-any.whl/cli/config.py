# SPDX-License-Identifier: GPL-3.0-or-later
"""ZebraStream CLI configuration module."""
import confuse
from pathlib import Path

# Explicit configuration using variables
class ExplicitConfig:
    def __init__(self, app_name, prefix=None):
        # Load configuration from OS-specific path with environment overlay
        self._config = confuse.Configuration(app_name)  # TODO: add default config to replace hardcoded values
        self._config.set_env(prefix=prefix)
        self._config_path = Path(self._config.config_dir()) / confuse.CONFIG_FILENAME
    
    def persist(self):
        """Save the current configuration to disk."""
        with open(self._config_path, 'w') as f:
            f.write(self._config.dump())

    @property
    def api_key(self):
        return self._config['api_key'].get(str)

    @api_key.setter
    def api_key(self, value):
        self._config['api_key'].set(value)

    @property
    def api_url(self):
        return self._config['api_url'].get(confuse.Optional(str, default="https://api.zebrastream.io"))

    @api_url.setter
    def api_url(self, value):
        self._config['api_url'].set(value)


config = ExplicitConfig(app_name='zebrastream-cli', prefix='ZEBRASTREAM_')
