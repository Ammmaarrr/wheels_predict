# MVP Frontend Server Configuration

## Update Your Server

To use the new MVP frontend, update your server files to serve templates from:
- **Template directory**: `frontend_mvp/templates/`
- **Static directory**: `frontend_mvp/static/`

## Example FastAPI Configuration:

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Serve static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="frontend_mvp/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="frontend_mvp/templates")
```

## Example Flask Configuration:

```python
from flask import Flask, render_template

app = Flask(__name__, 
           template_folder='frontend_mvp/templates',
           static_folder='frontend_mvp/static')
```

## Files to Update:
- simple_mvp_server.py
- mvp_fastapi_server.py
- web_interface.py

Generated: 2025-08-02T18:03:40.663000
