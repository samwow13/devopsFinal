"""
Module for managing server configuration and services
"""
import json
import os
from typing import Dict, List, Optional

class ServerConfig:
    """Class to manage server configuration and services"""
    
    def __init__(self):
        """Initialize ServerConfig with the configuration file"""
        self.config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                      'config', 'server_config.json')
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """
        Load the server configuration from JSON file
        
        Returns:
            Dict: Server configuration dictionary
        """
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def get_server_info(self, server_id: str) -> Optional[Dict]:
        """
        Get information for a specific server
        
        Args:
            server_id (str): ID of the server
            
        Returns:
            Optional[Dict]: Server information or None if not found
        """
        return self.config['servers'].get(server_id)
    
    def get_server_services(self, server_id: str) -> List[Dict]:
        """
        Get services associated with a server
        
        Args:
            server_id (str): ID of the server
            
        Returns:
            List[Dict]: List of services for the server or empty list if server not found
        """
        server_info = self.get_server_info(server_id)
        return server_info['services'] if server_info else []
