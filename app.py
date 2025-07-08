import streamlit as st
import json
import os
from datetime import datetime
import secrets
import string

# Page configuration
st.set_page_config(
    page_title="Onboarding Flow",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        color: #1f77b4;
    }
    .option-card {
        background-color: #f0f2f6;
        padding: 2rem;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        margin: 1rem 0;
        text-align: center;
    }
    .success-message {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
        color: #155724;
    }
    .info-message {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
        color: #0c5460;
    }
    .back-button {
        position: fixed;
        top: 20px;
        left: 20px;
        z-index: 1000;
    }
    .stButton > button {
        background-color: #ffffff;
        color: #262730;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #f8f9fa;
        border-color: #262730;
    }
    .stTextInput > div > div > input {
        border-radius: 6px;
        border: 1px solid #e0e0e0;
    }
    .stTextInput > div > div > input:focus {
        border-color: #262730;
        box-shadow: 0 0 0 2px rgba(38, 39, 48, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_step' not in st.session_state:
    st.session_state.current_step = 'welcome'
if 'token_option' not in st.session_state:
    st.session_state.token_option = None
if 'user_authenticated' not in st.session_state:
    st.session_state.user_authenticated = False
if 'pat_token' not in st.session_state:
    st.session_state.pat_token = None

def go_back():
    """Navigate to the previous step"""
    if st.session_state.current_step == 'login':
        st.session_state.current_step = 'welcome'
        st.session_state.token_option = None
    elif st.session_state.current_step == 'token_setup':
        st.session_state.current_step = 'login'
        st.session_state.user_authenticated = False
        st.session_state.user_id = None
    elif st.session_state.current_step == 'dashboard':
        st.session_state.current_step = 'token_setup'
    st.rerun()

def generate_pat_token():
    """Generate a random PAT token"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(32))

def save_token_to_file(token, option):
    """Save token to a JSON file"""
    token_data = {
        'token': token,
        'generation_method': option,
        'created_at': datetime.now().isoformat(),
        'user_id': st.session_state.get('user_id', 'unknown')
    }
    
    os.makedirs('data', exist_ok=True)
    with open('data/token_data.json', 'w') as f:
        json.dump(token_data, f, indent=2)

def load_token_from_file():
    """Load token from JSON file"""
    try:
        with open('data/token_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def welcome_page():
    """First page - Welcome and token option selection"""
    st.markdown('<h1 class="main-header">Welcome to Your Application</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem;">
        <p style="font-size: 1.2rem; color: #666;">
            Let's get you started! First, we need to set up your Personal Access Token (PAT).
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="option-card" onclick="document.querySelector('#auto-generate').click()">
            <h3>🔄 Auto-Generate Token</h3>
            <p>We'll automatically generate a secure PAT token for you.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Auto-Generate Token", key="auto-generate", use_container_width=True):
            st.session_state.token_option = 'auto'
            st.session_state.current_step = 'login'
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="option-card" onclick="document.querySelector('#manual-enter').click()">
            <h3>✏️ Manual Entry</h3>
            <p>You can enter your existing PAT token manually.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Manual Entry", key="manual-enter", use_container_width=True):
            st.session_state.token_option = 'manual'
            st.session_state.current_step = 'login'
            st.rerun()

def login_page():
    """Login page"""
    # Back button
    if st.button("← Back", key="back_to_welcome"):
        go_back()
    
    st.markdown('<h1 class="main-header">Login Required</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-message">
        <strong>Authentication Required:</strong> Please log in to continue with the onboarding process.
    </div>
    """, unsafe_allow_html=True)
    
    # Simple login form (in a real app, you'd integrate with your auth system)
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if username and password:  # Simple validation
                st.session_state.user_authenticated = True
                st.session_state.user_id = username
                st.session_state.current_step = 'token_setup'
                st.rerun()
            else:
                st.error("Please enter both username and password.")

def token_setup_page():
    """Token setup page based on user's choice"""
    # Back button
    if st.button("← Back", key="back_to_login"):
        go_back()
    
    st.markdown('<h1 class="main-header">Token Setup</h1>', unsafe_allow_html=True)
    
    if st.session_state.token_option == 'auto':
        # Auto-generate token
        if st.session_state.pat_token is None:
            st.session_state.pat_token = generate_pat_token()
            save_token_to_file(st.session_state.pat_token, 'auto')
        
        st.markdown("""
        <div class="success-message">
            <h3>✅ Token Generated Successfully!</h3>
            <p>Your Personal Access Token has been automatically generated and saved.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.info(f"**Generated Token:** `{st.session_state.pat_token}`")
        st.warning("⚠️ Please save this token securely. It won't be displayed again.")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("Continue to Dashboard", use_container_width=True):
                st.session_state.current_step = 'dashboard'
                st.rerun()
    
    elif st.session_state.token_option == 'manual':
        # Manual token entry
        st.markdown("""
        <div class="info-message">
            <strong>Manual Token Entry:</strong> Please enter your Personal Access Token below.
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("token_form"):
            token_input = st.text_input("Personal Access Token", type="password", 
                                      help="Enter your existing PAT token")
            save_button = st.form_submit_button("Save Token")
            
            if save_button:
                if token_input:
                    st.session_state.pat_token = token_input
                    save_token_to_file(token_input, 'manual')
                    st.success("✅ Token saved successfully!")
                    
                    if st.button("Continue to Dashboard", use_container_width=True):
                        st.session_state.current_step = 'dashboard'
                        st.rerun()
                else:
                    st.error("Please enter a valid token.")

def dashboard_page():
    """Final dashboard page"""
    # Back button
    if st.button("← Back", key="back_to_token_setup"):
        go_back()
    
    st.markdown('<h1 class="main-header">🎉 Welcome to Your Dashboard!</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="success-message">
        <h3>Onboarding Complete!</h3>
        <p>You have successfully completed the onboarding process.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display user info
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("User Information")
        st.write(f"**Username:** {st.session_state.get('user_id', 'Unknown')}")
        st.write(f"**Token Method:** {st.session_state.token_option.title()}")
        
        # Load and display token info
        token_data = load_token_from_file()
        if token_data:
            st.write(f"**Token Created:** {token_data['created_at'][:19]}")
    
    with col2:
        st.subheader("Quick Actions")
        if st.button("View Token Info", use_container_width=True):
            token_data = load_token_from_file()
            if token_data:
                st.json(token_data)
        
        if st.button("Reset Onboarding", use_container_width=True):
            # Clear session state and restart
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

def main():
    """Main application logic"""
    # Navigation based on current step
    if st.session_state.current_step == 'welcome':
        welcome_page()
    elif st.session_state.current_step == 'login':
        login_page()
    elif st.session_state.current_step == 'token_setup':
        token_setup_page()
    elif st.session_state.current_step == 'dashboard':
        dashboard_page()

if __name__ == "__main__":
    main()