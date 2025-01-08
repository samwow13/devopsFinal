from models.user import User

class AuthManager:
    """
    Manages authentication operations
    """
    
    @staticmethod
    def authenticate_user(username, password):
        """
        Authenticate a user with username and password
        Args:
            username (str): The username to authenticate
            password (str): The password to authenticate
        Returns:
            bool: True if authentication successful, False otherwise
        """
        # For now, just check if username and password are not empty
        return bool(username.strip() and password.strip())
