# 📦 xUserAuth

A modular, production-ready authentication and user management library for FastAPI.

**Supports:**

* JWT-based auth (access, refresh, email verification, password reset)
* Role-based access control (RBAC)
* Password hashing
* Google OAuth integration
* Custom user model support

---

## 📌 Installation

```bash
pip install xuserauth
```

Or for development:

```bash
git clone https://github.com/yourusername/xuserauth.git
cd xuserauth
pip install -e .
```

---

## 🧠 Core Components

| Module             | Purpose                                   |
| ------------------ | ----------------------------------------- |
| `auth_manager.py`  | Central class for managing auth workflows |
| `jwt_utils.py`     | JWT encoding/decoding helpers             |
| `hashing.py`       | Password hashing & verification           |
| `roles.py`         | Role checking utilities                   |
| `exceptions.py`    | Standardized auth errors                  |
| `schemas.py`       | Pydantic base user schemas                |
| `social/google.py` | Google OAuth2 login/callback              |

---

## 🛠 Setup & Configuration

### ✅ 1. Define your user model

```python
# myapp/models.py
class User:
    def __init__(self, id, email, password, is_active=True, roles=["user"], email_verified=False):
        self.id = id
        self.email = email
        self.password = password
        self.is_active = is_active
        self.roles = roles
        self.email_verified = email_verified
```

### ✅ 2. Define a user loader

```python
async def get_user_by_id(user_id: str):
    # Replace with your DB query logic
    return fake_user_db.get(user_id)
```

### ✅ 3. Initialize `AuthManager`

```python
from xuserauth import AuthManager
from myapp.models import User

auth = AuthManager(
    user_model=User,
    jwt_secret="your_secret_key_here",
    user_loader=get_user_by_id
)
```

---

## 🔐 Usage Examples

### 🧪 Register / Hash Password

```python
hashed = auth.hash_password("mypassword")
```

### 🔐 Login

```python
if auth.verify_password("mypassword", user.password):
    access_token = auth.generate_token(user)
    refresh_token = auth.generate_refresh_token(user)
```

### 🔄 Refresh Token

```python
new_token = await auth.refresh_access_token(refresh_token)
```

### 🛡 Protect Routes (Auth + Role)

```python
@app.get("/me")
@auth.require_authenticated
async def get_profile(user):
    return {"email": user.email, "roles": user.roles}
```

```python
@app.get("/admin")
@auth.require_role("admin")
async def get_admin_panel(user):
    return {"message": "Welcome Admin"}
```

---

## 📬 Token Types

| Type      | Use                                |
| --------- | ---------------------------------- |
| `access`  | Short-lived access token (default) |
| `refresh` | Refresh token for session renewal  |
| `email`   | Email verification token           |
| `reset`   | Password reset token               |

---

## 🧪 Google OAuth Login

### Redirect to Google:

```python
@app.get("/login/google")
async def google_login(request: Request):
    return await login_with_google(request)
```

### Google Callback:

```python
@app.get("/auth/google/callback")
async def google_callback(request: Request):
    user_info = await auth_google_callback(request)
    # Link or register user in your DB
```

---

## 🔍 Testing

Tests included for:

* JWT creation/verification
* Password hashing
* Role-based access
* Google OAuth
* Error handling

Run tests:

```bash
pytest test/
```

---

## ⚠️ Exception Classes

* `InvalidToken`
* `PermissionDenied`
* `UserNotFound`
* `AuthError`

---

## ✅ Schema Examples (Pydantic)

```python
from xuserauth.schemas import UserCreate, UserRead

user = UserCreate(email="a@a.com", password="secure123")
```

---

## 📎 Example Folder Structure

```
yourapp/
├── main.py
├── models.py
├── routes.py
├── auth/
│   └── auth_manager.py
├── utils/
│   └── hashing.py
```

---

## 🧩 Roadmap

* ✅ Google login
* ✅ RBAC
* ⏳ Facebook login (planned)
* ⏳ Refresh token rotation
* ⏳ Database adapters (SQLModel, Tortoise, Prisma)

---

## 📝 License

MIT License © 2025 Aliyu Abdulbasit Ayinde

---