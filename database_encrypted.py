#!/usr/bin/env python3
"""
Enhanced Secure Token Storage with PostgreSQL Encryption
Provides additional database-level encryption on top of application encryption
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from cryptography.fernet import Fernet
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EnhancedSecureTokenStorage:
    def __init__(self, use_postgres_encryption=True):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'token_storage'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', ''),
            'port': os.getenv('DB_PORT', '5432')
        }
        
        # Initialize encryption keys
        self.encryption_key = os.getenv('ENCRYPTION_KEY')
        if not self.encryption_key:
            self.encryption_key = Fernet.generate_key().decode()
            print(f"Generated new encryption key: {self.encryption_key}")
            print("Please add this to your .env file as ENCRYPTION_KEY")
        
        self.cipher = Fernet(self.encryption_key.encode())
        
        # PostgreSQL encryption settings
        self.use_postgres_encryption = use_postgres_encryption
        self.postgres_key = os.getenv('POSTGRES_ENCRYPTION_KEY', 'default-postgres-key')
        
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
        """Initialize database tables with encryption"""
        conn = self.get_connection()
        if not conn:
            return
        
        try:
            with conn.cursor() as cursor:
                # Enable pgcrypto extension for PostgreSQL encryption
                if self.use_postgres_encryption:
                    cursor.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
                
                # Create users table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(255) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create tokens table with optional PostgreSQL encryption
                if self.use_postgres_encryption:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS tokens (
                            id SERIAL PRIMARY KEY,
                            user_id VARCHAR(255) NOT NULL,
                            encrypted_token TEXT NOT NULL,
                            encrypted_token_pgp BYTEA,
                            generation_method VARCHAR(50) NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                else:
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
                
                # Create indexes
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_tokens_user_id ON tokens(user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_tokens_created_at ON tokens(created_at)")
                
                conn.commit()
                print("Database tables initialized successfully")
                if self.use_postgres_encryption:
                    print("PostgreSQL encryption enabled")
                
        except psycopg2.Error as e:
            print(f"Database initialization error: {e}")
        finally:
            conn.close()
    
    def encrypt_token(self, token):
        """Encrypt token with Fernet (application level)"""
        return self.cipher.encrypt(token.encode()).decode()
    
    def decrypt_token(self, encrypted_token):
        """Decrypt token with Fernet (application level)"""
        try:
            return self.cipher.decrypt(encrypted_token.encode()).decode()
        except Exception as e:
            print(f"Token decryption error: {e}")
            return None
    
    def encrypt_for_postgres(self, data):
        """Encrypt data for PostgreSQL storage"""
        if not self.use_postgres_encryption:
            return data
        
        try:
            # Use pgcrypto to encrypt the already-encrypted data
            conn = self.get_connection()
            if conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT pgp_sym_encrypt(%s, %s)",
                        (data, self.postgres_key)
                    )
                    result = cursor.fetchone()
                    conn.close()
                    return result[0] if result else data
        except Exception as e:
            print(f"PostgreSQL encryption error: {e}")
            return data
    
    def decrypt_from_postgres(self, encrypted_data):
        """Decrypt data from PostgreSQL storage"""
        if not self.use_postgres_encryption or not encrypted_data:
            return encrypted_data
        
        try:
            conn = self.get_connection()
            if conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT pgp_sym_decrypt(%s, %s)",
                        (encrypted_data, self.postgres_key)
                    )
                    result = cursor.fetchone()
                    conn.close()
                    return result[0].decode() if result else encrypted_data
        except Exception as e:
            print(f"PostgreSQL decryption error: {e}")
            return encrypted_data
    
    def save_token(self, user_id, token, generation_method):
        """Save encrypted token to database with optional PostgreSQL encryption"""
        conn = self.get_connection()
        if not conn:
            return False
        
        try:
            # First level: Fernet encryption
            fernet_encrypted = self.encrypt_token(token)
            
            # Second level: PostgreSQL encryption (optional)
            if self.use_postgres_encryption:
                pg_encrypted = self.encrypt_for_postgres(fernet_encrypted)
                
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
                            SET encrypted_token = %s, encrypted_token_pgp = %s, 
                                generation_method = %s, updated_at = CURRENT_TIMESTAMP
                            WHERE user_id = %s
                        """, (fernet_encrypted, pg_encrypted, generation_method, user_id))
                    else:
                        # Insert new token
                        cursor.execute("""
                            INSERT INTO tokens (user_id, encrypted_token, encrypted_token_pgp, generation_method)
                            VALUES (%s, %s, %s, %s)
                        """, (user_id, fernet_encrypted, pg_encrypted, generation_method))
            else:
                # Only Fernet encryption
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT id FROM tokens WHERE user_id = %s",
                        (user_id,)
                    )
                    
                    if cursor.fetchone():
                        cursor.execute("""
                            UPDATE tokens 
                            SET encrypted_token = %s, generation_method = %s, updated_at = CURRENT_TIMESTAMP
                            WHERE user_id = %s
                        """, (fernet_encrypted, generation_method, user_id))
                    else:
                        cursor.execute("""
                            INSERT INTO tokens (user_id, encrypted_token, generation_method)
                            VALUES (%s, %s, %s)
                        """, (user_id, fernet_encrypted, generation_method))
            
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
                if self.use_postgres_encryption:
                    cursor.execute("""
                        SELECT encrypted_token, encrypted_token_pgp, generation_method, created_at, updated_at
                        FROM tokens WHERE user_id = %s
                    """, (user_id,))
                else:
                    cursor.execute("""
                        SELECT encrypted_token, generation_method, created_at, updated_at
                        FROM tokens WHERE user_id = %s
                    """, (user_id,))
                
                result = cursor.fetchone()
                if result:
                    # Decrypt in reverse order
                    if self.use_postgres_encryption and result.get('encrypted_token_pgp'):
                        # First: Decrypt PostgreSQL encryption
                        fernet_encrypted = self.decrypt_from_postgres(result['encrypted_token_pgp'])
                    else:
                        fernet_encrypted = result['encrypted_token']
                    
                    # Second: Decrypt Fernet encryption
                    decrypted_token = self.decrypt_token(fernet_encrypted)
                    
                    if decrypted_token:
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
    
    def get_encryption_status(self):
        """Get encryption status information"""
        return {
            'application_encryption': True,
            'postgres_encryption': self.use_postgres_encryption,
            'encryption_layers': 2 if self.use_postgres_encryption else 1,
            'fernet_key_configured': bool(self.encryption_key),
            'postgres_key_configured': bool(self.postgres_key)
        }

# Backward compatibility
SecureTokenStorage = EnhancedSecureTokenStorage 