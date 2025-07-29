import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
RUN_DIR = os.path.dirname(os.getcwd())
app_manager_log_path = os.path.join(BASE_DIR, 'logs/app_manager.log')
os.makedirs(os.path.join(RUN_DIR,"resources"), exist_ok=True)
print("当前启动目录",RUN_DIR)
print(BASE_DIR)
app_manager_db_path = os.path.join(RUN_DIR, 'resources/app_manager.db')
app_settings_ini_path = os.path.join(RUN_DIR, 'resources/app_settings.ini')
