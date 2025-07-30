"""
Centralized Configuration Management for the DPI System.

This module provides a ConfigManager to load and serve all system configurations
from a central directory.
"""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """
    Centralized configuration manager for the DPI system.
    Loads all YAML files from a config directory and provides access to module configs.
    """
    
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = Path(config_dir)
        self._configs: Dict[str, Any] = {}
        self.load_all_configs()

    def load_all_configs(self) -> None:
        """
        Load all YAML configuration files from the config directory.
        
        Merges all configuration files into a single dictionary.
        """
        if not self.config_dir.is_dir():
            raise FileNotFoundError(f"Configuration directory not found: {self.config_dir}")
        
        for config_file in self.config_dir.glob('*.yaml'):
            try:
                with open(config_file, 'r') as f:
                    data = yaml.safe_load(f) or {}
                    self._configs.update(data)
            except yaml.YAMLError as e:
                print(f"Error parsing YAML file {config_file}: {e}")
            except Exception as e:
                print(f"Error loading config file {config_file}: {e}")
                
        if not self._configs:
            print(f"Warning: No configurations loaded from {self.config_dir}")

    def get_config(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Get a specific configuration value by key.
        
        Args:
            key: The top-level key for the configuration.
            default: The default value to return if the key is not found.
            
        Returns:
            The configuration value or the default.
        """
        return self._configs.get(key, default)

    def get_module_config(self, module_name: str) -> Dict[str, Any]:
        """
        Get the configuration for a specific module.
        
        Searches for the module's configuration under standard sections
        like 'dpi_engine.modules' or a top-level key.
        
        Args:
            module_name: The name of the module.
            
        Returns:
            A dictionary with the module's configuration, or an empty dict.
        """
        # Try to find in dpi_engine.modules
        if 'dpi_engine' in self._configs and 'modules' in self._configs['dpi_engine']:
            if module_name in self._configs['dpi_engine']['modules']:
                return self._configs['dpi_engine']['modules'][module_name]
        
        # Try to find as a top-level key
        if module_name in self._configs:
            return self._configs[module_name]
        
        return {}

    def get_logging_config(self) -> Dict[str, Any]:
        """
        Get the main logging configuration.
        """
        return self.get_config('logging', {})