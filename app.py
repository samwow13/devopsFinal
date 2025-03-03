from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models.user import User
from models.server_selection import ServerSelection
from auth.auth_manager import AuthManager
from models.server_config import ServerConfig  # Import ServerConfig
from powershellStatusChecker import check_services_powershell  # Import the PowerShell checker function
from manage_jboss import manage_jboss  # Import manage_jboss function

# Dictionary to store user passwords temporarily in memory
_user_passwords = {}

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
    # We need to create a new user without password when loading from session
    # The password will be set by the login route
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
        if not current_user.is_authenticated:
            raise ValueError("User not authenticated")
            
        username = current_user.username
        password = _user_passwords.get(username)
        print(f"Username: {username}")
        print(f"Password: {password}")

        # Get service names from config
        service_names = [service['name'] for service in services]
        print(f"Service Names: {service_names}")
        jboss_cli_command = server_config.config['servers'][server_id]['check_jboss_is_running']
        print(f"JBoss CLI Command: {jboss_cli_command}")

        
        if not username or not password:
            raise ValueError("Missing credentials")
        
        # Check service status using PowerShell
        try:
            status_output = check_services_powershell(username, password, server_id, service_names, jboss_cli_command)
            
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
                    
        except ConnectionError as ce:
            # Handle connection error specifically
            return jsonify({
                "error": "connection_failed",
                "message": str(ce)
            }), 503  # Service Unavailable
    
    except Exception as e:
        print(f"Error checking service status: {str(e)}")
        # Keep N/A status for all services on error
    
    return jsonify(service_statuses)

@app.route('/manage_eap/<server_id>/<action>', methods=['POST'])
@login_required
def manage_eap_service(server_id, action):
    """
    Manage EAP service (start/stop) for a specific server
    
    Args:
        server_id (str): ID of the server to manage EAP on
        action (str): Action to perform ('start' or 'stop')
        
    Returns:
        JSON: Result of the operation
    """
    if action not in ['start', 'stop']:
        return jsonify({
            "error": "invalid_action",
            "message": "Action must be either 'start' or 'stop'"
        }), 400
        
    try:
        if not current_user.is_authenticated:
            raise ValueError("User not authenticated")
            
        username = current_user.username
        password = _user_passwords.get(username)
        
        if not username or not password:
            raise ValueError("Missing credentials")
            
        # Call manage_jboss function with the credentials
        manage_jboss(server_id, action, username, password, "config/server_config.json")
        
        return jsonify({
            "success": True,
            "message": f"EAP {action} operation initiated successfully"
        })
        
    except Exception as e:
        return jsonify({
            "error": "operation_failed",
            "message": str(e)
        }), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login route, handles both GET and POST requests
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if AuthManager.authenticate_user(username, password):
            # Store user in session with password
            user = User(username, password)
            _user_passwords[username] = password  # Store password for session
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """
    Logout route
    """
    if current_user.is_authenticated:
        _user_passwords.pop(current_user.username, None)  # Remove password on logout
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=3000)
