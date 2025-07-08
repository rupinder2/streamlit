# 🔐 Secure Token Storage System - Visual Flow

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SECURE TOKEN STORAGE SYSTEM                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   FastAPI       │    │   PostgreSQL    │
│   Web App       │    │   API Server    │    │   Database      │
│   (app.py)      │    │   (api_server)  │    │   (Encrypted)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   External      │    │   Token Client  │    │   Encryption    │
│   Applications  │    │   Library       │    │   Layer         │
│   (Users)       │    │   (token_client)│    │   (Fernet)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔄 Complete User Journey Flow

### Phase 1: Initial Setup & Token Creation
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PHASE 1: SETUP                                 │
└─────────────────────────────────────────────────────────────────────────────┘

User → Streamlit App → Login → Token Setup → Database Storage
  │         │           │         │              │
  │         ▼           ▼         ▼              ▼
  │    ┌─────────┐ ┌─────────┐ ┌─────────┐  ┌─────────────┐
  │    │Welcome  │ │Login    │ │Token    │  │PostgreSQL   │
  │    │Page     │ │Form     │ │Setup    │  │(Encrypted)  │
  │    └─────────┘ └─────────┘ └─────────┘  └─────────────┘
  │         │           │         │              │
  │         ▼           ▼         ▼              ▼
  │    ┌─────────┐ ┌─────────┐ ┌─────────┐  ┌─────────────┐
  │    │Choose   │ │Verify   │ │Generate │  │Store Token  │
  │    │Method   │ │User     │ │or Enter │  │(Encrypted)  │
  │    │(Auto/   │ │(SHA256) │ │Token    │  │             │
  │    │Manual)  │ │         │ │         │  │             │
  │    └─────────┘ └─────────┘ └─────────┘  └─────────────┘
  │
  └──→ Dashboard (Token Management)
```

### Phase 2: External Application Access
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 2: EXTERNAL ACCESS                             │
└─────────────────────────────────────────────────────────────────────────────┘

External App → Token Client → API Server → Database → Return Token
     │              │             │           │           │
     ▼              ▼             ▼           ▼           ▼
┌─────────┐   ┌─────────┐   ┌─────────┐ ┌─────────┐ ┌─────────┐
│Request  │   │Login    │   │JWT      │ │Decrypt  │ │Encrypted│
│Token    │   │(User/   │   │Auth     │ │Token    │ │Response │
│         │   │Pass)    │   │         │ │         │ │         │
└─────────┘   └─────────┘   └─────────┘ └─────────┘ └─────────┘
     │              │             │           │           │
     ▼              ▼             ▼           ▼           ▼
┌─────────┐   ┌─────────┐   ┌─────────┐ ┌─────────┐ ┌─────────┐
│Use Token│   │Get JWT  │   │Verify   │ │Access   │ │Return   │
│in API   │   │Token    │   │User     │ │Control  │ │Token    │
│Calls    │   │         │   │Access   │ │         │ │         │
└─────────┘   └─────────┘   └─────────┘ └─────────┘ └─────────┘
```

## 🔐 Security Flow Details

### Encryption Flow
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ENCRYPTION FLOW                                │
└─────────────────────────────────────────────────────────────────────────────┘

Original Token → Fernet Encryption → Encrypted Token → Database
      │                  │                    │              │
      ▼                  ▼                    ▼              ▼
┌─────────┐        ┌─────────┐        ┌─────────┐    ┌─────────┐
│Plain    │        │Encrypt  │        │Base64   │    │Store in │
│Text     │───────▶│with Key │───────▶│Encoded  │───▶│PostgreSQL│
│Token    │        │(Fernet) │        │String   │    │         │
└─────────┘        └─────────┘        └─────────┘    └─────────┘
                           │
                           ▼
                    ┌─────────┐
                    │ENCRYPTION│
                    │KEY      │
                    │(.env)   │
                    └─────────┘
```

### Authentication Flow
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AUTHENTICATION FLOW                               │
└─────────────────────────────────────────────────────────────────────────────┘

User Login → Password Hash → Database Check → JWT Token → API Access
     │            │              │              │           │
     ▼            ▼              ▼              ▼           ▼
┌─────────┐ ┌─────────┐   ┌─────────┐   ┌─────────┐ ┌─────────┐
│Username │ │SHA256   │   │Compare  │   │Generate │ │Bearer   │
│Password │ │Hash     │   │with DB  │   │JWT      │ │Token    │
└─────────┘ └─────────┘   └─────────┘   └─────────┘ └─────────┘
     │            │              │              │           │
     ▼            ▼              ▼              ▼           ▼
┌─────────┐ ┌─────────┐   ┌─────────┐   ┌─────────┐ ┌─────────┐
│Form     │ │Hash     │   │User     │   │24hr     │ │API      │
│Input    │ │Function │   │Verified │   │Expiry   │ │Requests │
└─────────┘ └─────────┘   └─────────┘   └─────────┘ └─────────┘
```

## 🌐 API Endpoints Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API ENDPOINTS                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   POST          │    │   POST          │    │   GET           │
│ /auth/login     │    │ /tokens/access  │    │ /tokens/status  │
│                 │    │                 │    │ /{user_id}      │
│ Input:          │    │ Input:          │    │ Input:          │
│ - username      │    │ - user_id       │    │ - user_id       │
│ - password      │    │ - app_name      │    │ - JWT token     │
│                 │    │ - purpose       │    │                 │
│ Output:         │    │ - JWT token     │    │ Output:         │
│ - JWT token     │    │                 │    │ - has_token     │
│ - expires_in    │    │ Output:         │    │ - metadata      │
└─────────────────┘    │ - token         │    └─────────────────┘
                       │ - metadata      │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   DELETE        │
                       │ /tokens/{user_id}│
                       │                 │
                       │ Input:          │
                       │ - user_id       │
                       │ - JWT token     │
                       │                 │
                       │ Output:         │
                       │ - success msg   │
                       └─────────────────┘
```

## 🔄 Data Flow Examples

### Example 1: GitHub Integration
```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│GitHub   │───▶│Token    │───▶│API      │───▶│Database │───▶│GitHub   │
│App      │    │Client   │    │Server   │    │(Decrypt)│    │API      │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
     │              │              │              │              │
     ▼              ▼              ▼              ▼              ▼
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│Need     │    │Login &  │    │Verify   │    │Return   │    │Use      │
│Token    │    │Request  │    │JWT &    │    │Token    │    │Token    │
│         │    │Token    │    │Access   │    │         │    │         │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
```

### Example 2: Custom API Integration
```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│Custom   │───▶│Token    │───▶│API      │───▶│Database │───▶│External │
│App      │    │Client   │    │Server   │    │(Decrypt)│    │Service  │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
     │              │              │              │              │
     ▼              ▼              ▼              ▼              ▼
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│API      │    │Get      │    │Validate │    │Retrieve │    │Authenticate│
│Request  │    │Token    │    │Access   │    │Token    │    │Request  │
│         │    │         │    │         │    │         │    │         │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
```

## 🛡️ Security Layers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SECURITY LAYERS                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              EXTERNAL ACCESS                                │
├─────────────────────────────────────────────────────────────────────────────┤
│ Layer 1: HTTPS/TLS Encryption (Transport Security)                         │
├─────────────────────────────────────────────────────────────────────────────┤
│ Layer 2: JWT Authentication (24hr expiry, Bearer tokens)                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ Layer 3: User Access Control (Users can only access their own tokens)      │
├─────────────────────────────────────────────────────────────────────────────┤
│ Layer 4: Application Purpose Tracking (Audit trail)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ Layer 5: Database Encryption (Fernet encryption at rest)                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ Layer 6: Password Hashing (SHA-256 for user passwords)                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                              DATABASE STORAGE                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 📊 System Components Interaction

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        COMPONENT INTERACTIONS                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Streamlit  │    │   FastAPI   │    │ PostgreSQL  │
│   Web App   │    │  API Server │    │  Database   │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  User       │    │  External   │    │  Encrypted  │
│  Interface  │    │  API Access │    │  Token      │
│             │    │             │    │  Storage    │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Token      │    │  JWT        │    │  Fernet     │
│  Setup      │    │  Auth       │    │  Encryption │
│  & Mgmt     │    │  & Access   │    │  & Decrypt  │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                           ▼
                   ┌─────────────┐
                   │  Token      │
                   │  Client     │
                   │  Library    │
                   └─────────────┘
                           │
                           ▼
                   ┌─────────────┐
                   │  External   │
                   │  Apps       │
                   └─────────────┘
```

## 🔄 Complete Request Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              REQUEST FLOW                                   │
└─────────────────────────────────────────────────────────────────────────────┘

1. User Setup (One-time):
   User → Streamlit → Login → Token Setup → Encrypted Storage

2. External App Access:
   App → Token Client → API Server → Database → Decrypted Token → App

3. Security Checks:
   - JWT Token Validation (24hr expiry)
   - User Access Control (own tokens only)
   - Application Purpose Tracking
   - Database Encryption/Decryption

4. Token Usage:
   App → External Service → API Calls → Success/Failure
```

This visual flow shows the complete architecture and data flow of the secure token storage system, highlighting the security layers and how external applications can securely access tokens while maintaining encryption and access control. 