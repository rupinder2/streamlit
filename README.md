# Streamlit Onboarding Webflow

A beautiful and modern onboarding flow built with Streamlit that guides users through the process of setting up their Personal Access Token (PAT).

## Features

- **Welcome Page**: Users can choose between auto-generating a PAT token or manually entering one
- **Login Page**: Simple authentication before proceeding to token setup
- **Token Setup**: 
  - Auto-generation: Automatically creates and saves a secure PAT token
  - Manual entry: Allows users to input their existing PAT token
- **Dashboard**: Final page showing completion status and user information
- **Modern UI**: Clean, responsive design with custom styling
- **Data Persistence**: Tokens are saved to JSON files for future reference

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
streamlit run app.py
```

## Usage Flow

1. **Welcome Page**: Choose between "Auto-Generate Token" or "Manual Entry"
2. **Login Page**: Enter username and password (any non-empty values work for demo)
3. **Token Setup**:
   - If auto-generate: Token is created and displayed
   - If manual entry: Enter your existing PAT token
4. **Dashboard**: View completion status and user information

## File Structure

```
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── data/              # Created automatically to store token data
    └── token_data.json # Token information and metadata
```

## Customization

- **Authentication**: Replace the simple login form with your actual authentication system
- **Token Generation**: Modify the `generate_pat_token()` function to integrate with your token service
- **Styling**: Update the CSS in the `st.markdown()` section to match your brand colors
- **Data Storage**: Replace the JSON file storage with your preferred database solution

## Security Notes

- This is a demo application with basic security
- In production, implement proper authentication and authorization
- Store tokens securely using environment variables or secure vaults
- Add proper input validation and sanitization
- Use HTTPS in production environments

## Demo Credentials

For testing purposes, you can use any non-empty username and password combination. 