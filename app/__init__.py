# app/__init__.py
from flask import Flask
from flask_cors import CORS
from config.settings import get_config
from app.routes import api

def create_app():
    app = Flask(__name__)
    
    # โหลด config
    app.config.from_object(get_config())
    
    # ตั้งค่า CORS เพื่อให้ frontend สามารถเรียกใช้ API ได้
    CORS(app)
    
    # ลงทะเบียน blueprint
    app.register_blueprint(api, url_prefix='/api')
    
    return app