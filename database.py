import os
import psycopg2
from psycopg2.extras import RealDictCursor
from cryptography.fernet import Fernet
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SecureTokenStorage:
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'token_storage'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', ''),
            'port': os.getenv('DB_PORT', '5432')
        }
        
        # Initialize encryption key
        self.encryption_key = os.getenv('ENCRYPTION_KEY')
        if not self.encryption_key:
            # Generate a new key if not provided
            self.encryption_key = Fernet.generate_key().decode()
            print(f"Generated new encryption key: {self.encryption_key}")
            print("Please add this to your .env file as ENCRYPTION_KEY")
        
        self.cipher = Fernet(self.encryption_key.encode())
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except psycopg2.Error as e:
            print(f"Database connection error: {e}")
            return None
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        if not conn:
            return
        
        try:
            with conn.cursor() as cursor:
                # Create tokens table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tokens (
                        id SERIAL PRIMARY KEY,
                        user_id VARCHAR(255) NOT NULL,
                        encrypted_token TEXT NOT NULL,
                        generation_method VARCHAR(50) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create users table for authentication
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(255) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                print("Database tables initialized successfully")
                
        except psycopg2.Error as e:
            print(f"Database initialization error: {e}")
        finally:
            conn.close()
    
    def encrypt_token(self, token):
        """Encrypt token before storage"""
        return self.cipher.encrypt(token.encode()).decode()
    
    def decrypt_token(self, encrypted_token):
        """Decrypt token for retrieval"""
        try:
            return self.cipher.decrypt(encrypted_token.encode()).decode()
        except Exception as e:
            print(f"Token decryption error: {e}")
            return None
    
    def save_token(self, user_id, token, generation_method):
        """Save encrypted token to database"""
        conn = self.get_connection()
        if not conn:
            return False
        
        try:
            encrypted_token = self.encrypt_token(token)
            
            with conn.cursor() as cursor:
                # Check if user already has a token
                cursor.execute(
                    "SELECT id FROM tokens WHERE user_id = %s",
                    (user_id,)
                )
                
                if cursor.fetchone():
                    # Update existing token
                    cursor.execute("""
                        UPDATE tokens 
                        SET encrypted_token = %s, generation_method = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = %s
                    """, (encrypted_token, generation_method, user_id))
                else:
                    # Insert new token
                    cursor.execute("""
                        INSERT INTO tokens (user_id, encrypted_token, generation_method)
                        VALUES (%s, %s, %s)
                    """, (user_id, encrypted_token, generation_method))
                
                conn.commit()
                return True
                
        except psycopg2.Error as e:
            print(f"Token save error: {e}")
            return False
        finally:
            conn.close()
    
    def get_token(self, user_id):
        """Retrieve and decrypt token for user"""
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT encrypted_token, generation_method, created_at, updated_at
                    FROM tokens WHERE user_id = %s
                """, (user_id,))
                
                result = cursor.fetchone()
                if result:
                    decrypted_token = self.decrypt_token(result['encrypted_token'])
                    return {
                        'token': decrypted_token,
                        'generation_method': result['generation_method'],
                        'created_at': result['created_at'].isoformat(),
                        'updated_at': result['updated_at'].isoformat()
                    }
                return None
                
        except psycopg2.Error as e:
            print(f"Token retrieval error: {e}")
            return None
        finally:
            conn.close()
    
    def delete_token(self, user_id):
        """Delete token for user"""
        conn = self.get_connection()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM tokens WHERE user_id = %s", (user_id,))
                conn.commit()
                return cursor.rowcount > 0
                
        except psycopg2.Error as e:
            print(f"Token deletion error: {e}")
            return False
        finally:
            conn.close()
    
    def create_user(self, username, password_hash):
        """Create a new user"""
        conn = self.get_connection()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO users (username, password_hash)
                    VALUES (%s, %s)
                """, (username, password_hash))
                conn.commit()
                return True
                
        except psycopg2.IntegrityError:
            print(f"User {username} already exists")
            return False
        except psycopg2.Error as e:
            print(f"User creation error: {e}")
            return False
        finally:
            conn.close()
    
    def verify_user(self, username, password_hash):
        """Verify user credentials"""
        conn = self.get_connection()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id FROM users 
                    WHERE username = %s AND password_hash = %s
                """, (username, password_hash))
                
                return cursor.fetchone() is not None
                
        except psycopg2.Error as e:
            print(f"User verification error: {e}")
            return False
        finally:
            conn.close() 