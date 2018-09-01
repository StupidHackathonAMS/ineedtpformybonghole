#!/usr/bin/env python
import os
from app import create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'development')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007, debug=True)
