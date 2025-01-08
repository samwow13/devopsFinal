from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models.user import User
from models.server_selection import ServerSelection
from auth.auth_manager import AuthManager
from models.server_config import ServerConfig  # Import ServerConfig

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Change this in production

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login user loader callback
    Args:
        user_id (str): The user ID to load
    Returns:
        User: The User object for the given ID
    """
    # Since we're storing the password in memory, we need to create a new user
    # without password when loading from session
    return User(user_id)

@app.route('/')
@login_required
def home():
    """
    Home page route, requires authentication
    """
    server_config = ServerConfig()
    servers = server_config.config['servers']
    return render_template('home.html', servers=servers)

@app.route('/get_services/<server_id>')
@login_required
def get_services(server_id):
    """
    Get services for a specific server
    
    Args:
        server_id (str): ID of the server to get services for
        
    Returns:
        JSON: List of services with their status
    """
    server_config = ServerConfig()
    services = server_config.get_server_services(server_id)
    
    # Initialize all services with N/A status
    service_statuses = [{
        "name": service['name'],
        "running": None  # None indicates N/A status
    } for service in services]
    
    try:
        # Get the current user's credentials
        username = current_user.username
        # In a real application, you would get this from a secure storage
        password = current_user.password  # TODO: Replace with actual password retrieval
        
        # Get service names from config
        service_names = [service['name'] for service in services]
        
        # Check service status using PowerShell
        status_output = check_services_powershell(username, password, server_id, service_names)
        
        # Create a dictionary of service statuses from PowerShell output
        status_dict = {}
        for line in status_output.splitlines():
            if "Service '" in line and "' is" in line:
                parts = line.split("'")
                if len(parts) >= 2:
                    service_name = parts[1]
                    is_running = "is running" in line.lower()
                    status_dict[service_name] = is_running
        
        # Update service statuses with PowerShell results
        for service in service_statuses:
            if service['name'] in status_dict:
                service['running'] = status_dict[service['name']]
    
    except Exception as e:
        print(f"Error checking service status: {str(e)}")
        # Keep N/A status for all services on error
    
    return jsonify(service_statuses)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login route, handles both GET and POST requests
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if AuthManager.authenticate_user(username, password):
            user = User(username, password)  # Create user with password
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """
    Logout route
    """
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=3000)
