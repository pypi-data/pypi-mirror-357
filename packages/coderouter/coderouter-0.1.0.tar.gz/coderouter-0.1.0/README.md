# CodeRouter

A simple routing library for Python applications.

## Installation

```bash
pip install coderouter
```

## Usage

```python
from coderouter import Router

router = Router()

def home_handler():
    return "Welcome home!"

def about_handler():
    return "About page"

router.add_route("/", home_handler)
router.add_route("/about", about_handler, methods=["GET", "POST"])

# Handle requests
result = router.handle("/")  # Returns "Welcome home!"
result = router.handle("/about", "POST")  # Returns "About page"
```

## License

MIT