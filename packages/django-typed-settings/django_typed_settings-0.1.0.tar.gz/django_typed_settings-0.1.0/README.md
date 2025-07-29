# Django Typed Settings

Type validation for bare django configuration settings system.
Alternative to `django-environ` and somehow `pydantic`

## Example

```python
# /settings.py

# Default Django way
TIMEOUT = 80                             # Hardcoded
TIMEOUT = os.environ.get("TIMEOUT", 80). # Environment, non-type safe

# Django Typed Settings
TIMEOUT = env_key('TIMEOUT', as_type=int, default=80) # Runtime checkable, type safe
```
