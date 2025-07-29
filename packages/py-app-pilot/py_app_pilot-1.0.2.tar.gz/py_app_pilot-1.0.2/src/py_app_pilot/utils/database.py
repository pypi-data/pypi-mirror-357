import os
import sys

from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from .eunm import app_manager_db_path
engine = create_engine(f'sqlite:///{app_manager_db_path}')
Base = declarative_base()

class GlobalSetting(Base):
    __tablename__ = 'global_settings'
    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)

    def __repr__(self):
        return f"GlobalSetting(key='{self.key}', value='{self.value}')"

class App(Base):
    __tablename__ = 'apps'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)
    python_path = Column(String, default=sys.executable)
    arguments = Column(String, default='')
    working_directory = Column(String, default='')
    group = Column(String, default='默认组')
    is_running = Column(Boolean, default=False)
    def __repr__(self):
        return f"App(id={self.id}, name='{self.name}', path='{self.path}', arguments='{self.arguments}', working_directory='{self.working_directory}', group='{self.group}', is_running={self.is_running})"

class AppDataManager:
    def __init__(self):
        self.engine = create_engine(f'sqlite:///{app_manager_db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.session = scoped_session(Session)
        
    def add_app(self, name, path, arguments='', working_directory='', group='默认组'):
        app = App(
            name=name,
            path=path,
            arguments=arguments,
            working_directory=working_directory,
            group=group
        )
        self.session.add(app)
        self.session.commit()
        self.session.refresh(app)
        return app
    
    def get_all_apps(self):
        apps = self.session.query(App).all()
        self.session.commit()
        return apps
    
    def get_app_by_id(self, app_id):
        app = self.session.query(App).filter_by(id=app_id).first()
        self.session.commit()
        return app
    
    def update_app(self, app_id, **kwargs):
        app = self.session.query(App).filter_by(id=app_id).first()
        if app:
            for key, value in kwargs.items():
                if hasattr(app, key):
                    setattr(app, key, value)
            self.session.commit()
    
    def delete_app(self, app_id):
        app = self.session.query(App).filter_by(id=app_id).first()
        if app:
            self.session.delete(app)
            self.session.commit()
    
    def update_app_status(self, app_id, is_running):
        self.update_app(app_id, is_running=is_running)

    def get_global_setting(self, key, default=None):
        setting = self.session.query(GlobalSetting).filter_by(key=key).first()
        return setting.value if setting else default

    def save_global_setting(self, key, value):
        setting = self.session.query(GlobalSetting).filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            setting = GlobalSetting(key=key, value=value)
            self.session.add(setting)
        self.session.commit()

    def get_app_settings(self, app_id):
        app = self.get_app_by_id(app_id)
        if app:
            return {
                'name': app.name,
                'path': app.path,
                'python_path': app.python_path,
                'arguments': app.arguments,
                'working_directory': app.working_directory,
                'group': app.group
            }
        return None

    def update_group_name(self, old_name, new_name):
        apps = self.session.query(App).filter_by(group=old_name).all()
        for app in apps:
            app.group = new_name
        self.session.commit()

# 初始化时创建数据库文件
if not os.path.exists(app_manager_db_path):
    Base.metadata.create_all(engine)
    session = scoped_session(sessionmaker(bind=engine, expire_on_commit=False))
    session.commit()