"""
Module for handling server selection functionality
"""

class ServerSelection:
    """Class to manage server selection options and related functionality"""
    
    @staticmethod
    def get_server_options():
        """
        Returns a list of available server options
        
        Returns:
            list: List of server options as tuples (server_id, server_name)
        """
        return [
            ('', 'Select a Server'),  # Default option
            ('prod92', 'Prod 92'),
            ('prod94', 'Prod 94'),
            ('wpdhsappl84', 'WPDHSappl84')
        ]
