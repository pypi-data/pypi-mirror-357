

---

# INX Web Framework

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![PyPI](https://img.shields.io/pypi/v/inxlib)


**INX** is a lightweight Python web framework designed for simplicity and performance. Built for learning purposes, it provides essential features like routing, middleware support, template rendering, and static file serving.

There should be __init__.py file inside of inxlib file please don't forget

---

## Features

- **Easy Routing**: Define routes with support for dynamic URL parameters.
- **Middleware Support**: Add custom middleware for request/response processing.
- **Template Rendering**: Use Jinja2 templates for dynamic HTML content.
- **Static File Serving**: Serve static files (CSS, JS, images) with WhiteNoise.
- **JSON Responses**: Easily return JSON data from your routes.
- **Exception Handling**: Custom exception handlers for better error management.

---



## Installation

You can install **INX Web Framework** via pip:

```bash
pip install inxlib

## Installation

You can install **INX Web Framework** via pip:

```bash
pip install inxlib
```

---

## Quick Start

### 1. Create a Simple App

```python
from inxlib.app import PyInxApp

app = PyInxApp()

@app.route("/")
def home(request, response):
    response.text = "Hello, World!"

if __name__ == "__main__":
    app.run()
```



---



#### Run the App with Waitress
You can run your app directly using Waitress:

```bash
waitress-serve --call 'app:app'
```

This command assumes that your `app` object is defined in a file named `app.py`.

---

### Development vs Production
- **Development**: Use the built-in development server for testing and debugging.
- **Production**: Use **Waitress** or another production-ready server like **Gunicorn** or **uWSGI**.

---

### Start the Development Server
For development, you can start the server using:

```bash
python app.py
```

Visit `http://localhost:8080` in your browser to see "Hello, World!".



## Basic Usage

### Routing

Define routes with the `@app.route` decorator:

```python
@app.route("/about")
def about(request, response):
    response.text = "About Us"
```

### Dynamic Routes

Capture URL parameters:

```python
@app.route("/hello/{name}")
def greet(request, response, name):
    response.text = f"Hello, {name}!"
```

### Template Rendering

Use Jinja2 templates to render HTML:

```python
@app.route("/template")
def template_handler(req, resp):
    resp.body = app.template(
        'home.html',
        context={"new_title": "Best Title", "new_body": "Best body"}
    )
```

### Static Files

Serve static files (CSS, JS, images) from the `static/` directory:

```html
<link rel="stylesheet" href="/static/test.css">
```

### JSON Responses

Return JSON data:

```python
@app.route("/json")
def json_handler(request, response):
    response.json = {"status": "success", "message": "Hello, JSON!"}
```

### Middleware

Add custom middleware:

```python
class LoggingMiddleware:
    def __init__(self, app):
        self.app = app

    def process_request(self, req):
        print(f"Request: {req.url}")

    def process_response(self, req, resp):
        print(f"Response: {resp.status_code}")

app.add_middleware(LoggingMiddleware)
```

---


### Example Test File (`test_app.py`)

```python
import pytest
from inxlib import PyInxApp

@pytest.fixture
def app():
    return PyInxApp()

@pytest.fixture
def test_client(app):
    return app.test_session()

def test_basic_route_adding(app, test_client):
    @app.route("/home")
    def home(req, resp):
        resp.text = "Hello from home"

    response = test_client.get("https://testserver/home")
    assert response.text == "Hello from home"

def test_template_handler(app, test_client):
    @app.route("/test-template")
    def template_handler(req, resp):
        resp.body = app.template(
            'test.html',
            context={"new_title": "Best Title", "new_body": "Best body"}
        )
    
    response = test_client.get("http://testserver/test-template")

    assert "Best Title" in response.text
    assert "Best body" in response.text
    assert "text/html" in response.headers["Content-Type"]
```

