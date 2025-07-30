# Authentication Module Implementation Plan

## 📋 **SCOPE & OBJECTIVES**

### **Primary Goals**
- Implement comprehensive authentication handling for Cognify API
- Support multiple authentication methods (JWT tokens, API keys)
- Automatic token refresh and session management
- Secure credential storage and handling

### **Deliverables**
1. Authentication module with JWT and API key support
2. Token refresh mechanism
3. Session management
4. Credential validation and security
5. Authentication middleware for HTTP requests
6. User profile and permissions handling

## 🛠️ **TECHNOLOGY STACK**

### **Core Dependencies**
- **PyJWT**: JWT token handling and validation
- **cryptography**: Secure token operations
- **keyring**: Secure credential storage (optional)
- **datetime**: Token expiration handling

### **Authentication Methods Supported**
Based on Cognify API analysis:
1. **JWT Bearer Tokens**: `Authorization: Bearer <jwt_token>`
2. **API Keys**: Multiple formats:
   - `Authorization: Bearer cog_<api_key>`
   - `X-API-Key: cog_<api_key>`
   - Query parameter: `?api_key=cog_<api_key>`

## 🏗️ **IMPLEMENTATION STRATEGY**

### **Step 1: Authentication Base Classes**
```python
# auth/base.py
from abc import ABC, abstractmethod

class AuthProvider(ABC):
    @abstractmethod
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for requests"""
        
    @abstractmethod
    def is_valid(self) -> bool:
        """Check if authentication is valid"""
        
    @abstractmethod
    async def refresh_if_needed(self) -> bool:
        """Refresh authentication if needed"""

class JWTAuthProvider(AuthProvider):
    def __init__(self, access_token: str, refresh_token: Optional[str] = None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self._expires_at: Optional[datetime] = None
    
    def get_auth_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.access_token}"}

class APIKeyAuthProvider(AuthProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def get_auth_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"}
```

### **Step 2: Authentication Module**
```python
# auth/auth_module.py
class AuthModule:
    def __init__(self, client: 'CognifyClient'):
        self.client = client
        self._auth_provider: Optional[AuthProvider] = None
        
    async def login(self, email: str, password: str) -> TokenResponse:
        """Login with email/password and get JWT tokens"""
        
    async def logout(self) -> None:
        """Logout and invalidate tokens"""
        
    def set_api_key(self, api_key: str) -> None:
        """Set API key for authentication"""
        
    def set_jwt_tokens(self, access_token: str, refresh_token: str) -> None:
        """Set JWT tokens for authentication"""
        
    async def get_current_user(self) -> UserResponse:
        """Get current authenticated user info"""
```

### **Step 3: Token Management**
```python
# auth/token_manager.py
class TokenManager:
    def __init__(self):
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._expires_at: Optional[datetime] = None
    
    def set_tokens(self, access_token: str, refresh_token: str, expires_in: int):
        """Set JWT tokens with expiration"""
        
    def is_expired(self) -> bool:
        """Check if access token is expired"""
        
    def needs_refresh(self) -> bool:
        """Check if token needs refresh (expires in <5 minutes)"""
        
    async def refresh_token(self, client: 'HTTPClient') -> bool:
        """Refresh access token using refresh token"""
```

### **Step 4: Authentication Middleware**
```python
# auth/middleware.py
class AuthMiddleware:
    def __init__(self, auth_provider: AuthProvider):
        self.auth_provider = auth_provider
    
    async def prepare_request(self, request: httpx.Request) -> httpx.Request:
        """Add authentication headers to request"""
        await self.auth_provider.refresh_if_needed()
        headers = self.auth_provider.get_auth_headers()
        request.headers.update(headers)
        return request
    
    def handle_auth_error(self, response: httpx.Response) -> None:
        """Handle authentication errors (401, 403)"""
        if response.status_code == 401:
            raise CognifyAuthenticationError("Invalid or expired credentials")
        elif response.status_code == 403:
            raise CognifyAuthenticationError("Insufficient permissions")
```

## 🔗 **DEPENDENCIES**

### **Prerequisites**
- Core client architecture (Plan 02) completed
- HTTP client wrapper implemented
- Configuration system in place

### **External Dependencies**
- PyJWT >= 2.8.0
- cryptography >= 41.0.0
- python-dateutil >= 2.8.0

## ✅ **SUCCESS CRITERIA**

### **Functional Requirements**
- [ ] JWT authentication working (login/logout)
- [ ] API key authentication working
- [ ] Automatic token refresh implemented
- [ ] Multiple auth header formats supported
- [ ] Secure credential handling
- [ ] User profile retrieval working

### **Security Requirements**
- [ ] Tokens stored securely (not in plain text logs)
- [ ] Automatic token expiration handling
- [ ] Proper error handling for auth failures
- [ ] No credential leakage in error messages

### **API Design**
```python
# JWT Authentication
client = CognifyClient()
await client.auth.login("user@example.com", "password")
user = await client.auth.get_current_user()

# API Key Authentication
client = CognifyClient(api_key="cog_your_api_key")
# or
client = CognifyClient()
client.auth.set_api_key("cog_your_api_key")

# Manual token management
client.auth.set_jwt_tokens(access_token, refresh_token)
```

## ⏱️ **TIMELINE**

### **Day 1: Core Authentication**
- Implement base auth classes
- JWT token handling
- API key authentication

### **Day 2: Advanced Features**
- Token refresh mechanism
- Authentication middleware
- Session management

### **Day 3: Integration & Testing**
- Integration with HTTP client
- Comprehensive testing
- Security validation

## 🧪 **TESTING STRATEGY**

### **Unit Tests**
```python
def test_jwt_auth_provider():
    provider = JWTAuthProvider("access_token", "refresh_token")
    headers = provider.get_auth_headers()
    assert headers["Authorization"] == "Bearer access_token"

def test_api_key_auth_provider():
    provider = APIKeyAuthProvider("cog_test_key")
    headers = provider.get_auth_headers()
    assert headers["Authorization"] == "Bearer cog_test_key"

async def test_token_refresh():
    # Mock refresh endpoint
    # Test automatic token refresh

def test_auth_middleware():
    # Test request header injection
    # Test error handling
```

### **Integration Tests**
```python
async def test_login_flow():
    client = CognifyClient()
    response = await client.auth.login("test@example.com", "password")
    assert response.access_token
    
    user = await client.auth.get_current_user()
    assert user.email == "test@example.com"

async def test_api_key_flow():
    client = CognifyClient(api_key="cog_test_key")
    user = await client.auth.get_current_user()
    assert user is not None
```

### **Security Tests**
- Token expiration handling
- Invalid credential scenarios
- Permission boundary testing
- Credential storage security

## 📚 **DOCUMENTATION**

### **Authentication Guide**
```python
# Quick Start - API Key
from cognify_sdk import CognifyClient

client = CognifyClient(api_key="cog_your_api_key")

# Quick Start - JWT Login
client = CognifyClient()
await client.auth.login("your@email.com", "password")

# Advanced - Manual Token Management
client.auth.set_jwt_tokens(
    access_token="eyJ...",
    refresh_token="eyJ..."
)

# Check Authentication Status
user = await client.auth.get_current_user()
print(f"Logged in as: {user.email}")
```

### **Security Best Practices**
- Store API keys in environment variables
- Use JWT tokens for user sessions
- Handle token refresh automatically
- Never log sensitive credentials

## 🔄 **RISK MITIGATION**

### **Security Risks**
- **Token Leakage**: Secure storage and handling
- **Expired Tokens**: Automatic refresh mechanism
- **Invalid Credentials**: Clear error messages

### **Technical Risks**
- **API Changes**: Flexible auth provider system
- **Network Issues**: Retry logic for auth requests
- **Concurrency**: Thread-safe token management

---

**Plan Status**: 🟡 Ready for Implementation
**Dependencies**: Core client architecture (Plan 02)
**Estimated Effort**: 3 days
**Priority**: High (Required for API access)
