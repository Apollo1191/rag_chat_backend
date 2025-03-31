# config/settings.py
import os
from dotenv import load_dotenv

# โหลดตัวแปรจาก .env ไฟล์
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    GOOGLE_AI_API_KEY = os.environ.get('GOOGLE_AI_API_KEY')
    
    # ตั้งค่าเพิ่มเติมของ Gemini
    GEMINI_MODEL_NAME = "gemini-1.5-flash"  # เปลี่ยนเป็นรุ่นที่ต้องการใช้
    
    # ตั้งค่าเกี่ยวกับ prompt templates
    PROMPT_TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'prompt_templates')
    
    # ตั้งค่าเกี่ยวกับข้อมูลฝึกสอน
    TRAINING_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'training')
    EXAMPLES_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'examples')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

# เลือกใช้ config ตาม environment
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# ฟังก์ชันสำหรับเรียกใช้ config
def get_config():
    config_name = os.environ.get('FLASK_ENV') or 'default'
    return config[config_name]