# Flask 應用工廠（可選）
from flask import Flask
from flask_cors import CORS

def create_app(config_name='development'):
    """應用工廠函數"""
    app = Flask(__name__)
    CORS(app)
    app.config['JSON_AS_ASCII'] = False
    return app
