import os

from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from .eunm import app_manager_db_path
engine = create_engine(f'sqlite:///{app_manager_db_path}')
Base = declarative_base()

class App(Base):
    __tablename__ = 'apps'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)
    arguments = Column(String, default='')
    working_directory = Column(String, default='')
    is_running = Column(Boolean, default=False)
    def __repr__(self):
        return f"App(id={self.id}, name='{self.name}', path='{self.path}', arguments='{self.arguments}', working_directory='{self.working_directory}', is_running={self.is_running})"

class AppDataManager:
    def __init__(self):
        self.engine = create_engine(f'sqlite:///{app_manager_db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.session = scoped_session(Session)
        
    def add_app(self, name, path, arguments='', working_directory=''):
        app = App(
            name=name,
            path=path,
            arguments=arguments,
            working_directory=working_directory
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

# 初始化时创建数据库文件
if not os.path.exists(app_manager_db_path):
    Base.metadata.create_all(engine)
    session = scoped_session(sessionmaker(bind=engine, expire_on_commit=False))
    session.commit()