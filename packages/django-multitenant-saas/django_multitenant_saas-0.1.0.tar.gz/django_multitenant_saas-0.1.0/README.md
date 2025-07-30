# django-multitenant-saas

A plug-and-play multi-tenancy package for Django SaaS apps using shared database and shared schema model.

---

## 🚀 Features

- Tenant model with domain-based identification
- Middleware to auto-detect tenant from request host
- Thread-local storage of current tenant
- Abstract base model to scope all tenant-specific data
- Automatic query filtering based on active tenant

---

## 📦 Installation

```bash
pip install django-multitenant-saas
```

---

## ⚙️ Setup

### 1. Add to Installed Apps

In your `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'multitenant',
]
```

### 2. Add Middleware

```python
MIDDLEWARE = [
    ...
    'multitenant.middleware.TenantMiddleware',
]
```

Make sure it's **before** views or anything that uses `request.tenant`.

### 3. Migrate

Run initial migrations:

```bash
python manage.py makemigrations multitenant
python manage.py migrate
```

---

## 🧱 Usage

### Step 1: Create a Tenant

```python
from multitenant.models import Tenant

Tenant.objects.create(name="Tenant A", domain="tenant-a.localhost")
```

### Step 2: Create Your Models with Tenant Awareness

```python
from multitenant.models import TenantAwareModel

class Invoice(TenantAwareModel):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
```

This will automatically:
- Add a `tenant` ForeignKey
- Auto-set `tenant` from the request
- Ensure query filtering by current tenant

### Step 3: Query Your Data (Filtered Automatically)

```python
Invoice.objects.all()  # Automatically scoped to current request's tenant
```

---

## 🔍 Behind the Scenes

### Middleware
Detects the domain from the request and fetches the tenant:
```python
host = request.get_host().split(':')[0]
Tenant.objects.get(domain=host)
```

### Thread-Local Storage
The tenant is stored per-request using Python’s `threading.local`.

### Model Inheritance
Your custom models inherit `TenantAwareModel`, which auto-fills and filters by tenant.

---

## 🛡 Security Note

- Always scope views and queries using the `TenantAwareModel` or `TenantManager`.
- Do not allow direct access to `tenant` field in serializers unless validated.

---

## 📚 Example Project Structure

```
myproject/
├── myapp/
│   └── models.py  # Inherit from TenantAwareModel
├── multitenant/   # Installed from package
│   └── ...
├── settings.py    # Add app and middleware
```

---

## 🧪 Testing (Optional)

You can add custom middleware tests or unit tests to simulate tenant context.

---

## 📬 Support

Have questions or want to contribute? Reach out or fork the repo. Built by [Pranav Dixit](https://medium.com/@pranavdixit20)

---
MIT License
