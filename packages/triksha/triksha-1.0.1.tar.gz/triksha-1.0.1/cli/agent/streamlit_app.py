"""
Dravik Agent Streamlit App
Streamlit UI for the Dravik Agent
"""
import os
import sys
import json
import streamlit as st
import threading
import time
import datetime
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
import hashlib
import hmac
import base64
import secrets
import requests

# Add parent directory to path to allow importing from other Dravik modules
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import the DravikAgent class
from cli.agent.dravik_agent import DravikAgent
from db_handler import DravikDB
from cli.commands.benchmark.command import BenchmarkCommands

# Configure the Streamlit page
st.set_page_config(
    page_title="Dravik Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/dravik-org/dravik',
        'Report a bug': 'https://github.com/dravik-org/dravik/issues',
        'About': 'Dravik - A red teaming platform for detecting vulnerabilities in LLMs'
    }
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #4e54c8;
        --secondary-color: #8f94fb;
        --background-color: #1e1e2e;
        --text-color: #f8f8f2;
        --card-bg: #2a2a3c;
        --success-color: #50fa7b;
        --warning-color: #ffb86c;
        --error-color: #ff5555;
    }
    
    /* Global styles */
    .main {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    
    h1, h2, h3 {
        color: white !important;
        font-weight: 600 !important;
    }

    /* Custom card component */
    .stCard {
        background-color: var(--card-bg);
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        border-left: 4px solid var(--primary-color);
    }
    
    /* Custom button styles */
    .stButton > button {
        background-color: var(--primary-color);
        color: white;
        border-radius: 6px;
        transition: all 0.3s ease;
        border: none;
        padding: 0.5rem 1rem;
    }
    
    .stButton > button:hover {
        background-color: var(--secondary-color);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        transform: translateY(-2px);
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        max-width: 80%;
    }
    
    .chat-message.user {
        background-color: var(--primary-color);
        margin-left: auto;
    }
    
    .chat-message.assistant {
        background-color: var(--card-bg);
        margin-right: auto;
    }
    
    /* Wizard steps indicator */
    .step-indicator {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
    }
    
    .step {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-color: var(--card-bg);
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
    }
    
    .step.active {
        background-color: var(--primary-color);
        color: white;
    }
    
    .step.completed {
        background-color: var(--success-color);
        color: black;
    }
    
    .step-line {
        flex-grow: 1;
        height: 3px;
        background-color: var(--card-bg);
        margin: 0 10px;
    }
    
    .step-line.completed {
        background-color: var(--success-color);
    }
    
    /* Radio buttons and checkboxes */
    .stRadio > div {
        background-color: var(--card-bg);
        border-radius: 8px;
        padding: 10px;
    }
    
    .stRadio > div:hover {
        background-color: rgba(78, 84, 200, 0.1);
    }
    
    /* Multiselect */
    .stMultiSelect > div {
        background-color: var(--card-bg);
        border-radius: 8px;
    }
    
    /* Add spacing to dividers */
    hr {
        margin: 30px 0;
    }
    
    /* Animations */
    @keyframes gradient {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    
    .gradient-text {
        background: linear-gradient(-45deg, #4e54c8, #8f94fb, #4776E6);
        background-size: 200% auto;
        color: transparent;
        -webkit-background-clip: text;
        background-clip: text;
        animation: gradient 3s ease infinite;
        font-weight: bold;
    }
    
    /* Logo animation */
    @keyframes pulse {
        0% {transform: scale(1);}
        50% {transform: scale(1.05);}
        100% {transform: scale(1);}
    }
    
    .logo {
        animation: pulse 2s infinite;
    }
    
    /* Improved sidebar styling */
    .css-1d391kg {
        background-color: #252536;
    }
    
    /* Progress bars */
    .stProgress > div > div {
        background-color: var(--primary-color);
    }
    
    /* Split layout styling */
    .split-container {
        display: flex;
        flex-direction: row;
        gap: 20px;
        width: 100%;
    }
    
    .chat-container {
        flex: 3;
        padding-right: 1rem;
        overflow-y: auto;
        max-height: 85vh;
    }
    
    .config-container {
        flex: 2;
        padding: 1rem;
        background-color: var(--card-bg);
        border-radius: 10px;
        overflow-y: auto;
        max-height: 85vh;
        border-left: 1px solid rgba(250, 250, 250, 0.2);
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    .config-container h3 {
        margin-top: 0;
        margin-bottom: 1rem;
        border-bottom: 1px solid rgba(250, 250, 250, 0.2);
        padding-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Create a function to handle API key persistence
def load_api_keys():
    """Load API keys and authentication credentials from environment variables or local storage"""
    # Define the config file path in user's home directory
    config_dir = Path.home() / ".dravik"
    config_file = config_dir / "config.json"
    
    # Initialize keys dictionary
    keys = {
        "gemini": os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY") or "",
        "openai": os.environ.get("OPENAI_API_KEY") or "",
        "auth": {
            "username": os.environ.get("DRAVIK_USERNAME", "admin"),
            "password_hash": os.environ.get("DRAVIK_PASSWORD_HASH", ""),
            "salt": os.environ.get("DRAVIK_SALT", "")
        }
    }
    
    # Try to load from config file if it exists
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                stored_keys = json.load(f)
                # Only use stored keys if environment variables not set
                if not keys["gemini"]:
                    keys["gemini"] = stored_keys.get("gemini", "")
                if not keys["openai"]:
                    keys["openai"] = stored_keys.get("openai", "")
                
                # Load authentication details
                if "auth" in stored_keys:
                    # If password hash isn't set in env vars, use stored one
                    if not keys["auth"]["password_hash"]:
                        keys["auth"]["username"] = stored_keys["auth"].get("username", "admin")
                        keys["auth"]["password_hash"] = stored_keys["auth"].get("password_hash", "")
                        keys["auth"]["salt"] = stored_keys["auth"].get("salt", "")
        except Exception as e:
            print(f"Error loading config: {e}")
    
    return keys

def save_api_keys(keys):
    """Save API keys and authentication credentials to local storage"""
    # Define the config file path in user's home directory
    config_dir = Path.home() / ".dravik"
    config_file = config_dir / "config.json"
    
    # Create directory if it doesn't exist
    config_dir.mkdir(exist_ok=True)
    
    try:
        # Write keys to config file
        with open(config_file, "w") as f:
            json.dump(keys, f)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

# Add authentication helper functions
def hash_password(password, salt=None):
    """Hash password with salt using PBKDF2 with SHA-256"""
    # Generate a new salt if none provided
    if salt is None:
        salt = secrets.token_bytes(16)
        salt_hex = salt.hex()
    else:
        # If salt is provided as hex string, convert to bytes
        if isinstance(salt, str):
            salt = bytes.fromhex(salt)
            salt_hex = salt.hex()
        else:
            salt_hex = salt.hex()
    
    # Convert password to bytes
    password_bytes = password.encode('utf-8')
    
    # Use PBKDF2 HMAC with SHA-256
    key = hashlib.pbkdf2_hmac('sha256', password_bytes, salt, 100000)
    password_hash = key.hex()
    
    # Debug print
    print(f"Generated hash: {password_hash}")
    print(f"Salt (hex): {salt_hex}")
    
    # Return the salt and the key as hex strings
    return salt_hex, password_hash

def verify_password(stored_hash, salt, provided_password):
    """Verify a password against a stored hash and salt"""
    # Convert salt from hex to bytes if it's a string
    if isinstance(salt, str):
        salt_bytes = bytes.fromhex(salt)
    else:
        salt_bytes = salt
        
    # Convert provided password to bytes
    password_bytes = provided_password.encode('utf-8')
    
    # Generate hash with same parameters
    key = hashlib.pbkdf2_hmac('sha256', password_bytes, salt_bytes, 100000)
    new_hash = key.hex()
    
    # Debug print
    print(f"Comparing stored hash: {stored_hash} with generated hash: {new_hash}")
    
    # Compare the hashes
    return hmac.compare_digest(stored_hash, new_hash)

def check_password(username, password, config):
    """Check if username and password match stored credentials"""
    stored_username = config["auth"]["username"]
    stored_hash = config["auth"]["password_hash"]
    stored_salt = config["auth"]["salt"]
    
    # Print debug info
    print(f"Checking password for user: {username}")
    print(f"Stored username: {stored_username}")
    print(f"Stored hash exists: {bool(stored_hash)}")
    print(f"Stored salt exists: {bool(stored_salt)}")
    
    # Check if username matches
    if username != stored_username:
        print("Username mismatch")
        return False
    
    # If no password is set, any password is valid (first-time login)
    if not stored_hash or not stored_salt:
        print("No stored hash or salt - first time login")
        return True
    
    # Verify password
    result = verify_password(stored_hash, stored_salt, password)
    print(f"Password verification result: {result}")
    return result

def set_password(username, password, config):
    """Set a new password for the user"""
    # Generate salt and hash the password
    salt, password_hash = hash_password(password)
    
    # Update the config
    config["auth"]["username"] = username
    config["auth"]["password_hash"] = password_hash
    config["auth"]["salt"] = salt
    
    # Save the updated config
    return save_api_keys(config)

# Initialize session state before doing anything else
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.messages = []
    st.session_state.current_task = None
    st.session_state.task_status = "idle"
    st.session_state.pending_action = None
    st.session_state.red_teaming_config = {}
    st.session_state.conversation_config = {}
    st.session_state.task_steps = []
    st.session_state.current_step_index = 0
    st.session_state.advanced_mode = False
    
    # Load API keys from persistent storage
    api_keys = load_api_keys()
    
    # Set API keys in session state
    st.session_state.api_keys = api_keys
    
    # Make sure keys are set in environment variables too
    if api_keys["gemini"]:
        os.environ["GOOGLE_API_KEY"] = api_keys["gemini"]
    if api_keys["openai"]:
        os.environ["OPENAI_API_KEY"] = api_keys["openai"]
    
    # Initialize database connection
    try:
        st.session_state.dravik_db = DravikDB()
        gemini_api_key = api_keys["gemini"]
        st.session_state.agent = DravikAgent(db=st.session_state.dravik_db, api_key=gemini_api_key)
    except Exception as e:
        st.error(f"Error initializing database: {str(e)}")
        st.session_state.dravik_db = None
        st.session_state.agent = DravikAgent(db=None, api_key=api_keys["gemini"])
    
    # Report initialization status
    print("Initialized session state successfully")

# Add authentication section
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.login_attempts = 0

# Check if the default password has been set
default_password_not_set = not st.session_state.api_keys["auth"]["password_hash"]

# Authentication logic
if not st.session_state.authenticated:
    # Force the user to create a password if none exists
    if default_password_not_set:
        st.title("Welcome to Dravik Agent")
        st.markdown("### Initial Setup Required")
        st.warning("No password has been set. Please create an administrator account.")
        
        with st.form("create_admin"):
            new_username = st.text_input("Admin Username", value="admin")
            new_password = st.text_input("Admin Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            submit = st.form_submit_button("Create Admin Account")
            
            if submit:
                if not new_username or len(new_username) < 3:
                    st.error("Username must be at least 3 characters long")
                elif not new_password or len(new_password) < 6:
                    st.error("Password must be at least 6 characters long")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    # Set the new password
                    if set_password(new_username, new_password, st.session_state.api_keys):
                        st.success("Admin account created successfully!")
                        st.session_state.authenticated = True
                        st.rerun()
                    else:
                        st.error("Failed to save credentials. Please try again.")
    else:
        # Show login form
        st.title("Dravik Agent Login")
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login")
                
                if submit:
                    if check_password(username, password, st.session_state.api_keys):
                        st.session_state.authenticated = True
                        st.session_state.login_attempts = 0
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.session_state.login_attempts += 1
                        st.error(f"Invalid username or password. Attempt {st.session_state.login_attempts}/3")
                        
                        # Lock out after 3 failed attempts
                        if st.session_state.login_attempts >= 3:
                            st.warning("Too many failed login attempts. Please try again later.")
                            time.sleep(3)  # Add a delay to prevent brute force
                            st.session_state.login_attempts = 0
        
        with col2:
            st.markdown("""
            <div style="background-color: rgba(0, 0, 0, 0.1); padding: 20px; border-radius: 10px;">
                <h3>Welcome to Dravik</h3>
                <p>A secure platform for LLM red teaming and evaluation.</p>
                <p>Please log in to continue.</p>
            </div>
            """, unsafe_allow_html=True)
else:
    # Add logout button to the sidebar if user is authenticated
    with st.sidebar:
        if st.button("🔒 Logout"):
            st.session_state.authenticated = False
            st.rerun()
    
    # Custom function to create a styled card
    def card(title, content, icon=""):
        st.markdown(f"""
        <div class="stCard">
            <h3>{icon} {title}</h3>
            <div>{content}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Only continue with the rest of the app if authenticated
    # Page header with animation
    col1, col2 = st.columns([1, 5])
    with col1:
        st.markdown('<div class="logo">🤖</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<h1>Dravik <span class="gradient-text">Agent</span></h1>', unsafe_allow_html=True)
        st.markdown('<p>Natural language interface for the Dravik red teaming platform</p>', unsafe_allow_html=True)

    # Sidebar for configuration with improved styling
    with st.sidebar:
        st.markdown('<h2><i class="fas fa-cogs"></i> Configuration</h2>', unsafe_allow_html=True)
        
        # Create a card-like container for the API key
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.markdown("### 🔑 API Keys")
        
        # Gemini API Key
        api_key = st.text_input(
            "Gemini API Key", 
            value=st.session_state.api_keys["gemini"],
            type="password",
            help="Enter your Google Gemini API key to enable advanced NLP capabilities"
        )
        
        # OpenAI API Key
        openai_api_key = st.text_input(
            "OpenAI API Key", 
            value=st.session_state.api_keys["openai"],
            type="password",
            help="Enter your OpenAI API key for OpenAI models"
        )
        
        # Save API key
        if st.button("💾 Save API Keys"):
            keys_changed = False
            
            if api_key != st.session_state.api_keys["gemini"]:
                st.session_state.api_keys["gemini"] = api_key
                os.environ["GOOGLE_API_KEY"] = api_key
                keys_changed = True
                
            if openai_api_key != st.session_state.api_keys["openai"]:
                st.session_state.api_keys["openai"] = openai_api_key
                os.environ["OPENAI_API_KEY"] = openai_api_key
                keys_changed = True
            
            if keys_changed:
                # Save keys to persistent storage
                if save_api_keys(st.session_state.api_keys):
                    st.success("API keys saved successfully! Settings will persist between sessions.")
                else:
                    st.warning("API keys saved for this session only.")
                
                # Reinitialize agent with new API key
                if "agent" in st.session_state:
                    st.session_state.agent = DravikAgent(db=st.session_state.dravik_db, api_key=api_key)
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Security settings
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.markdown("### 🔐 Security Settings")
        
        # Option to change password
        if st.checkbox("Change Password"):
            with st.form("change_password_form"):
                current_username = st.session_state.api_keys["auth"]["username"]
                new_username = st.text_input("New Username", value=current_username)
                current_password = st.text_input("Current Password", type="password")
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm New Password", type="password")
                
                update_button = st.form_submit_button("Update Credentials")
                
                if update_button:
                    # Verify current password
                    if not check_password(current_username, current_password, st.session_state.api_keys):
                        st.error("Current password is incorrect")
                    elif not new_username or len(new_username) < 3:
                        st.error("Username must be at least 3 characters long")
                    elif not new_password or len(new_password) < 6:
                        st.error("New password must be at least 6 characters long")
                    elif new_password != confirm_password:
                        st.error("New passwords do not match")
                    else:
                        # Update credentials
                        if set_password(new_username, new_password, st.session_state.api_keys):
                            st.success("Credentials updated successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to update credentials")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.markdown("### ⚙️ Display Options")
        
        # Advanced mode toggle with better styling
        advanced_mode = st.toggle(
            "Advanced Mode", 
            value=st.session_state.get("advanced_mode", False),
            help="Enable advanced features and detailed task planning"
        )
        if advanced_mode != st.session_state.get("advanced_mode", False):
            st.session_state.advanced_mode = advanced_mode
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick actions section
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.markdown("### ⚡ Quick Actions")
        
        # Show buttons for common actions with fixed direct action handling
        sidebar_col1, sidebar_col2 = st.columns(2)
        
        with sidebar_col1:
            if st.button("🧪 Red Teaming", key="sidebar_static_redteam"):
                st.session_state.pending_action = {"type": "red_teaming_static"}
                st.rerun()
                
            if st.button("📊 View Results", key="sidebar_view_results"):
                st.session_state.pending_action = {"type": "view_results"}
                st.rerun()
        
        with sidebar_col2:
            if st.button("💬 Conversation Test", key="sidebar_conv_redteam"):
                st.session_state.pending_action = {"type": "red_teaming_conversation"}
                st.rerun()
                
            if st.button("🤖 Manage Models", key="sidebar_manage_models"):
                st.session_state.pending_action = {"type": "list_models"}
                st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)

    # Main content area with tabs
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📋 Tasks", "ℹ️ Help"])

    with tab1:
        # Create a split container for the UI
        if st.session_state.pending_action:
            # Create a split layout with chat on left and configuration on right
            st.markdown('<div class="split-container">', unsafe_allow_html=True)
            
            # Left side - Chat area
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            
            # Display chat messages
            if not st.session_state.messages:
                # Show welcome message if no messages
                st.markdown("""
                <div class="stCard">
                    <h3>👋 Welcome to Dravik Agent</h3>
                    <p>I'm an agent for the Dravik CLI. Here's what I can help you with:</p>
                    <ol>
                        <li><strong>Red Teaming</strong> - Run static or conversation-based red teaming benchmarks</li>
                        <li><strong>View Results</strong> - View and analyze benchmark results</li>
                        <li><strong>Custom Models</strong> - Register, list, or delete custom models</li>
                        <li><strong>Scheduled Benchmarks</strong> - Configure, list, or delete scheduled benchmarks</li>
                    </ol>
                    <p>Just tell me what you'd like to do, and I'll guide you through the process!</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Display existing messages
                for i, message in enumerate(st.session_state.messages):
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
            
            # User input
            prompt = st.chat_input("Enter your request...")
            if prompt:
                # Add user message to chat history
                user_msg = {"role": "user", "content": prompt}
                st.session_state.messages.append(user_msg)
                
                # Process the message with the agent
                try:
                    # Process the message with the agent
                    response = st.session_state.agent.handle_message(prompt)
                    
                    if response and "content" in response:
                        # Add assistant message to chat history
                        assistant_msg = {"role": "assistant", "content": response["content"]}
                        st.session_state.messages.append(assistant_msg)
                        
                        # Handle specific response types with better parameter extraction
                        if "type" in response and response["type"] not in ["text", "help"]:
                            if response["type"] == "red_teaming_static":
                                # Extract parameters from the response if they're provided
                                params = response.get("parameters", {})
                                # Set defaults for required parameters
                                if "models" not in params and "model" in params:
                                    params["models"] = [params["model"]]
                                
                                st.session_state.pending_action = {
                                    "type": "red_teaming_static",
                                    "params": params,
                                    # Set defaults for missing parameters
                                    "models": params.get("models", []),
                                    "dataset_source": params.get("dataset_source", "Internal datasets"),
                                    "dataset_type": params.get("dataset_type", "Static Templates"),
                                    "num_prompts": params.get("num_prompts", 20),
                                    "generation_method": params.get("generation_method", "jailbreak"),
                                    "skip_wizard": params.get("skip_wizard", False)
                                }
                            elif response["type"] == "red_teaming_conversation":
                                # Check if we should skip the wizard based on NLP extraction
                                if st.session_state.pending_action.get("skip_wizard", False):
                                    # Get parameters from pending_action
                                    models = st.session_state.pending_action.get("models", [])
                                    attack_vectors = st.session_state.pending_action.get("attack_vectors", ["jailbreak"])
                                    num_attempts = st.session_state.pending_action.get("num_attempts", 3)
                                    
                                    # Display summary
                                    st.write("### Running Conversation Red Teaming Benchmark")
                                    st.write("Starting conversation benchmark with the following parameters:")
                                    
                                    st.markdown(f"""
                                    **Models:** {', '.join(models)}  
                                    **Attack Vectors:** {', '.join(attack_vectors)}  
                                    **Attempts per Model:** {num_attempts}
                                    """)
                                    
                                    # Show progress indicator
                                    progress_bar = st.progress(0)
                                    for i in range(100):
                                        # Simulating progress
                                        progress_bar.progress(i + 1)
                                        time.sleep(0.02)
                                    
                                    # Get the response message from pending_action
                                    response = st.session_state.pending_action.get("content", 
                                        f"Started conversation red teaming benchmark with {len(models)} models using {', '.join(attack_vectors)} attack vectors.")
                                    
                                    # Add to chat history
                                    st.session_state.messages.append({"role": "assistant", "content": response})
                                    
                                    # Clear the pending action
                                    st.session_state.pending_action = None
                                    st.success("Conversation benchmark started successfully!")
                                    st.rerun()
                                else:
                                    # Create a step-by-step flow
                                    if 'conversation_step' not in st.session_state:
                                        st.session_state.conversation_step = 1

                                    st.write("### Configure Conversation Red Teaming")
                                    st.progress(st.session_state.conversation_step / 3)  # 3 total steps
                                    
                                    # Step indicators
                                    cols = st.columns(3)
                                    for i in range(3):
                                        with cols[i]:
                                            if i + 1 < st.session_state.conversation_step:
                                                st.markdown(f"<div style='text-align: center;'><span style='background-color: #50fa7b; color: black; border-radius: 50%; padding: 5px 10px;'>{i+1}</span></div>", unsafe_allow_html=True)
                                            elif i + 1 == st.session_state.conversation_step:
                                                st.markdown(f"<div style='text-align: center;'><span style='background-color: #4e54c8; color: white; border-radius: 50%; padding: 5px 10px;'>{i+1}</span></div>", unsafe_allow_html=True)
                                            else:
                                                st.markdown(f"<div style='text-align: center;'><span style='background-color: #2a2a3c; color: white; border-radius: 50%; padding: 5px 10px;'>{i+1}</span></div>", unsafe_allow_html=True)
                                    
                                    # Step 1: Model Selection
                                    if st.session_state.conversation_step == 1:
                                        st.subheader("Select Models for Conversation Testing")
                                        
                                        # Provider selection
                                        provider_options = ["OpenAI", "Gemini", "Custom", "All"]
                                        providers = st.multiselect(
                                            "Select model providers:",
                                            provider_options,
                                            key="conv_providers"
                                        )
                                        
                                        # Initialize selected models list
                                        all_selected_models = []
                                        
                                        # Show models for each selected provider
                                        if "OpenAI" in providers:
                                            openai_models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
                                            openai_selected = st.multiselect(
                                                "Select OpenAI models:",
                                                openai_models,
                                                key="conv_openai_models"
                                            )
                                            all_selected_models.extend([f"openai:{model}" for model in openai_selected])
                                        
                                        if "Gemini" in providers:
                                            gemini_models = ["gemini-pro", "gemini-1.5-pro", "gemini-1.5-flash"]
                                            gemini_selected = st.multiselect(
                                                "Select Gemini models:",
                                                gemini_models,
                                                key="conv_gemini_models"
                                            )
                                            all_selected_models.extend([f"gemini:{model}" for model in gemini_selected])
                                        
                                        if "Custom" in providers:
                                            custom_models = ["custom-model-1", "custom-model-2"]
                                            custom_selected = st.multiselect(
                                                "Select custom models:",
                                                custom_models,
                                                key="conv_custom_models"
                                            )
                                            all_selected_models.extend([f"custom:{model}" for model in custom_selected])
                                        
                                        # Manual model entry
                                        st.write("Or enter models manually:")
                                        manual_models_input = st.text_area(
                                            "Enter models manually (one per line):",
                                            key="conv_manual_models",
                                            help="Format: provider:model_name (e.g., openai:gpt-4)"
                                        )
                                        
                                        # Process manual input
                                        manual_models = []
                                        if manual_models_input:
                                            for line in manual_models_input.split('\n'):
                                                if line.strip():
                                                    # Add provider prefix if not present
                                                    if ":" not in line.strip():
                                                        if line.startswith("gpt"):
                                                            model = f"openai:{line.strip()}"
                                                        elif line.startswith("gemini"):
                                                            model = f"gemini:{line.strip()}"
                                                        else:
                                                            model = f"custom:{line.strip()}"
                                                    else:
                                                        model = line.strip()
                                                    
                                                    manual_models.append(model)
                                        
                                        # Combine all models
                                        final_models = all_selected_models + [m for m in manual_models if m not in all_selected_models]
                                        
                                        col1, col2 = st.columns(2)
                                        with col2:
                                            if st.button("Next →", key="next_conv_models"):
                                                if not final_models:
                                                    st.error("Please select at least one model")
                                                else:
                                                    # Store selection and advance to next step
                                                    st.session_state.conv_selected_models = final_models
                                                    st.session_state.conversation_step = 2
                                                    st.rerun()
                                    
                                    # Step 2: Attack Vector Configuration
                                    elif st.session_state.conversation_step == 2:
                                        st.subheader("Configure Attack Vectors")
                                        
                                        # Attack vector selection
                                        attack_vectors = st.multiselect(
                                            "Select attack vectors to test:",
                                            ["jailbreak", "harmful_content", "personal_information", "illegal_activity", "hate_speech"],
                                            default=["jailbreak"],
                                            key="conv_attack_vectors"
                                        )
                                        
                                        # Number of attempts setting
                                        num_attempts = st.slider(
                                            "Number of conversation attempts per model:",
                                            min_value=1,
                                            max_value=10,
                                            value=3,
                                            step=1,
                                            key="conv_num_attempts"
                                        )
                                        
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            if st.button("← Back", key="back_conv_attack"):
                                                st.session_state.conversation_step = 1
                                                st.rerun()
                                        with col2:
                                            if st.button("Next →", key="next_conv_attack"):
                                                if not attack_vectors:
                                                    st.error("Please select at least one attack vector")
                                                else:
                                                    # Store selection and advance to next step
                                                    st.session_state.conv_attack_vectors = attack_vectors
                                                    st.session_state.conv_num_attempts = num_attempts
                                                    st.session_state.conversation_step = 3
                                                    st.rerun()
                                    
                                    # Step 3: Review and Submit
                                    elif st.session_state.conversation_step == 3:
                                        st.subheader("Review and Start Benchmark")
                                        
                                        # Show review information
                                        st.write("#### Configuration Summary")
                                        st.markdown(f"""
                                        **Selected Models:** {", ".join(st.session_state.conv_selected_models)}  
                                        **Attack Vectors:** {", ".join(st.session_state.conv_attack_vectors)}  
                                        **Attempts per Model:** {st.session_state.conv_num_attempts}
                                        """)
                                        
                                        # Show help info
                                        st.info("The conversation red teaming will attempt to elicit harmful or inappropriate responses through multi-turn conversations. Each selected attack vector will be tried with different approaches.")
                                        
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            if st.button("← Back", key="back_conv_review"):
                                                st.session_state.conversation_step = 2
                                                st.rerun()
                                        with col2:
                                            if st.button("Start Benchmark", key="start_conv_test"):
                                                # Create response message
                                                response = f"Starting conversation red teaming benchmark with:\n\n" \
                                                          f"- Models: {', '.join(st.session_state.conv_selected_models)}\n" \
                                                          f"- Attack vectors: {', '.join(st.session_state.conv_attack_vectors)}\n" \
                                                          f"- Attempts per model: {st.session_state.conv_num_attempts}"
                                                
                                                st.session_state.messages.append({"role": "assistant", "content": response})
                                                
                                                # Clear the conversation flow state
                                                if 'conversation_step' in st.session_state:
                                                    del st.session_state.conversation_step
                                                if 'conv_selected_models' in st.session_state:
                                                    del st.session_state.conv_selected_models
                                                if 'conv_attack_vectors' in st.session_state:
                                                    del st.session_state.conv_attack_vectors
                                                if 'conv_num_attempts' in st.session_state:
                                                    del st.session_state.conv_num_attempts
                                                
                                                # Clear the pending action
                                                st.session_state.pending_action = None
                                                st.success("Conversation benchmark started successfully!")
                                                st.rerun()
                    
                    st.rerun()
                except Exception as e:
                    # Handle any errors
                    error_msg = f"Error processing your request: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": f"⚠️ {error_msg}"})
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Right side - Configuration area
            st.markdown('<div class="config-container">', unsafe_allow_html=True)
            
            st.markdown(f"<h3>Configure {st.session_state.pending_action.get('type').replace('_', ' ').title()}</h3>", unsafe_allow_html=True)
            
            # Set up the appropriate configuration panel based on action type
            if st.session_state.pending_action.get("type") == "red_teaming_static":
                # Check if we should skip the wizard based on NLP extraction
                if st.session_state.pending_action.get("skip_wizard", False):
                    # Get parameters from pending_action
                    models = st.session_state.pending_action.get("models", [])
                    num_prompts = st.session_state.pending_action.get("num_prompts", 20)
                    generation_method = st.session_state.pending_action.get("generation_method", "jailbreak")
                    dataset_source = st.session_state.pending_action.get("dataset_source", "Internal datasets")
                    dataset_type = st.session_state.pending_action.get("dataset_type", "Static Templates")
                    
                    # Display summary 
                    st.write("### Running Red Teaming Benchmark")
                    st.write("Starting benchmark with the following parameters:")
                    
                    st.markdown(f"""
                    **Models:** {', '.join(models)}  
                    **Dataset Source:** {dataset_source}  
                    **Dataset Type:** {dataset_type}  
                    **Number of Prompts:** {num_prompts}  
                    **Generation Method:** {generation_method}
                    """)
                    
                    # Show progress indicator
                    progress_bar = st.progress(0)
                    for i in range(100):
                        # Simulating progress
                        progress_bar.progress(i + 1)
                        time.sleep(0.02)
                    
                    # Get the response message from pending_action
                    response = st.session_state.pending_action.get("content", 
                        f"Started static red teaming benchmark with {len(models)} models and {num_prompts} prompts.")
                    
                    # Add to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # Clear the pending action
                    st.session_state.pending_action = None
                    st.success("Benchmark started successfully!")
                    st.rerun()
                else:
                    # Create a step-by-step flow that matches the CLI
                    if 'benchmark_step' not in st.session_state:
                        st.session_state.benchmark_step = 1

                    st.write("### Configure Red Teaming Benchmark")
                    st.progress(st.session_state.benchmark_step / 5)  # 5 total steps
                    
                    # Step indicators
                    cols = st.columns(5)
                    for i in range(5):
                        with cols[i]:
                            if i + 1 < st.session_state.benchmark_step:
                                st.markdown(f"<div style='text-align: center;'><span style='background-color: #50fa7b; color: black; border-radius: 50%; padding: 5px 10px;'>{i+1}</span></div>", unsafe_allow_html=True)
                            elif i + 1 == st.session_state.benchmark_step:
                                st.markdown(f"<div style='text-align: center;'><span style='background-color: #4e54c8; color: white; border-radius: 50%; padding: 5px 10px;'>{i+1}</span></div>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div style='text-align: center;'><span style='background-color: #2a2a3c; color: white; border-radius: 50%; padding: 5px 10px;'>{i+1}</span></div>", unsafe_allow_html=True)
                    
                    # Step 1: Dataset Source
                    if st.session_state.benchmark_step == 1:
                        st.subheader("Where would you like to get your dataset from?")
                        dataset_source = st.radio(
                            "Dataset Source:",
                            ["Internal datasets", "Public datasets"],
                            key="dataset_source"
                        )
                        
                        col1, col2 = st.columns(2)
                        with col2:
                            if st.button("Next →", key="next_dataset_source"):
                                # Store selection in session state
                                st.session_state.selected_dataset_source = dataset_source
                                st.session_state.benchmark_step = 2
                                st.rerun()
                
                    # Step 2: Dataset Type
                    elif st.session_state.benchmark_step == 2:
                        st.subheader("What type of dataset would you like to use?")
                        dataset_type = st.radio(
                            "Dataset Type:",
                            ["Static Templates (predefined templates)", "From Existing Dataset"],
                            key="dataset_type"
                        )
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("← Back", key="back_dataset_type"):
                                st.session_state.benchmark_step = 1
                                st.rerun()
                        with col2:
                            if st.button("Next →", key="next_dataset_type"):
                                # Store selection in session state
                                st.session_state.selected_dataset_type = dataset_type
                                st.session_state.benchmark_step = 3
                                st.rerun()
                
                    # Step 3: Model Provider Selection
                    elif st.session_state.benchmark_step == 3:
                        st.subheader("Which types of models would you like to benchmark?")
                        model_provider = st.radio(
                            "Model Provider:",
                            ["Ollama", "OpenAI", "Gemini", "Custom", "All"],
                            key="model_provider"
                        )
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("← Back", key="back_provider"):
                                st.session_state.benchmark_step = 2
                                st.rerun()
                        with col2:
                            if st.button("Next →", key="next_provider"):
                                # Store selection in session state
                                st.session_state.selected_provider = model_provider
                                st.session_state.benchmark_step = 4
                                st.rerun()
                
                    # Step 4: Model Selection
                    elif st.session_state.benchmark_step == 4:
                        st.subheader(f"Select {st.session_state.selected_provider} models to benchmark")
                        
                        # Model selection logic based on provider
                        if st.session_state.selected_provider == "Ollama":
                            # Placeholder for Ollama models
                            ollama_models = ["llama3", "mistral", "codellama", "phi3", "gemma"]
                            selected_models = st.multiselect(
                                "Select Ollama models:",
                                ollama_models,
                                key="ollama_models"
                            )
                        elif st.session_state.selected_provider == "OpenAI":
                            # OpenAI models
                            openai_models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o"]
                            selected_models = st.multiselect(
                                "Select OpenAI models:",
                                openai_models,
                                key="openai_models"
                            )
                        elif st.session_state.selected_provider == "Gemini":
                            # Gemini models
                            gemini_models = ["gemini-pro", "gemini-1.5-pro", "gemini-1.5-flash"]
                            selected_models = st.multiselect(
                                "Select Gemini models:",
                                gemini_models,
                                key="gemini_models"
                            )
                        elif st.session_state.selected_provider == "Custom":
                            # Custom models list
                            custom_models = ["custom-model-1", "custom-model-2"]
                            selected_models = st.multiselect(
                                "Select custom models:",
                                custom_models,
                                key="custom_models"
                            )
                        elif st.session_state.selected_provider == "All":
                            # All available models
                            all_models = [
                                "ollama:llama3", "ollama:mistral", 
                                "openai:gpt-3.5-turbo", "openai:gpt-4", 
                                "gemini:gemini-pro", "gemini:gemini-1.5-pro",
                                "custom:custom-model-1"
                            ]
                            selected_models = st.multiselect(
                                "Select from all available models:",
                                all_models,
                                key="all_models"
                            )
                        
                        # Manual model entry option
                        st.write("Or enter models manually:")
                        manual_entry = st.text_area(
                            "Enter model names (one per line):",
                            key="manual_models",
                            help="Format: provider:model_name (e.g., openai:gpt-4) or just model_name"
                        )
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("← Back", key="back_models"):
                                st.session_state.benchmark_step = 3
                                st.rerun()
                        with col2:
                            if st.button("Next →", key="next_models"):
                                # Combine selected models with manual entries
                                final_models = selected_models.copy()
                                if manual_entry:
                                    manual_models = [model.strip() for model in manual_entry.split('\n') if model.strip()]
                                    final_models.extend(manual_models)
                                
                                if not final_models:
                                    st.error("Please select at least one model or enter a model manually")
                                else:
                                    # Store selections in session state
                                    st.session_state.selected_models_list = final_models
                                    st.session_state.benchmark_step = 5
                                    st.rerun()
                
                    # Step 5: Configuration & Review
                    elif st.session_state.benchmark_step == 5:
                        st.subheader("Configure and Review")
                        
                        # Additional configuration options
                        st.write("##### Prompt Generation Settings")
                        generation_method = st.radio(
                            "Select prompt generation method:",
                            ["default", "fewshot", "conversation", "jailbreak"],
                            key="generation_method"
                        )
                        
                        num_prompts = st.slider(
                            "Number of prompts to generate:",
                            min_value=1,
                            max_value=100,
                            value=10,
                            key="num_prompts"
                        )
                        
                        # Review section
                        st.write("### Review Your Benchmark Configuration")
                        st.markdown(f"""
                        **Dataset Source:** {st.session_state.selected_dataset_source}  
                        **Dataset Type:** {st.session_state.selected_dataset_type}  
                        **Model Provider:** {st.session_state.selected_provider}  
                        **Models Selected:** {", ".join(st.session_state.selected_models_list)}  
                        **Generation Method:** {generation_method}  
                        **Number of Prompts:** {num_prompts}
                        """)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("← Back", key="back_config"):
                                st.session_state.benchmark_step = 4
                                st.rerun()
                        with col2:
                            if st.button("Run Benchmark", key="run_benchmark"):
                                # Prepare to run the benchmark
                                response = f"Starting red teaming benchmark with:\n\n" \
                                          f"- Dataset: {st.session_state.selected_dataset_source}, {st.session_state.selected_dataset_type}\n" \
                                          f"- Models: {', '.join(st.session_state.selected_models_list)}\n" \
                                          f"- Generation method: {generation_method}\n" \
                                          f"- Number of prompts: {num_prompts}"
                                
                                st.session_state.messages.append({"role": "assistant", "content": response})
                                
                                # Reset the benchmark flow
                                if 'benchmark_step' in st.session_state:
                                    del st.session_state.benchmark_step
                                if 'selected_dataset_source' in st.session_state:
                                    del st.session_state.selected_dataset_source
                                if 'selected_dataset_type' in st.session_state:
                                    del st.session_state.selected_dataset_type
                                if 'selected_provider' in st.session_state:
                                    del st.session_state.selected_provider
                                if 'selected_models_list' in st.session_state:
                                    del st.session_state.selected_models_list
                                
                                # Clear the pending action
                                st.session_state.pending_action = None
                                st.success("Benchmark started successfully!")
                                st.rerun()

            elif st.session_state.pending_action.get("type") == "view_results":
                # Create a step-by-step flow
                if 'results_step' not in st.session_state:
                    st.session_state.results_step = 1
                    st.session_state.selected_benchmark_type = None
                    st.session_state.selected_benchmark_id = None
                    st.session_state.results_data = None

                st.write("### View Benchmark Results")
                st.progress(st.session_state.results_step / 3)  # 3 total steps
                
                # Step indicators
                cols = st.columns(3)
                for i in range(3):
                    with cols[i]:
                        if i + 1 < st.session_state.results_step:
                            st.markdown(f"<div style='text-align: center;'><span style='background-color: #50fa7b; color: black; border-radius: 50%; padding: 5px 10px;'>{i+1}</span></div>", unsafe_allow_html=True)
                        elif i + 1 == st.session_state.results_step:
                            st.markdown(f"<div style='text-align: center;'><span style='background-color: #4e54c8; color: white; border-radius: 50%; padding: 5px 10px;'>{i+1}</span></div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div style='text-align: center;'><span style='background-color: #2a2a3c; color: white; border-radius: 50%; padding: 5px 10px;'>{i+1}</span></div>", unsafe_allow_html=True)
                
                # Step 1: Select Benchmark Type
                if st.session_state.results_step == 1:
                    st.subheader("Select Benchmark Type")
                    
                    benchmark_types = ["Red Teaming - Static", "Red Teaming - Conversation", "Model Comparison", "All Benchmarks"]
                    selected_type = st.radio(
                        "Select the type of benchmark results to view:",
                        benchmark_types,
                        key="results_benchmark_type"
                    )
                    
                    col1, col2 = st.columns(2)
                    with col2:
                        if st.button("Next →", key="next_results_type"):
                            st.session_state.selected_benchmark_type = selected_type
                            st.session_state.results_step = 2
                            st.rerun()
                
                # Step 2: Select Specific Benchmark
                elif st.session_state.results_step == 2:
                    st.subheader(f"Select {st.session_state.selected_benchmark_type} Benchmark")
                    
                    # In a real implementation, this would load actual benchmark IDs from storage
                    # For now, we'll use dummy data
                    benchmark_ids = {
                        "Red Teaming - Static": ["static-bench-20230615", "static-bench-20230712", "static-bench-20230827"],
                        "Red Teaming - Conversation": ["conv-bench-20230618", "conv-bench-20230715"],
                        "Model Comparison": ["model-comp-20230610", "model-comp-20230720"],
                        "All Benchmarks": ["bench-20230610", "bench-20230615", "bench-20230618", "bench-20230712", "bench-20230715", "bench-20230720", "bench-20230827"]
                    }
                    
                    # Get the list of benchmark IDs based on the selected type
                    available_benchmarks = benchmark_ids.get(st.session_state.selected_benchmark_type, [])
                    
                    if not available_benchmarks:
                        st.warning(f"No {st.session_state.selected_benchmark_type} benchmarks found.")
                        selected_benchmark = None
                    else:
                        # Create selection options with dates and additional info
                        benchmark_options = {
                            id: f"{id} - Run on {id.split('-')[-1][:4]}/{id.split('-')[-1][4:6]}/{id.split('-')[-1][6:]}" 
                            for id in available_benchmarks
                        }
                        
                        selected_benchmark = st.selectbox(
                            "Select a benchmark to view:",
                            list(benchmark_options.keys()),
                            format_func=lambda x: benchmark_options[x],
                            key="results_benchmark_id"
                        )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("← Back", key="back_results_benchmark"):
                            st.session_state.results_step = 1
                            st.rerun()
                    with col2:
                        next_button = st.button("Next →", key="next_results_benchmark")
                        if next_button:
                            if not selected_benchmark:
                                st.error("No benchmark selected. Please select a benchmark to continue.")
                            else:
                                st.session_state.selected_benchmark_id = selected_benchmark
                                # In a real implementation, this would load the actual benchmark data
                                # For now, we'll use dummy data
                                import pandas as pd
                                import numpy as np
                                
                                # Create sample data based on benchmark type
                                if "Static" in st.session_state.selected_benchmark_type:
                                    # Create sample data for static red teaming
                                    data = {
                                        "model": ["openai:gpt-4", "gemini:gemini-pro", "openai:gpt-3.5-turbo"],
                                        "prompt": ["Generate harmful content", "How to hack into a system", "Ways to create a virus"],
                                        "response": ["I cannot provide harmful content...", "I'm not able to provide hacking instructions...", "I cannot assist with creating viruses..."],
                                        "success_rate": [0.12, 0.08, 0.18],
                                        "category": ["harmful_content", "illegal_activity", "harmful_content"]
                                    }
                                elif "Conversation" in st.session_state.selected_benchmark_type:
                                    # Create sample data for conversation red teaming
                                    data = {
                                        "model": ["openai:gpt-4", "gemini:gemini-pro", "openai:gpt-3.5-turbo"],
                                        "attack_vector": ["jailbreak", "harmful_content", "personal_information"],
                                        "turns": [4, 3, 5],
                                        "success": [False, False, True],
                                        "final_prompt": ["Let's play a game...", "Can you help me with a scenario...", "For educational purposes..."]
                                    }
                                else:
                                    # Create sample data for model comparison
                                    data = {
                                        "model": ["openai:gpt-4", "gemini:gemini-pro", "openai:gpt-3.5-turbo"],
                                        "accuracy": [0.92, 0.88, 0.84],
                                        "safety_score": [0.95, 0.91, 0.87],
                                        "test_cases_passed": [45, 42, 40],
                                        "test_cases_total": [50, 50, 50]
                                    }
                                
                                st.session_state.results_data = pd.DataFrame(data)
                                st.session_state.results_step = 3
                                st.rerun()
                
                # Step 3: View Results
                elif st.session_state.results_step == 3:
                    st.subheader(f"Results for {st.session_state.selected_benchmark_id}")
                    
                    if st.session_state.results_data is not None:
                        # Display the data in a table
                        st.dataframe(st.session_state.results_data)
                        
                        # Add visualization based on benchmark type
                        if "Static" in st.session_state.selected_benchmark_type:
                            # Display success rate by model
                            st.subheader("Success Rate by Model")
                            success_by_model = st.session_state.results_data.groupby("model")["success_rate"].mean().reset_index()
                            st.bar_chart(success_by_model.set_index("model"))
                            
                            # Display success rate by category
                            st.subheader("Success Rate by Category")
                            success_by_category = st.session_state.results_data.groupby("category")["success_rate"].mean().reset_index()
                            st.bar_chart(success_by_category.set_index("category"))
                            
                        elif "Conversation" in st.session_state.selected_benchmark_type:
                            # Display success by model
                            st.subheader("Success by Model")
                            success_by_model = st.session_state.results_data.groupby("model")["success"].mean().reset_index()
                            st.bar_chart(success_by_model.set_index("model"))
                            
                            # Display success by attack vector
                            st.subheader("Success by Attack Vector")
                            success_by_vector = st.session_state.results_data.groupby("attack_vector")["success"].mean().reset_index()
                            st.bar_chart(success_by_vector.set_index("attack_vector"))
                            
                        else:
                            # Display model comparison
                            st.subheader("Model Comparison")
                            
                            # Calculate overall score
                            st.session_state.results_data["overall_score"] = (
                                st.session_state.results_data["accuracy"] * 0.4 + 
                                st.session_state.results_data["safety_score"] * 0.4 + 
                                (st.session_state.results_data["test_cases_passed"] / st.session_state.results_data["test_cases_total"]) * 0.2
                            )
                            
                            # Display metrics
                            metrics = ["accuracy", "safety_score", "overall_score"]
                            for metric in metrics:
                                st.subheader(f"{metric.replace('_', ' ').title()}")
                                st.bar_chart(st.session_state.results_data[["model", metric]].set_index("model"))
                        
                        # Export options
                        st.write("### Export Options")
                        export_format = st.radio("Export Format:", ["CSV", "JSON", "Excel"], horizontal=True)
                        
                        if st.button("Export Results"):
                            if export_format == "CSV":
                                st.success("Results exported to CSV successfully.")
                            elif export_format == "JSON":
                                st.success("Results exported to JSON successfully.")
                            elif export_format == "Excel":
                                st.success("Results exported to Excel successfully.")
                    else:
                        st.error("No results data available. Please go back and select a benchmark.")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("← Back", key="back_results_view"):
                            st.session_state.results_step = 2
                            st.rerun()
                    with col2:
                        if st.button("Close", key="close_results"):
                            # Create response message
                            response = f"Viewed results for benchmark: {st.session_state.selected_benchmark_id} ({st.session_state.selected_benchmark_type})"
                            st.session_state.messages.append({"role": "assistant", "content": response})
                            
                            # Clear the results flow state
                            if 'results_step' in st.session_state:
                                del st.session_state.results_step
                            if 'selected_benchmark_type' in st.session_state:
                                del st.session_state.selected_benchmark_type
                            if 'selected_benchmark_id' in st.session_state:
                                del st.session_state.selected_benchmark_id
                            if 'results_data' in st.session_state:
                                del st.session_state.results_data
                            
                            # Clear the pending action
                            st.session_state.pending_action = None
                            st.rerun()

            elif st.session_state.pending_action.get("type") == "list_models":
                st.write("### Registered Models")
                
                # In a real implementation, this would load actual models from storage
                # For now, we'll use dummy data
                registered_models = [
                    {"name": "GPT-4 Turbo", "id": "openai:gpt-4-turbo", "provider": "openai", "status": "Active"},
                    {"name": "Gemini Pro", "id": "gemini:gemini-pro", "provider": "gemini", "status": "Active"},
                    {"name": "Claude 3 Opus", "id": "anthropic:claude-3-opus", "provider": "anthropic", "status": "Active"},
                    {"name": "Llama 3", "id": "local:llama-3-70b", "provider": "local", "status": "Inactive"}
                ]
                
                # Add filtering options
                col1, col2 = st.columns(2)
                with col1:
                    # Filter by provider
                    providers = ["All Providers"] + list(set(model["provider"] for model in registered_models))
                    selected_provider = st.selectbox(
                        "Filter by provider:",
                        providers,
                        key="list_provider_filter"
                    )
                
                with col2:
                    # Filter by status
                    statuses = ["All Statuses"] + list(set(model["status"] for model in registered_models))
                    selected_status = st.selectbox(
                        "Filter by status:",
                        statuses,
                        key="list_status_filter"
                    )
                
                # Apply filters
                filtered_models = registered_models
                if selected_provider != "All Providers":
                    filtered_models = [m for m in filtered_models if m["provider"] == selected_provider]
                if selected_status != "All Statuses":
                    filtered_models = [m for m in filtered_models if m["status"] == selected_status]
                
                # Display models in a table
                if not filtered_models:
                    st.warning("No models found matching the selected filters.")
                else:
                    import pandas as pd
                    
                    # Convert to DataFrame for display
                    models_df = pd.DataFrame(filtered_models)
                    st.dataframe(models_df)
                
                # Quick action buttons
                st.write("### Actions")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("Register New Model", key="list_register_btn"):
                        # Switch to register model action
                        st.session_state.pending_action = {"type": "register_model"}
                        st.rerun()
                
                with col2:
                    if st.button("Delete Model", key="list_delete_btn"):
                        # Switch to delete model action
                        st.session_state.pending_action = {"type": "delete_model"}
                        st.rerun()
                
                with col3:
                    if st.button("Close", key="list_close_btn"):
                        # Create response message
                        if filtered_models:
                            response = f"Listed {len(filtered_models)} registered models"
                        else:
                            response = "No models found matching the selected filters"
                        
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        
                        # Clear the pending action
                        st.session_state.pending_action = None
                        st.rerun()

            elif st.session_state.pending_action.get("type") == "register_model":
                # Create a step-by-step flow
                if 'register_step' not in st.session_state:
                    st.session_state.register_step = 1

                st.write("### Register a New Model")
                st.progress(st.session_state.register_step / 3)  # 3 total steps
                
                # Step indicators
                cols = st.columns(3)
                for i in range(3):
                    with cols[i]:
                        if i + 1 < st.session_state.register_step:
                            st.markdown(f"<div style='text-align: center;'><span style='background-color: #50fa7b; color: black; border-radius: 50%; padding: 5px 10px;'>{i+1}</span></div>", unsafe_allow_html=True)
                        elif i + 1 == st.session_state.register_step:
                            st.markdown(f"<div style='text-align: center;'><span style='background-color: #4e54c8; color: white; border-radius: 50%; padding: 5px 10px;'>{i+1}</span></div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div style='text-align: center;'><span style='background-color: #2a2a3c; color: white; border-radius: 50%; padding: 5px 10px;'>{i+1}</span></div>", unsafe_allow_html=True)
                
                # Step 1: Select Model Type
                if st.session_state.register_step == 1:
                    st.subheader("Select Model Type")
                    
                    model_types = ["OpenAI API", "Gemini API", "Self-hosted API", "Azure OpenAI", "Local Model"]
                    model_type = st.radio(
                        "Select the type of model you want to register:",
                        model_types,
                        key="register_model_type"
                    )
                    
                    # Help text based on selected model type
                    help_texts = {
                        "OpenAI API": "Models that use OpenAI's API directly (e.g., GPT-4, GPT-3.5)",
                        "Gemini API": "Models that use Google's Gemini API",
                        "Self-hosted API": "Models that you're hosting with a compatible API (e.g., Llama, Mistral)",
                        "Azure OpenAI": "OpenAI models deployed through Azure",
                        "Local Model": "Models running locally on your machine"
                    }
                    st.info(help_texts.get(model_type, ""))
                    
                    col1, col2 = st.columns(2)
                    with col2:
                        if st.button("Next →", key="next_register_type"):
                            st.session_state.register_model_type = model_type
                            st.session_state.register_step = 2
                            st.rerun()
                
                # Step 2: Configure Model Details
                elif st.session_state.register_step == 2:
                    st.subheader(f"Configure {st.session_state.register_model_type} Model")
                    
                    # Common fields for all model types
                    model_name = st.text_input(
                        "Model Name (for display):",
                        key="register_model_name",
                        help="A friendly name to identify this model in the UI"
                    )
                    
                    model_id = st.text_input(
                        "Model ID:",
                        key="register_model_id",
                        help="The specific model identifier (e.g., gpt-4, gemini-pro)"
                    )
                    
                    # Type-specific fields
                    if st.session_state.register_model_type == "OpenAI API":
                        api_key = st.text_input(
                            "OpenAI API Key:",
                            type="password",
                            key="register_openai_key"
                        )
                        
                        organization = st.text_input(
                            "Organization ID (optional):",
                            key="register_openai_org"
                        )
                        
                        model_config = {
                            "provider": "openai",
                            "model_id": model_id,
                            "api_key": api_key,
                            "organization": organization if organization else None
                        }
                        
                    elif st.session_state.register_model_type == "Gemini API":
                        api_key = st.text_input(
                            "Gemini API Key:",
                            type="password",
                            key="register_gemini_key"
                        )
                        
                        model_config = {
                            "provider": "gemini",
                            "model_id": model_id,
                            "api_key": api_key
                        }
                        
                    elif st.session_state.register_model_type == "Self-hosted API":
                        api_url = st.text_input(
                            "API Endpoint URL:",
                            key="register_api_url",
                            help="The full URL to your API endpoint"
                        )
                        
                        api_key = st.text_input(
                            "API Key (if required):",
                            type="password",
                            key="register_api_key"
                        )
                        
                        model_config = {
                            "provider": "custom",
                            "model_id": model_id,
                            "api_url": api_url,
                            "api_key": api_key if api_key else None
                        }
                        
                    elif st.session_state.register_model_type == "Azure OpenAI":
                        api_key = st.text_input(
                            "Azure API Key:",
                            type="password",
                            key="register_azure_key"
                        )
                        
                        endpoint = st.text_input(
                            "Azure Endpoint:",
                            key="register_azure_endpoint",
                            help="Your Azure OpenAI service endpoint"
                        )
                        
                        deployment_name = st.text_input(
                            "Deployment Name:",
                            key="register_azure_deployment"
                        )
                        
                        model_config = {
                            "provider": "azure",
                            "model_id": model_id,
                            "api_key": api_key,
                            "endpoint": endpoint,
                            "deployment_name": deployment_name
                        }
                        
                    elif st.session_state.register_model_type == "Local Model":
                        model_path = st.text_input(
                            "Model Path:",
                            key="register_local_path",
                            help="Full path to the model weights or directory"
                        )
                        
                        device = st.selectbox(
                            "Device:",
                            ["cuda", "cpu", "mps"],
                            key="register_local_device"
                        )
                        
                        model_config = {
                            "provider": "local",
                            "model_id": model_id,
                            "model_path": model_path,
                            "device": device
                        }
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("← Back", key="back_register_details"):
                            st.session_state.register_step = 1
                            st.rerun()
                    with col2:
                        next_button = st.button("Next →", key="next_register_details")
                        if next_button:
                            if not model_name:
                                st.error("Please enter a model name")
                            elif not model_id:
                                st.error("Please enter a model ID")
                            elif st.session_state.register_model_type in ["OpenAI API", "Gemini API", "Azure OpenAI"] and not model_config.get("api_key"):
                                st.error("API key is required")
                            elif st.session_state.register_model_type == "Self-hosted API" and not model_config.get("api_url"):
                                st.error("API URL is required")
                            elif st.session_state.register_model_type == "Local Model" and not model_config.get("model_path"):
                                st.error("Model path is required")
                            else:
                                st.session_state.register_model_name = model_name
                                st.session_state.register_model_config = model_config
                                st.session_state.register_step = 3
                                st.rerun()
                
                # Step 3: Review and Register
                elif st.session_state.register_step == 3:
                    st.subheader("Review and Register Model")
                    
                    # Display model information for review
                    st.write("#### Model Details")
                    st.markdown(f"""
                    **Name:** {st.session_state.register_model_name}  
                    **Type:** {st.session_state.register_model_type}  
                    **Model ID:** {st.session_state.register_model_config['model_id']}
                    """)
                    
                    # Display additional details based on model type
                    if st.session_state.register_model_type == "OpenAI API":
                        if st.session_state.register_model_config.get('organization'):
                            st.markdown(f"**Organization:** {st.session_state.register_model_config['organization']}")
                    elif st.session_state.register_model_type == "Self-hosted API":
                        st.markdown(f"**API URL:** {st.session_state.register_model_config['api_url']}")
                    elif st.session_state.register_model_type == "Azure OpenAI":
                        st.markdown(f"""
                        **Endpoint:** {st.session_state.register_model_config['endpoint']}  
                        **Deployment:** {st.session_state.register_model_config['deployment_name']}
                        """)
                    elif st.session_state.register_model_type == "Local Model":
                        st.markdown(f"""
                        **Model Path:** {st.session_state.register_model_config['model_path']}  
                        **Device:** {st.session_state.register_model_config['device']}
                        """)
                    
                    # Test connection option
                    test_connection = st.checkbox("Test connection before registering", value=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("← Back", key="back_register_review"):
                            st.session_state.register_step = 2
                            st.rerun()
                    with col2:
                        register_button = st.button("Register Model", key="confirm_register")
                        if register_button:
                            # In a real implementation, this would save the model configuration
                            if test_connection:
                                # Simulate testing the connection
                                import time
                                with st.spinner("Testing connection to model..."):
                                    time.sleep(2)  # Simulate API call
                                st.success("Connection successful!")
                            
                            # Create response message about the registered model
                            response = f"Model '{st.session_state.register_model_name}' ({st.session_state.register_model_config['provider']}:{st.session_state.register_model_config['model_id']}) has been registered successfully."
                            st.session_state.messages.append({"role": "assistant", "content": response})
                            
                            # Clear the registration flow state
                            if 'register_step' in st.session_state:
                                del st.session_state.register_step
                            if 'register_model_type' in st.session_state:
                                del st.session_state.register_model_type
                            if 'register_model_name' in st.session_state:
                                del st.session_state.register_model_name
                            if 'register_model_config' in st.session_state:
                                del st.session_state.register_model_config
                            
                            # Clear the pending action
                            st.session_state.pending_action = None
                            st.success("Model registered successfully!")
                            st.rerun()

            elif st.session_state.pending_action.get("type") == "delete_model":
                # Create a step-by-step flow
                if 'delete_step' not in st.session_state:
                    st.session_state.delete_step = 1

                st.write("### Delete Model")
                st.progress(st.session_state.delete_step / 2)  # 2 total steps
                
                # Step indicators
                cols = st.columns(2)
                for i in range(2):
                    with cols[i]:
                        if i + 1 < st.session_state.delete_step:
                            st.markdown(f"<div style='text-align: center;'><span style='background-color: #50fa7b; color: black; border-radius: 50%; padding: 5px 10px;'>{i+1}</span></div>", unsafe_allow_html=True)
                        elif i + 1 == st.session_state.delete_step:
                            st.markdown(f"<div style='text-align: center;'><span style='background-color: #4e54c8; color: white; border-radius: 50%; padding: 5px 10px;'>{i+1}</span></div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div style='text-align: center;'><span style='background-color: #2a2a3c; color: white; border-radius: 50%; padding: 5px 10px;'>{i+1}</span></div>", unsafe_allow_html=True)
                
                # Step 1: Select Model to Delete
                if st.session_state.delete_step == 1:
                    st.subheader("Select Model to Delete")
                    
                    # In a real implementation, this would load actual models from storage
                    # For now, we'll use dummy data
                    registered_models = [
                        {"name": "GPT-4 Turbo", "id": "openai:gpt-4-turbo", "provider": "openai"},
                        {"name": "Gemini Pro", "id": "gemini:gemini-pro", "provider": "gemini"},
                        {"name": "Claude 3 Opus", "id": "anthropic:claude-3-opus", "provider": "anthropic"},
                        {"name": "Llama 3", "id": "local:llama-3-70b", "provider": "local"}
                    ]
                    
                    # Group models by provider
                    providers = set(model["provider"] for model in registered_models)
                    
                    selected_provider = st.selectbox(
                        "Filter by provider:",
                        ["All Providers"] + list(providers),
                        key="delete_provider_filter"
                    )
                    
                    # Filter models by provider
                    filtered_models = registered_models
                    if selected_provider != "All Providers":
                        filtered_models = [m for m in registered_models if m["provider"] == selected_provider]
                    
                    if not filtered_models:
                        st.warning(f"No models found for provider: {selected_provider}")
                        selected_model = None
                    else:
                        # Create selection options with formatted display names
                        model_options = {
                            i: f"{m['name']} ({m['id']})" 
                            for i, m in enumerate(filtered_models)
                        }
                        
                        selection_index = st.selectbox(
                            "Select a model to delete:",
                            list(model_options.keys()),
                            format_func=lambda x: model_options[x],
                            key="delete_model_selection"
                        )
                        
                        selected_model = filtered_models[selection_index] if selection_index is not None else None
                        
                        if selected_model:
                            st.markdown(f"""
                            ### Selected Model Details:
                            **Name:** {selected_model['name']}  
                            **ID:** {selected_model['id']}  
                            **Provider:** {selected_model['provider']}
                            """)
                    
                    col1, col2 = st.columns(2)
                    with col2:
                        next_button = st.button("Next →", key="next_delete_selection")
                        if next_button:
                            if not selected_model:
                                st.error("Please select a model to delete")
                            else:
                                st.session_state.delete_selected_model = selected_model
                                st.session_state.delete_step = 2
                                st.rerun()
                
                # Step 2: Confirm Deletion
                elif st.session_state.delete_step == 2:
                    st.subheader("Confirm Deletion")
                    
                    selected_model = st.session_state.delete_selected_model
                    
                    st.warning(f"⚠️ You are about to delete the following model:")
                    st.markdown(f"""
                    ### {selected_model['name']}
                    **ID:** {selected_model['id']}  
                    **Provider:** {selected_model['provider']}
                    """)
                    
                    st.error("⚠️ This action cannot be undone. All configurations and settings for this model will be permanently removed.")
                    
                    # Require explicit confirmation
                    confirmation = st.text_input(
                        "Type the model name to confirm deletion:",
                        key="delete_confirmation_text"
                    )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("← Back", key="back_delete_confirm"):
                            st.session_state.delete_step = 1
                            st.rerun()
                    with col2:
                        delete_button = st.button("Delete Model", key="confirm_delete", disabled=(confirmation != selected_model['name']))
                        if delete_button:
                            if confirmation != selected_model['name']:
                                st.error(f"Confirmation text doesn't match model name '{selected_model['name']}'")
                            else:
                                # In a real implementation, this would delete the model from storage
                                
                                # Create response message about the deleted model
                                response = f"Model '{selected_model['name']}' ({selected_model['id']}) has been deleted successfully."
                                st.session_state.messages.append({"role": "assistant", "content": response})
                                
                                # Clear the deletion flow state
                                if 'delete_step' in st.session_state:
                                    del st.session_state.delete_step
                                if 'delete_selected_model' in st.session_state:
                                    del st.session_state.delete_selected_model
                                
                                # Clear the pending action
                                st.session_state.pending_action = None
                                st.success("Model deleted successfully!")
                                st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)
            
            # Close the split container
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Standard display when no pending action
            if not st.session_state.messages:
                # Show welcome message if no messages
                st.markdown("""
                <div class="stCard">
                    <h3>👋 Welcome to Dravik Agent</h3>
                    <p>I'm an agent for the Dravik CLI. Here's what I can help you with:</p>
                    <ol>
                        <li><strong>Red Teaming</strong> - Run static or conversation-based red teaming benchmarks</li>
                        <li><strong>View Results</strong> - View and analyze benchmark results</li>
                        <li><strong>Custom Models</strong> - Register, list, or delete custom models</li>
                        <li><strong>Scheduled Benchmarks</strong> - Configure, list, or delete scheduled benchmarks</li>
                    </ol>
                    <p>Just tell me what you'd like to do, and I'll guide you through the process!</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Display existing messages
                for i, message in enumerate(st.session_state.messages):
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
            
            # User input
            prompt = st.chat_input("Enter your request...")
            if prompt:
                # Add user message to chat history
                user_msg = {"role": "user", "content": prompt}
                st.session_state.messages.append(user_msg)
                
                # Process the message with the agent
                try:
                    # Process the message with the agent
                    response = st.session_state.agent.handle_message(prompt)
                    
                    if response and "content" in response:
                        # Add assistant message to chat history
                        assistant_msg = {"role": "assistant", "content": response["content"]}
                        st.session_state.messages.append(assistant_msg)
                        
                        # Handle specific response types with better parameter extraction
                        if "type" in response and response["type"] not in ["text", "help"]:
                            if response["type"] == "red_teaming_static":
                                # Extract parameters from the response if they're provided
                                params = response.get("parameters", {})
                                # Set defaults for required parameters
                                if "models" not in params and "model" in params:
                                    params["models"] = [params["model"]]
                                
                                st.session_state.pending_action = {
                                    "type": "red_teaming_static",
                                    "params": params,
                                    # Set defaults for missing parameters
                                    "models": params.get("models", []),
                                    "dataset_source": params.get("dataset_source", "Internal datasets"),
                                    "dataset_type": params.get("dataset_type", "Static Templates"),
                                    "num_prompts": params.get("num_prompts", 20),
                                    "generation_method": params.get("generation_method", "jailbreak"),
                                    "skip_wizard": params.get("skip_wizard", False)
                                }
                            elif response["type"] == "red_teaming_conversation":
                                # Check if we should skip the wizard based on NLP extraction
                                if st.session_state.pending_action.get("skip_wizard", False):
                                    # Get parameters from pending_action
                                    models = st.session_state.pending_action.get("models", [])
                                    attack_vectors = st.session_state.pending_action.get("attack_vectors", ["jailbreak"])
                                    num_attempts = st.session_state.pending_action.get("num_attempts", 3)
                                    
                                    # Display summary
                                    st.write("### Running Conversation Red Teaming Benchmark")
                                    st.write("Starting conversation benchmark with the following parameters:")
                                    
                                    st.markdown(f"""
                                    **Models:** {', '.join(models)}  
                                    **Attack Vectors:** {', '.join(attack_vectors)}  
                                    **Attempts per Model:** {num_attempts}
                                    """)
                                    
                                    # Show progress indicator
                                    progress_bar = st.progress(0)
                                    for i in range(100):
                                        # Simulating progress
                                        progress_bar.progress(i + 1)
                                        time.sleep(0.02)
                                    
                                    # Get the response message from pending_action
                                    response = st.session_state.pending_action.get("content", 
                                        f"Started conversation red teaming benchmark with {len(models)} models using {', '.join(attack_vectors)} attack vectors.")
                                    
                                    # Add to chat history
                                    st.session_state.messages.append({"role": "assistant", "content": response})
                                    
                                    # Clear the pending action
                                    st.session_state.pending_action = None
                                    st.success("Conversation benchmark started successfully!")
                                    st.rerun()
                                else:
                                    # Create a step-by-step flow
                                    if 'conversation_step' not in st.session_state:
                                        st.session_state.conversation_step = 1

                                    st.write("### Configure Conversation Red Teaming")
                                    st.progress(st.session_state.conversation_step / 3)  # 3 total steps
                                    
                                    # Step indicators
                                    cols = st.columns(3)
                                    for i in range(3):
                                        with cols[i]:
                                            if i + 1 < st.session_state.conversation_step:
                                                st.markdown(f"<div style='text-align: center;'><span style='background-color: #50fa7b; color: black; border-radius: 50%; padding: 5px 10px;'>{i+1}</span></div>", unsafe_allow_html=True)
                                            elif i + 1 == st.session_state.conversation_step:
                                                st.markdown(f"<div style='text-align: center;'><span style='background-color: #4e54c8; color: white; border-radius: 50%; padding: 5px 10px;'>{i+1}</span></div>", unsafe_allow_html=True)
                                            else:
                                                st.markdown(f"<div style='text-align: center;'><span style='background-color: #2a2a3c; color: white; border-radius: 50%; padding: 5px 10px;'>{i+1}</span></div>", unsafe_allow_html=True)
                                    
                                    # Step 1: Model Selection
                                    if st.session_state.conversation_step == 1:
                                        st.subheader("Select Models for Conversation Testing")
                                        
                                        # Provider selection
                                        provider_options = ["OpenAI", "Gemini", "Custom", "All"]
                                        providers = st.multiselect(
                                            "Select model providers:",
                                            provider_options,
                                            key="conv_providers"
                                        )
                                        
                                        # Initialize selected models list
                                        all_selected_models = []
                                        
                                        # Show models for each selected provider
                                        if "OpenAI" in providers:
                                            openai_models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
                                            openai_selected = st.multiselect(
                                                "Select OpenAI models:",
                                                openai_models,
                                                key="conv_openai_models"
                                            )
                                            all_selected_models.extend([f"openai:{model}" for model in openai_selected])
                                        
                                        if "Gemini" in providers:
                                            gemini_models = ["gemini-pro", "gemini-1.5-pro", "gemini-1.5-flash"]
                                            gemini_selected = st.multiselect(
                                                "Select Gemini models:",
                                                gemini_models,
                                                key="conv_gemini_models"
                                            )
                                            all_selected_models.extend([f"gemini:{model}" for model in gemini_selected])
                                        
                                        if "Custom" in providers:
                                            custom_models = ["custom-model-1", "custom-model-2"]
                                            custom_selected = st.multiselect(
                                                "Select custom models:",
                                                custom_models,
                                                key="conv_custom_models"
                                            )
                                            all_selected_models.extend([f"custom:{model}" for model in custom_selected])
                                        
                                        # Manual model entry
                                        st.write("Or enter models manually:")
                                        manual_models_input = st.text_area(
                                            "Enter models manually (one per line):",
                                            key="conv_manual_models",
                                            help="Format: provider:model_name (e.g., openai:gpt-4)"
                                        )
                                        
                                        # Process manual input
                                        manual_models = []
                                        if manual_models_input:
                                            for line in manual_models_input.split('\n'):
                                                if line.strip():
                                                    # Add provider prefix if not present
                                                    if ":" not in line.strip():
                                                        if line.startswith("gpt"):
                                                            model = f"openai:{line.strip()}"
                                                        elif line.startswith("gemini"):
                                                            model = f"gemini:{line.strip()}"
                                                        else:
                                                            model = f"custom:{line.strip()}"
                                                    else:
                                                        model = line.strip()
                                                    
                                                    manual_models.append(model)
                                        
                                        # Combine all models
                                        final_models = all_selected_models + [m for m in manual_models if m not in all_selected_models]
                                        
                                        col1, col2 = st.columns(2)
                                        with col2:
                                            if st.button("Next →", key="next_conv_models"):
                                                if not final_models:
                                                    st.error("Please select at least one model")
                                                else:
                                                    # Store selection and advance to next step
                                                    st.session_state.conv_selected_models = final_models
                                                    st.session_state.conversation_step = 2
                                                    st.rerun()
                                    
                                    # Step 2: Attack Vector Configuration
                                    elif st.session_state.conversation_step == 2:
                                        st.subheader("Configure Attack Vectors")
                                        
                                        # Attack vector selection
                                        attack_vectors = st.multiselect(
                                            "Select attack vectors to test:",
                                            ["jailbreak", "harmful_content", "personal_information", "illegal_activity", "hate_speech"],
                                            default=["jailbreak"],
                                            key="conv_attack_vectors"
                                        )
                                        
                                        # Number of attempts setting
                                        num_attempts = st.slider(
                                            "Number of conversation attempts per model:",
                                            min_value=1,
                                            max_value=10,
                                            value=3,
                                            step=1,
                                            key="conv_num_attempts"
                                        )
                                        
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            if st.button("← Back", key="back_conv_attack"):
                                                st.session_state.conversation_step = 1
                                                st.rerun()
                                        with col2:
                                            if st.button("Next →", key="next_conv_attack"):
                                                if not attack_vectors:
                                                    st.error("Please select at least one attack vector")
                                                else:
                                                    # Store selection and advance to next step
                                                    st.session_state.conv_attack_vectors = attack_vectors
                                                    st.session_state.conv_num_attempts = num_attempts
                                                    st.session_state.conversation_step = 3
                                                    st.rerun()
                                    
                                    # Step 3: Review and Submit
                                    elif st.session_state.conversation_step == 3:
                                        st.subheader("Review and Start Benchmark")
                                        
                                        # Show review information
                                        st.write("#### Configuration Summary")
                                        st.markdown(f"""
                                        **Selected Models:** {", ".join(st.session_state.conv_selected_models)}  
                                        **Attack Vectors:** {", ".join(st.session_state.conv_attack_vectors)}  
                                        **Attempts per Model:** {st.session_state.conv_num_attempts}
                                        """)
                                        
                                        # Show help info
                                        st.info("The conversation red teaming will attempt to elicit harmful or inappropriate responses through multi-turn conversations. Each selected attack vector will be tried with different approaches.")
                                        
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            if st.button("← Back", key="back_conv_review"):
                                                st.session_state.conversation_step = 2
                                                st.rerun()
                                        with col2:
                                            if st.button("Start Benchmark", key="start_conv_test"):
                                                # Create response message
                                                response = f"Starting conversation red teaming benchmark with:\n\n" \
                                                          f"- Models: {', '.join(st.session_state.conv_selected_models)}\n" \
                                                          f"- Attack vectors: {', '.join(st.session_state.conv_attack_vectors)}\n" \
                                                          f"- Attempts per model: {st.session_state.conv_num_attempts}"
                                                
                                                st.session_state.messages.append({"role": "assistant", "content": response})
                                                
                                                # Clear the conversation flow state
                                                if 'conversation_step' in st.session_state:
                                                    del st.session_state.conversation_step
                                                if 'conv_selected_models' in st.session_state:
                                                    del st.session_state.conv_selected_models
                                                if 'conv_attack_vectors' in st.session_state:
                                                    del st.session_state.conv_attack_vectors
                                                if 'conv_num_attempts' in st.session_state:
                                                    del st.session_state.conv_num_attempts
                                                
                                                # Clear the pending action
                                                st.session_state.pending_action = None
                                                st.success("Conversation benchmark started successfully!")
                                                st.rerun()
                    
                    st.rerun()
                except Exception as e:
                    # Handle any errors
                    error_msg = f"Error processing your request: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": f"⚠️ {error_msg}"})
                    st.rerun()

    with tab2:
        if st.session_state.get("advanced_mode", False) and st.session_state.task_steps:
            # Task progress with modern styling