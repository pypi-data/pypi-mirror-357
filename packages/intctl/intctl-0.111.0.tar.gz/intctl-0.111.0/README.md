remove the existing package: rm -rf build/ dist/ *.egg-info
build again: python -m build 

upload to pypi: twine upload dist/* 















## 📦 Overview

The CLI now supports:

* 🔐 Secure login via browser-based device authorization (OAuth2-compliant)
* 🏢 Organization-scoped login (per session)
* 🔁 Automatic token refresh using offline tokens
* 👤 User context inspection (`whoami`)
* 👋 Session clearing (`logout`)

---

## 🧑‍💻 Commands

All auth-related commands are grouped under:

```bash
intctl auth <subcommand>
```

### 1. 🔐 `intctl auth login`

Start login flow via browser:

```bash
intctl auth login
```

**Flow:**

1. Prompts for organization ID or name
2. Opens Keycloak device login via browser
3. User authenticates (e.g., via password or IdP)
4. Token is issued and saved locally:

   * `access_token`: short-lived
   * `refresh_token`: long-lived
   * `username`, `org`: stored with token

**Stored at:** `~/.intctl_token`

---

### 2. 🧾 `intctl auth whoami`

Displays the current authenticated user and selected organization:

```bash
intctl auth whoami
```

**Output:**

```
👤 User: saeid
🏢 Org:  org-abc
```

---

### 3. 🚪 `intctl auth logout`

Clears the local session:

```bash
intctl auth logout
```

This deletes the token and org information stored in `~/.intctl_token`.

---

## 🔁 Token Refresh

The CLI automatically refreshes your token when it's near expiry:

* Refreshes if token expires in **less than 60 seconds**
* Uses stored `refresh_token` (offline token)
* Seamless; no user input required

### 🔧 Use in Code

```python
from login import get_valid_access_token

headers = {
    "Authorization": f"Bearer {get_valid_access_token()}",
    "X-Org": load_login_data()["org"]
}
```

---

## 🗂️ Token Storage Format

Stored as JSON at `~/.intctl_token`:

```json
{
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "username": "saeid",
  "org": "intellithing"
}
```

---

## 🔐 Keycloak Client Configuration Summary

| Field                | Value                   |
| -------------------- | ----------------------- |
| Client Type          | OpenID Connect (Public) |
| Device Auth Grant    | ✅ Enabled               |
| Offline Access Scope | ✅ Assigned              |
| Access Type          | Public                  |

---

## 🔄 Future Ideas (Optional Enhancements)

* `intctl auth switch-org`: change org context without full re-login
* Encrypt token file using `keyring` or GPG
* Add `intctl auth refresh` (manual token refresh)

---

## 📎 Example Usage

```bash
intctl auth login
intctl configure
intctl setup
intctl auth whoami
intctl auth logout
```

---

