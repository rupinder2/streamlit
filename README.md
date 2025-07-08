# Secure Token Storage Application

A Streamlit application with secure PostgreSQL-based token storage using encryption and a REST API for external access.

## Features

- 🔐 **Secure Token Storage**: Tokens are encrypted before storing in PostgreSQL
- 👤 **User Authentication**: Database-based user management
- 🔄 **Auto-Generate Tokens**: Automatic secure token generation
- ✏️ **Manual Token Entry**: Support for existing tokens
- 🛡️ **Encryption**: Fernet encryption for all sensitive data
- 📊 **Dashboard**: Token management and user information
- 🌐 **REST API**: Secure API for external applications to access tokens
- 🔑 **JWT Authentication**: Secure API authentication with JWT tokens

## Security Features

- **Encryption at Rest**: All tokens are encrypted using Fernet encryption
- **Password Hashing**: User passwords are hashed using SHA-256
- **Database Security**: PostgreSQL with proper connection handling
- **Environment Variables**: Sensitive configuration stored in .env files
- **JWT Authentication**: Secure API access with time-limited tokens
- **Access Control**: Users can only access their own tokens

## Prerequisites

- Python 3.7+
- PostgreSQL database
- pip (Python package manager)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd streamlit
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL**
   - Install PostgreSQL on your system
   - Create a new database for the application
   - Note down the database credentials

4. **Configure environment variables**
   ```bash
   cp env_example.txt .env
   ```
   
   Edit `.env` file with your database credentials:
   ```env
   # Database Configuration
   DB_HOST=localhost
   DB_NAME=token_storage
   DB_USER=postgres
   DB_PASSWORD=your_password_here
   DB_PORT=5432
   
   # Encryption Key (will be auto-generated on first run)
   ENCRYPTION_KEY=your_encryption_key_here
   
   # JWT Secret for API Authentication (generate this securely)
   JWT_SECRET=your_jwt_secret_key_here
   ```

5. **Initialize the database**
   ```bash
   python setup_database.py
   ```

6. **Run the application**
   ```bash
   streamlit run app.py
   ```

7. **Start the API server** (optional, for external access)
   ```bash
   python api_server.py
   ```

## API Usage for External Applications

### Starting the API Server

The API server provides secure access to tokens for external applications:

```bash
python api_server.py
```

The API will be available at `http://localhost:8000`

### Using the Python Client

Other applications can use the provided Python client to access tokens:

```python
from token_client import SecureTokenClient

# Initialize client
client = SecureTokenClient("http://localhost:8000")

# Login
if client.login("testuser", "testpass123"):
    # Get token for your application
    token_data = client.get_token(
        user_id="testuser",
        application_name="my-app",
        purpose="API integration"
    )
    
    if token_data:
        token = token_data["token"]
        print(f"Token: {token}")
```

### Direct API Calls

You can also make direct HTTP calls to the API:

1. **Login to get JWT token:**
   ```bash
   curl -X POST "http://localhost:8000/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"username": "testuser", "password": "testpass123"}'
   ```

2. **Access token using JWT:**
   ```bash
   curl -X POST "http://localhost:8000/tokens/access" \
        -H "Authorization: Bearer YOUR_JWT_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"user_id": "testuser", "application_name": "my-app", "purpose": "API integration"}'
   ```

### API Endpoints

- `POST /auth/login` - Authenticate and get JWT token
- `POST /tokens/access` - Access a user's token
- `GET /tokens/status/{user_id}` - Check token status
- `DELETE /tokens/{user_id}` - Delete user's token
- `GET /health` - Health check

### Example Usage

See `example_usage.py` for complete examples of how to integrate with:
- GitHub API
- Custom APIs
- Token management
- Error handling

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Tokens Table
```sql
CREATE TABLE tokens (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    encrypted_token TEXT NOT NULL,
    generation_method VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Usage

1. **Start the application**: `streamlit run app.py`
2. **Login**: Use the test credentials created during setup
   - Username: `testuser`
   - Password: `testpass123`
3. **Choose token method**: Auto-generate or manual entry
4. **Complete setup**: View your dashboard
5. **Start API server**: `python api_server.py` (for external access)
6. **Use tokens in other apps**: Use the client library or direct API calls

## Security Considerations

### Encryption Key Management
- The encryption key is stored in the `.env` file
- Never commit the `.env` file to version control
- Use a strong, randomly generated key in production
- Consider using a key management service for production

### JWT Security
- Use a strong JWT secret in production
- JWT tokens expire after 24 hours by default
- Store JWT secrets securely
- Consider shorter expiration times for sensitive applications

### Database Security
- Use strong database passwords
- Restrict database access to application servers only
- Enable SSL connections for database communication
- Regular database backups with encryption

### API Security
- Use HTTPS in production
- Implement rate limiting
- Monitor API access logs
- Consider API key authentication for additional security

### Application Security
- Use HTTPS in production
- Implement proper session management
- Add rate limiting for login attempts
- Consider adding two-factor authentication

## Development

### Project Structure
```
├── app.py                 # Main Streamlit application
├── api_server.py          # FastAPI server for external access
├── token_client.py        # Python client library
├── example_usage.py       # Usage examples
├── database.py            # Database and encryption logic
├── setup_database.py      # Database initialization script
├── requirements.txt       # Python dependencies
├── env_example.txt        # Environment variables template
└── README.md             # This file
```

### Adding New Features
1. Update the database schema if needed
2. Add new methods to `SecureTokenStorage` class
3. Update the Streamlit interface in `app.py`
4. Add corresponding API endpoints in `api_server.py`
5. Update the client library in `token_client.py`
6. Test thoroughly with the database

## Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure database exists and is accessible
- Check firewall settings

### API Server Issues
- Verify the API server is running on port 8000
- Check JWT_SECRET is set in `.env`
- Ensure proper network connectivity
- Check API server logs for errors

### Encryption Issues
- Verify `ENCRYPTION_KEY` is set in `.env`
- Ensure the key is properly formatted
- Check for key corruption or changes

### Application Errors
- Check Streamlit logs for error messages
- Verify all dependencies are installed
- Ensure proper file permissions

## Production Deployment

1. **Use a production database**
   - Set up PostgreSQL with proper security
   - Use connection pooling
   - Enable SSL connections

2. **Secure the environment**
   - Use strong encryption keys
   - Secure environment variables
   - Enable HTTPS for both Streamlit and API

3. **API deployment**
   - Use a production WSGI server (Gunicorn)
   - Set up reverse proxy (Nginx)
   - Enable SSL/TLS
   - Configure proper CORS settings

4. **Monitoring and logging**
   - Set up application monitoring
   - Configure database logging
   - Monitor for security events
   - Log API access for audit trails

5. **Backup strategy**
   - Regular database backups
   - Encrypted backup storage
   - Test restore procedures

## License

This project is licensed under the MIT License - see the LICENSE file for details. 