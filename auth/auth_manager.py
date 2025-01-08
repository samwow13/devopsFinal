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
            password (str): The password (not checked in this implementation)
        Returns:
            User: A User object if authentication successful, None otherwise
        """
        if username.strip():  # Check if username is not empty
            return User(username)
        return None
