<div align="center">
  <h2 align="center">CyberTemp API Client</h2>
  <p align="center">
    A Python client for interacting with the CyberTemp temporary email service API.
    <br />
    <br />
    <a href="https://cybertemp.xyz">🌐 Website</a>
    ·
    <a href="#-changelog">📜 ChangeLog</a>
    ·
    <a href="https://github.com/sexfrance/cybertemp-wrapper/issues">⚠️ Report Bug</a>
  </p>
</div>

---

### ⚙️ Installation

```bash
pip install cybertemp
```

### 🚀 Quick Start

```python
from cybertemp import CyberTemp

# Initialize (free tier, optional debug mode)
client = CyberTemp(debug=True)

# Or with API key (premium, optional)
client = CyberTemp(api_key="your_api_key_here")

# Get available domains
domains = client.get_domains()

# Check mailbox with retry settings (optional parameters: max_retries, delay_between_retries)
emails = client.get_email_content("test@cybertemp.xyz", max_retries=3, delay_between_retries=2.0)
```

You can purchase an API key here: [CyberTemp Pricing](https://cybertemp.xyz/pricing)

### 📚 API Reference

#### Initialization
```python
client = CyberTemp(
    debug=True,           # Optional: Enable debug logging
    api_key=None          # Optional: API key for premium features
)
```

#### Available Methods

1. **Get Email Content**
```python
emails = client.get_email_content("test@cybertemp.xyz", max_retries=3, delay_between_retries=2.0)  # Optional: max_retries, delay_between_retries
```

2. **Get Email by ID**
```python
email = client.get_email_content_by_id("email_id_here")
```

3. **Get Available Domains**
```python
domains = client.get_domains()
```

4. **Search Email by Subject**
```python
mail_id = client.get_mail_by_subject(
    email="test@cybertemp.xyz",
    subject_contains="Verification",
    max_attempts=5,                # Optional
    delay_between_retries=1.5       # Optional
)
```

5. **Extract URL from Email**
```python
url = client.extract_url_from_message(
    email="test@cybertemp.xyz",
    subject_contains="Verification",
    url_pattern=r'https://[^\s<>"]+',
    max_attempts=5,                # Optional
    delay_between_retries=1.5       # Optional
)
```

6. **Check API Balance** (Premium, requires API key)
```python
balance = client.get_balance()
```

### 💳 Premium Features

- No rate limiting
- API key support
- Credit system
- Priority support

### ⚠️ Rate Limits

- Free tier: 1-second delay between requests
- Premium tier: No delays, pay-per-use

### 📜 ChangeLog

```diff
v1.0.1 ⋮ 2025-03-05
+ Added configurable retry and delay options for email checking functions
+ Indicated optional parameters in documentation

v1.0.0 ⋮ 2025-02-14
! Initial release
```

<p align="center">
  <img src="https://img.shields.io/badge/python-3.7+-blue.svg"/>
  <img src="https://img.shields.io/badge/license-MIT-green.svg"/>
  <img src="https://img.shields.io/badge/version-1.0.1-orange.svg"/>
</p>