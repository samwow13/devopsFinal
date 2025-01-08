from flask_login import UserMixin

class User(UserMixin):
    """
    User class that represents a user in the system
    Inherits from UserMixin to provide Flask-Login required methods
    """
    
    def __init__(self, username):
        """
        Initialize a new user
        Args:
            username (str): The username of the user
        """
        self.username = username
        self.id = username  # Using username as the ID for simplicity
        
    def get_id(self):
        """
        Required by Flask-Login, returns the user ID
        Returns:
            str: The user ID (username in this case)
        """
        return self.username
