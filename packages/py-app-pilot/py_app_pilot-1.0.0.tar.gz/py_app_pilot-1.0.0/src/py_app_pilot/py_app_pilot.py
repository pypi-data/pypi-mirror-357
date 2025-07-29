import sys
import os
import subprocess
import shlex
from .utils.log_util import logger
import psutil

import configparser
import platform
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QTextEdit, QListWidget,
    QListWidgetItem, QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QMessageBox, QFileDialog, QMenu, QAction, QDialog, QTextBrowser
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject, QTimer, QCoreApplication, QUrl
from PyQt5.QtGui import QFont
from .utils.database import AppDataManager
from .utils.eunm import app_manager_log_path, app_settings_ini_path
from .resources import logo_rc, author_rc
import PyQt5.QtGui as QtGui


class ProcessOutputReader(QThread):
    output_received = pyqtSignal(str)

    def __init__(self, process):
        super().__init__()
        self.process = process

    def run(self):
        while self.process.poll() is None:
            output = self.process.stdout.readline()
            if output:
                self.output_received.emit(output.strip())
        # 读取剩余输出
        remaining = self.process.stdout.read()
        if remaining:
            self.output_received.emit(remaining.strip())


class PythonAppManager(QMainWindow):
    def __init__(self):
        super().__init__()
        # 设置全局暗色调样式
        self.setStyleSheet(""
                           "QMainWindow, QWidget {background-color: #2d2d2d; color: #ffffff;}"
                           "QPushButton {background-color: #4a4a4a; color: white; border: 1px solid #666; border-radius: 4px; padding: 5px 10px;}"
                           "QPushButton:hover {background-color: #5a5a5a;}"
                           "QPushButton:pressed {background-color: #3a3a3a;}"
                           "QListWidget {background-color: #3d3d3d; border: 1px solid #555; border-radius: 4px;}"
                           "QListWidget::item {padding: 5px; border-bottom: 1px solid #444;}"
                           "QListWidget::item:selected {background-color: #5a5a5a; color: white;}"
                           "QTabWidget::pane {border: 1px solid #555; background-color: #2d2d2d;}"
                           "QTabBar::tab {background-color: #3d3d3d; color: white; padding: 8px 16px; border: 1px solid #555; border-bottom-color: #555; border-top-left-radius: 4px; border-top-right-radius: 4px;}"
                           "QTabBar::tab:selected {background-color: #2d2d2d; border-bottom-color: #2d2d2d;}"
                           "QTabBar::tab:hover:!selected {background-color: #4a4a4a;}"
                           "QLineEdit, QTextEdit {background-color: #3d3d3d; color: white; border: 1px solid #555; border-radius: 4px; padding: 5px;}"
                           "QLabel {color: #ffffff;}"
                           "QMessageBox {background-color: #2d2d2d;}"
                           "QMessageBox QPushButton {min-width: 80px;}"
                           )
        self.app_data_manager = AppDataManager()
        self.processes = {}
        self.app_settings = {}
        self.global_settings = {}
        self.config = configparser.ConfigParser()
        self.logger = logger
        self.load_settings()
        self.init_ui()
        self.app_processes = {}
        self.output_widgets = {}
        self.output_readers = {}
        self.app_settings = {}
        self.app_tabs = {}  # 新增：跟踪应用对应的tab索引
        self.load_settings()
        self.load_apps_from_database()

    def init_ui(self):
        self.setWindowTitle('Py-App-Pilot(AI全程开发 by.test：龙翔)')

        self.setMinimumSize(1000, 850)
        # 加载logo
        self.setWindowIcon(QtGui.QIcon(":icon/logo.jpg"))

        # 创建Tab控件
        self.tabWidget = QTabWidget()
        self.setCentralWidget(self.tabWidget)

        # 初始化应用管理UI
        self.app_management_widget = QWidget()
        self.init_app_management_ui()
        self.tabWidget.addTab(self.app_management_widget, "应用管理")
        # 初始化日志查看UI
        self.log_viewer_widget = QWidget()
        self.init_log_viewer_ui()
        self.tabWidget.addTab(self.log_viewer_widget, "日志查看")
        # 初始化系统管理UI
        self.system_management_widget = QWidget()
        self.init_system_management_ui()
        self.tabWidget.addTab(self.system_management_widget, "系统管理")



    def init_app_management_ui(self):
        # 创建主横向布局
        main_layout = QHBoxLayout()

        # 左侧应用列表和操作按钮区域
        left_layout = QVBoxLayout()

        # 应用列表
        self.app_list = QListWidget()
        self.app_list.itemSelectionChanged.connect(self.on_app_selected)
        left_layout.addWidget(self.app_list)

        # 增加右键菜单 全选和取消全选
        self.app_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.app_list.customContextMenuRequested.connect(self.show_context_menu)

        # 操作按钮
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("添加应用")
        self.remove_btn = QPushButton("删除应用")
        self.start_btn = QPushButton("启动应用")
        self.stop_btn = QPushButton("关闭应用")

        # 绑定按钮事件
        self.add_btn.clicked.connect(self.add_app)
        self.remove_btn.clicked.connect(self.remove_app)
        self.start_btn.clicked.connect(self.start_app)
        self.stop_btn.clicked.connect(self.stop_app)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)

        left_layout.addLayout(btn_layout)

        # 右侧设置区域
        self.settings_group = QGroupBox("应用参数设置")
        self.settings_form = QFormLayout()

        self.name_input = QLineEdit()
        self.args_input = QLineEdit()
        self.cwd_input = QLineEdit()
        self.python_path_input = QLineEdit()
        self.browse_python_btn = QPushButton("浏览...")
        self.save_settings_btn = QPushButton("保存设置")
        # 关于作者
        self.about_author_btn = QPushButton("关于作者")
        self.about_author_btn.clicked.connect(self.show_about_dialog)

        self.save_settings_btn.clicked.connect(self.save_app_settings)
        self.browse_python_btn.clicked.connect(self.browse_python_path)

        self.settings_form.addRow("应用名称:", self.name_input)
        self.settings_form.addRow("命令行参数:", self.args_input)
        self.settings_form.addRow("工作目录:", self.cwd_input)
        self.settings_form.addRow("Python解释器路径:", self.python_path_input)
        self.settings_form.addRow(self.browse_python_btn)
        self.settings_form.addRow(self.save_settings_btn)
        self.settings_form.addRow(self.about_author_btn)
        self.settings_group.setLayout(self.settings_form)
        self.settings_group.setEnabled(False)

        # 将左右布局添加到主布局
        main_layout.addLayout(left_layout, 1)
        main_layout.addWidget(self.settings_group, 1)

        self.app_management_widget.setLayout(main_layout)

    def init_log_viewer_ui(self):
        layout = QVBoxLayout()

        # 日志显示区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        # 刷新按钮
        self.refresh_log_btn = QPushButton("手动刷新日志")
        self.refresh_log_btn.clicked.connect(self.refresh_log)
        layout.addWidget(self.refresh_log_btn)

        self.log_viewer_widget.setLayout(layout)
        self.refresh_log()  # 初始加载日志

    def init_system_management_ui(self):
        layout = QVBoxLayout()
        self.system_info_label = QLabel()
        self.system_info_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        # 全局Python路径设置
        global_settings_group = QGroupBox("全局设置")
        global_settings_form = QFormLayout()
        self.global_python_path_input = QLineEdit()
        self.browse_global_python_btn = QPushButton("浏览...")
        self.save_global_btn = QPushButton("保存全局设置")
        self.browse_global_python_btn.clicked.connect(self.browse_global_python_path)
        self.save_global_btn.clicked.connect(self.save_global_settings)
        global_settings_form.addRow("全局Python解释器路径:", self.global_python_path_input)
        global_settings_form.addRow(self.browse_global_python_btn)
        global_settings_form.addRow(self.save_global_btn)
        global_settings_group.setLayout(global_settings_form)

        # 获取系统信息
        system_info = self.get_system_info()
        self.system_info_label.setText(f"系统信息:\n{system_info}")

        layout.addWidget(global_settings_group)
        layout.addWidget(self.system_info_label)
        self.system_management_widget.setLayout(layout)

        # 加载全局Python路径
        python_path = self.global_settings.get('python_path', '')
        if not python_path:  # 检查是否为空字符串或None
            python_path = sys.executable
        self.global_python_path_input.setText(python_path)

    def get_system_info(self):
        """获取系统基本信息"""
        try:
            info = []
            info.append(f"操作系统: {platform.system()} {platform.release()}")
            info.append(f"Python版本: {platform.python_version()}")
            info.append(f"处理器: {platform.processor()}")
            info.append(f"内存: {self.get_memory_usage()}")
            return '\n'.join(info)
        except Exception as e:
            logger.error(f"获取系统信息失败: {str(e)}")
            return "无法获取系统信息"

    def get_memory_usage(self):
        """获取内存使用情况"""
        mem = psutil.virtual_memory()
        total = self.format_bytes(mem.total)
        available = self.format_bytes(mem.available)
        used = self.format_bytes(mem.used)
        percent = mem.percent
        return f"总计: {total}, 可用: {available}, 已用: {used} ({percent}%)"

    def format_bytes(self, bytes, decimals=2):
        """将字节数格式化为人类可读的单位"""
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        if bytes == 0:
            return '0 B'
        size = float(bytes)
        unit_index = 0
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        return f"{size:.{decimals}f} {units[unit_index]}"

    def show_context_menu(self, pos):
        menu = QMenu(self)
        select_all_action = menu.addAction("全选")
        deselect_all_action = menu.addAction("取消全选")
        action = menu.exec_(self.app_list.mapToGlobal(pos))

        if action == select_all_action:
            for i in range(self.app_list.count()):
                item = self.app_list.item(i)
                item.setCheckState(Qt.Checked)
        elif action == deselect_all_action:
            for i in range(self.app_list.count()):
                item = self.app_list.item(i)
                item.setCheckState(Qt.Unchecked)

    def closeEvent(self, event):
        # 应用未关闭完之前，不允许关闭窗口
        if self.app_processes:
            QMessageBox.warning(self, "警告", "请先关闭所有运行中的应用")
            event.ignore()
            return
        super().closeEvent(event)

    def load_settings(self):
        # 确保配置文件存在
        if not os.path.exists(app_settings_ini_path):
            self.logger.warning(f"配置文件不存在，将创建新文件: {app_settings_ini_path}")
            with open(app_settings_ini_path, 'w') as f:
                pass

        self.config.read(app_settings_ini_path)
        # 加载全局设置
        self.global_settings = {}
        if self.config.has_section('Global'):
            self.global_settings['python_path'] = self.config.get('Global', 'python_path', fallback=sys.executable)
        else:
            self.global_settings['python_path'] = sys.executable
        # 加载应用设置
        self.app_settings = {}
        apps = self.app_data_manager.get_all_apps()
        app_id_map = {app.id: app for app in apps}

        # 迁移旧配置（路径或名称为key）到新配置（ID为key）
        for section in self.config.sections():
            if section == 'Global':
                continue

            # 检查是否已经是ID格式
            if section.isdigit() and int(section) in app_id_map:
                # 已经是ID格式，直接加载
                app_id = int(section)
                self.app_settings[app_id] = {
                    'args': self.config.get(section, 'args', fallback=''),
                    'cwd': self.config.get(section, 'cwd', fallback=''),
                    'python_path': self.config.get(section, 'python_path', fallback='')
                }
                continue

            # 尝试通过路径查找应用
            found = False
            for app_id, app in app_id_map.items():
                app_path = os.path.normpath(app.path.strip('" '))
                app_path = os.path.abspath(app_path)
                if section == app_path or section == f"{app.name} (ID: {app.id})":
                    # 找到匹配的应用，迁移配置
                    self.app_settings[app_id] = {
                        'args': self.config.get(section, 'args', fallback=''),
                        'cwd': self.config.get(section, 'cwd', fallback=''),
                        'python_path': self.config.get(section, 'python_path', fallback='')
                    }
                    # 添加新section
                    if not self.config.has_section(str(app_id)):
                        self.config.add_section(str(app_id))
                    self.config.set(str(app_id), 'args', self.app_settings[app_id]['args'])
                    self.config.set(str(app_id), 'cwd', self.app_settings[app_id]['cwd'])
                    # 删除旧section
                    self.config.remove_section(section)
                    found = True
                    break

            if not found:
                self.logger.warning(f"无法迁移旧配置: {section}")

        # 保存迁移后的配置
        try:
            with open(app_settings_ini_path, 'w') as f:
                self.config.write(f)
        except Exception as e:
            self.logger.error(f"保存迁移配置失败: {str(e)}")
            # 更新Python路径UI
            if hasattr(self, 'python_path_input'):
                self.python_path_input.setText(self.global_settings['python_path'])

    def browse_python_path(self):
        """打开文件对话框选择应用Python解释器路径"""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择Python解释器",
            self.python_path_input.text() or os.path.dirname(sys.executable),
            "Python Executable (python.exe);;All Files (*)"
        )
        if path:
            self.python_path_input.setText(path)

    def browse_global_python_path(self):
        """打开文件对话框选择全局Python解释器路径"""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择全局Python解释器",
            self.global_python_path_input.text() or os.path.dirname(sys.executable),
            "Python Executable (python.exe);;All Files (*)"
        )
        if path:
            self.global_python_path_input.setText(path)

    def save_global_settings(self):
        """保存全局设置到配置文件"""
        if not self.config.has_section('Global'):
            self.config.add_section('Global')
        new_path = self.global_python_path_input.text().strip() or sys.executable
        self.config.set('Global', 'python_path', new_path)
        try:
            with open(app_settings_ini_path, 'w') as f:
                self.config.write(f)
            self.global_settings['python_path'] = new_path
            self.logger.info(f"已更新全局Python解释器路径: {new_path}")
            # QMessageBox.information(self, "成功", "全局设置已保存")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存全局设置失败: {str(e)}")
            self.logger.error(f"保存全局设置失败: {str(e)}")

    def save_app_settings(self):
        current_item = self.app_list.currentItem()
        if not current_item:
            return

        app_id = current_item.data(Qt.UserRole)
        app = self.app_data_manager.get_app_by_id(app_id)
        if not app:
            return

        app_path = app.path.strip('" ').strip()
        app_path = os.path.normpath(app_path)
        app_path = os.path.abspath(app_path)
        # 清理路径作为配置文件section名称
        sanitized_path = app_path
        args = self.args_input.text()
        cwd = self.cwd_input.text()

        self.app_settings[sanitized_path] = {'args': args, 'cwd': cwd}

        # 保存到配置文件
        # 更新应用名称
        new_name = self.name_input.text().strip()
        if new_name and new_name != app.name:
            self.app_data_manager.update_app(app_id, name=new_name)
            # 更新列表项显示
            current_item.setText(f"{new_name} (ID: {app_id})")
            app.name = new_name

        # 使用ID作为配置section名称
        section_name = str(app_id)
        if not self.config.has_section(section_name):
            self.config.add_section(section_name)
        self.config.set(section_name, 'args', args)
        self.config.set(section_name, 'cwd', cwd)
        self.config.set(section_name, 'python_path', self.python_path_input.text())

        try:
            with open(app_settings_ini_path, 'w') as f:
                self.config.write(f)
            # QMessageBox.information(self, "成功", "应用设置已保存")
            self.logger.info(f"保存应用设置: {app_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存设置失败: {str(e)}")
            self.logger.error(f"保存设置失败: {str(e)}")

        # 同时保存全局Python路径
        self.save_global_settings()

    def on_app_selected(self):
        current_item = self.app_list.currentItem()
        if current_item:
            app_id = current_item.data(Qt.UserRole)
            app = self.app_data_manager.get_app_by_id(app_id)
            if not app:
                return
            app_path = app.path.strip('" ').strip()
            app_path = os.path.normpath(app_path)
            app_path = os.path.abspath(app_path)
            self.settings_group.setEnabled(True)
            # 加载应用设置并替换参数占位符
            self.load_settings()
            # 配置迁移: 从旧的section名称迁移到应用路径
            old_section = f"{app.name} (ID: {app.id})"
            if old_section in self.app_settings:
                # 复制旧设置到新section
                self.app_settings[app_path] = self.app_settings[old_section]
                # 更新配置文件
                if not self.config.has_section(app_path):
                    self.config.add_section(app_path)
                self.config.set(app_path, 'args', self.app_settings[app_path]['args'])
                self.config.set(app_path, 'cwd', self.app_settings[app_path]['cwd'])
                # 删除旧section
                if self.config.has_section(old_section):
                    self.config.remove_section(old_section)
                # 保存配置文件
                try:
                    with open(app_settings_ini_path, 'w') as f:
                        self.config.write(f)
                    self.logger.info(f"迁移设置从旧section '{old_section}' 到新section '{app_path}'")
                    # 重新加载设置
                    self.load_settings()
                except Exception as e:
                    self.logger.error(f"迁移设置失败: {str(e)}")
            # 使用应用ID获取设置
            settings = self.app_settings.get(app_id, {})
            self.name_input.setText(app.name)
            self.args_input.setText(settings.get('args', ''))
            self.cwd_input.setText(settings.get('cwd', ''))
            self.python_path_input.setText(settings.get('python_path', ''))
            # 连接编辑完成信号到保存方法
            self.save_app_settings()
        else:
            self.settings_group.setEnabled(False)

    def refresh_log(self):
        try:
            with open('logs/app_manager.log', 'r', encoding='utf-8') as f:
                log_content = f.read()
                self.log_text.setText(log_content)
                # 滚动到底部
                self.log_text.moveCursor(self.log_text.textCursor().End)
        except Exception as e:
            self.log_text.setText(f"无法加载日志: {str(e)}")

    def load_apps_from_database(self):
        """从数据库加载应用列表"""
        self.app_list.clear()
        apps = self.app_data_manager.get_all_apps()
        for app in apps:
            item = QListWidgetItem(f"{app.name} (ID: {app.id})")
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, app.id)
            self.app_list.addItem(item)
            # 存储应用ID作为item的数据
            self.app_list.item(self.app_list.count() - 1).setData(Qt.UserRole, app.id)

    def add_app(self):
        """添加新应用"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择Python应用", "", "Python Files (*.py);;All Files (*)"
        )
        if file_path:
            # 获取文件名作为应用名称
            app_name = os.path.splitext(os.path.basename(file_path))[0]
            # 规范化路径
            file_path = os.path.normpath(file_path)
            file_path = os.path.abspath(file_path)
            # 检查路径是否包含空格
            if ' ' in file_path:
                QMessageBox.warning(self, "警告", "应用路径不能包含空格")
                return
            # 添加到数据库
            app = self.app_data_manager.add_app(
                name=app_name,
                path=file_path,
                arguments=self.args_input.text(),
                working_directory=self.cwd_input.text()
            )
            app = self.app_data_manager.get_app_by_id(app.id)
            # 添加到列表
            # 显式创建列表项以确保item不为None
            # 可勾选
            item = QListWidgetItem(f"{app.name} ({app.id})")
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, app.id)
            self.app_list.addItem(item)
            self.app_list.setCurrentItem(item)
            # 初始化新应用配置
            section_name = str(app.id)
            if not self.config.has_section(section_name):
                self.config.add_section(section_name)
            self.config.set(section_name, 'args', '')
            self.config.set(section_name, 'cwd', '')
            with open(app_settings_ini_path, 'w') as f:
                self.config.write(f)
            self.save_app_settings()
            QMessageBox.information(self, "成功", f"应用 '{app.name}' 添加成功")
            self.logger.info(f"Added application: {app_name} ({file_path})")

    def remove_app(self):
        current_item = self.app_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请选择要删除的应用")
            return

        app_id = current_item.data(Qt.UserRole)
        current_app = self.app_data_manager.get_app_by_id(app_id)
        if not current_app:
            QMessageBox.warning(self, "警告", "无法获取应用路径")
            return

        # 检查应用是否正在运行
        if app_id in self.app_processes:
            QMessageBox.warning(self, "警告", "应用正在运行，无法删除")
            return

        # 二次确认删除
        reply = QMessageBox.question(self, "确认删除", "确定要删除此应用吗？此操作不可恢复。",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

            # 从数据库中删除应用
            try:
                self.app_data_manager.delete_app(current_app.id)
                # 删除对应的配置
                section_name = str(current_app.id)
                if self.config.has_section(section_name):
                    self.config.remove_section(section_name)
                    with open(app_settings_ini_path, 'w') as f:
                        self.config.write(f)
                # 从应用设置中移除
                if current_app.id in self.app_settings:
                    del self.app_settings[current_app.id]
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除应用失败: {str(e)}")
                self.logger.error(f"删除应用失败 {current_app.name}: {str(e)}")
                return
        # 清理相关资源
        if app_id in self.app_tabs:
            del self.app_tabs[app_id]
        if app_id in self.output_widgets:
            del self.output_widgets[app_id]
        # 从列表中移除
        # 使用takeItem而非removeItemWidget，确保从列表模型中彻底移除项
        index = self.app_list.row(current_item)
        self.app_list.takeItem(index)
        # 刷新应用列表
        self.load_apps_from_database()
        # 只显示文件名而非完整路径，提升用户体验
        app_name = current_app.name
        QMessageBox.information(self, "成功", f"应用 '{app_name}' 删除成功")
        self.logger.info(f"已删除应用: {app_name}")

    def on_process_finished(self, pid, app_id):
        """应用进程结束时的处理"""
        if app_id in self.app_processes:
            del self.app_processes[app_id]
            del self.output_readers[app_id]

        # 更新数据库中所有应用的运行状态
        for i in range(self.app_list.count()):
            item = self.app_list.item(i)
            item_app_id = item.data(Qt.UserRole)
            app = self.app_data_manager.get_app_by_id(item_app_id)
            if app and app.id == app_id:
                self.app_data_manager.update_app_status(app_id, False)
                break

        self.logger.info(f"Application process finished: {app_id}")

    def stop_app(self, current_item=None):
        if not current_item:
            for i in range(self.app_list.count()):
                item = self.app_list.item(i)
                if item.checkState() == Qt.Checked:
                    self.stop_app(item)
            return
        if current_item:
            self.stop_app_by_id(current_item.data(Qt.UserRole))

    def _cleanup_ui_resources(self, app_id):
        """清理应用相关的UI资源"""
        # if app_id in self.app_tabs:
        self.tabWidget.removeTab(self.tabWidget.indexOf(self.app_tabs[app_id]))
        del self.app_tabs[app_id]
        # if app_id in self.output_widgets:
        del self.output_widgets[app_id]
        # if app_id in self.app_processes:
        del self.app_processes[app_id]

    def stop_app_by_id(self, app_id):
        self.logger.info(f"Stopping application: {app_id} {self.app_processes}")
        if app_id in self.app_processes:
            # 二次确认关闭
            app_name = self.app_data_manager.get_app_by_id(app_id).name
            reply = QMessageBox.question(self, "确认关闭", f"确定要关闭应用 '{app_name}' 吗？",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply != QMessageBox.Yes:
                return

            process_info = self.app_processes[app_id]
            try:
                parent = psutil.Process(process_info.pid)
                # 终止所有子进程
                for child in parent.children(recursive=True):
                    try:
                        child.terminate()
                    except psutil.NoSuchProcess:
                        pass
                # 终止父进程
                parent.terminate()

                # 等待进程终止
                try:
                    parent.wait(timeout=5)
                except psutil.TimeoutExpired:
                    # 超时后尝试强制终止
                    parent.kill()
                    parent.wait(timeout=2)

                # 检查进程是否已终止
                if parent.is_running():
                    raise RuntimeError(f"进程 {parent.pid} 无法终止")

                # 进程成功终止，清理UI资源
                self._cleanup_ui_resources(app_id)
                self.logger.info(f"关闭应用: {self.app_data_manager.get_app_by_id(app_id).name}")

            except psutil.NoSuchProcess:
                self.logger.warning(f"进程 {process_info.pid} 已不存在")
                self._cleanup_ui_resources(app_id)
            except Exception as e:
                self.logger.error(f"关闭应用失败: {str(e)}")
                QMessageBox.critical(self, "错误", f"关闭应用失败: {str(e)}")

    def restart_app(self, app_id):
        """重启应用"""
        self.logger.info(f"Restarting application: {app_id}")
        # 先停止应用
        self.stop_app_by_id(app_id)
        # 查找应用列表项并重新启动
        for i in range(self.app_list.count()):
            item = self.app_list.item(i)
            if item.data(Qt.UserRole) == app_id:
                # 延迟启动以确保进程已终止
                QTimer.singleShot(1000, lambda item=item: self.start_app(item))
                break

    def update_output(self, app_id, text):
        """更新指定应用Tab页中的输出内容"""
        if app_id in self.output_widgets:
            self.output_widgets[app_id].append(text)

    def load_app_settings(self, app_id):
        """加载应用配置"""
        config = configparser.ConfigParser()
        config.read(app_settings_ini_path)
        settings = {}
        if str(app_id) in config:
            settings = dict(config[str(app_id)])
        return settings

    def start_app(self, current_item=None):
        """启动选中的应用"""
        if not current_item:
            for i in range(self.app_list.count()):
                item = self.app_list.item(i)
                if item.checkState() == Qt.Checked:
                    self.start_app(item)
            return
        if not current_item or current_item.checkState() != Qt.Checked:
            QMessageBox.warning(self, "警告", "请先选择一个应用")
            return

        app_id = current_item.data(Qt.UserRole)
        app = self.app_data_manager.get_app_by_id(app_id)
        if not app:
            QMessageBox.critical(self, "错误", "应用数据不存在")
            return

        # 检查是否已有该应用的tab，如果有则切换并清空输出
        if app_id in self.app_tabs:
            tab_index = self.tabWidget.indexOf(self.app_tabs[app_id])
            self.tabWidget.setCurrentIndex(tab_index)
            output_text = self.output_widgets.get(app_id)

            # 检查进程是否正在运行
            process = self.app_processes.get(app_id)
            if process and process.poll() is None:
                # 进程仍在运行，仅清空输出
                if output_text:
                    output_text.clear()
                QMessageBox.information(self, "提示", f"应用 '{app.name}' 已在运行中，已切换到对应的Tab页面")
                return
            else:
                # 进程已停止，清空输出并准备重新启动
                if output_text:
                    output_text.clear()
        else:
            # 创建新的tab内容widget和布局
            tab_widget = QWidget()
            tab_layout = QVBoxLayout(tab_widget)

            # 创建按钮布局
            button_layout = QHBoxLayout()
            restart_btn = QPushButton("重启")
            close_btn = QPushButton("关闭")
            button_layout.addWidget(restart_btn)
            button_layout.addWidget(close_btn)

            # 创建输出文本框
            output_text = QTextEdit()
            output_text.setReadOnly(True)
            font = QFont()
            font.setFamily("SimHei")
            output_text.setFont(font)

            # 将按钮布局和输出文本框添加到垂直布局
            tab_layout.addLayout(button_layout)
            tab_layout.addWidget(output_text)

            # 添加tab
            tab_index = self.tabWidget.addTab(tab_widget, app.name)
            self.app_tabs[app_id] = tab_widget  # 存储整个widget
            self.output_widgets[app_id] = output_text  # 存储输出文本框
            self.tabWidget.setCurrentIndex(tab_index)

            # 连接按钮信号
            restart_btn.clicked.connect(lambda: self.restart_app(app_id))
            close_btn.clicked.connect(lambda: self.stop_app_by_id(app_id))

        # 获取应用路径
        app_path = app.path
        if not os.path.exists(app_path):
            QMessageBox.critical(self, "错误", f"应用路径不存在: {app_path}")
            return

        # 规范化应用路径
        app_path = os.path.normpath(app_path)
        app_path = os.path.abspath(app_path)

        # 迁移旧配置
        old_section = f"{app.name} (ID: {app.id})"
        sanitized_path = app_path
        if self.config.has_section(old_section) and not self.config.has_section(sanitized_path):
            # 创建新section
            self.config.add_section(sanitized_path)
            # 复制设置
            for key, value in self.config.items(old_section):
                self.config.set(sanitized_path, key, value)
            # 删除旧section
            self.config.remove_section(old_section)
            # 保存配置文件
            try:
                with open(app_settings_ini_path, 'w') as f:
                    self.config.write(f)
                self.logger.info(f"迁移设置从旧section '{old_section}' 到新section '{sanitized_path}'")
            except Exception as e:
                self.logger.error(f"迁移设置失败: {str(e)}")

        # 加载应用设置
        settings = self.app_settings.get(app.id, {})
        arguments = settings.get('args', '')
        cwd = settings.get('cwd', '')

        # 处理工作目录
        if cwd and os.path.isdir(cwd):
            working_dir = cwd
        else:
            working_dir = os.path.dirname(app_path) or os.getcwd()

        # 格式化参数
        formatted_args = arguments.format(app_path=app_path, app_id=app_id, app_name=app.name)

        # 构建命令
        # 使用全局Python解释器路径
        app_python_path = settings.get('python_path', '').strip()
        # 增强Python路径获取逻辑，确保正确使用应用设置的解释器路径
        app_python_path = app_python_path.strip() if app_python_path else None
        global_python_path = self.global_settings.get('python_path', '').strip()
        python_path = app_python_path if app_python_path else (global_python_path if global_python_path else sys.executable)
        command = [python_path, app_path] + shlex.split(formatted_args)

        # 启动应用进程
        try:
            process = subprocess.Popen(
                command,
                cwd=working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            self.app_processes[app_id] = process

            # 更新tab标题显示PID
            self.tabWidget.setTabText(tab_index, f"{app.name} (PID: {process.pid})")

            # 创建输出阅读器
            reader = ProcessOutputReader(process)
            reader.output_received.connect(lambda text: self.update_output(app_id, text))
            reader.start()

            # 连接进程完成信号
            output_reader = ProcessOutputReader(process)
            output_reader.finished.connect(
                lambda pid=process.pid, app_path=app.path: self.on_process_finished(pid, app_path))
            output_reader.output_received.connect(lambda text: self.update_output(app_id, text))
            self.logger.info(f"启动应用: {app.name}, PID: {process.pid}")
        except Exception as e:
            QMessageBox.critical(self, "启动失败", f"无法启动应用: {str(e)}")
            self.logger.error(f"启动应用失败: {str(e)}")
            if app_id in self.app_tabs:
                tab_index = self.tabWidget.indexOf(self.app_tabs[app_id])
                self.tabWidget.removeTab(tab_index)
                del self.app_tabs[app_id]
                del self.output_widgets[app_id]

    def show_about_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('关于作者')
        # 如果屏幕大于2k，设置dialog大小
        if self.screen().size().height() > 2000:
            dialog.setMinimumSize(500, 1000)
        else:
            dialog.setMinimumSize(350, 500)

        layout = QVBoxLayout()

        # 作者图片
        pixmap = QtGui.QPixmap(':images/author.jpg')
        # 调整图片大小保持比例
        scaled_pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image_label = QLabel()
        image_label.setPixmap(scaled_pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(image_label)

        # 作者信息
        info_text = '''<h3>关于作者</h3>
    <p><strong>作者笔名：</strong>龙翔</p>
    <p>作者从2021年开始深耕跨境电商领域ERP、办公自动化开发多年，构建了社区开发团队，如果你感兴趣，欢迎前来咨询</p>
    <p>期望各位开发者多多指点，如果有业务需要合作，也请与我们联系。</p>
    '''
        info_browser = QTextBrowser()
        info_browser.setHtml(info_text)
        layout.addWidget(info_browser)

        # 项目地址和社区地址 - 使用PyQt5组件
        link_layout = QVBoxLayout()

        # 项目地址
        project_layout = QHBoxLayout()
        project_label = QLabel('<strong>项目地址：</strong>')
        project_button = QPushButton('打开项目')
        project_button.setStyleSheet('background-color: #007bff; color: white; border-radius: 3px; padding: 5px 10px;')
        project_button.clicked.connect(lambda: QtGui.QDesktopServices.openUrl(QUrl('https://github.com/NelsonLongxiang/py-app-pilot')))
        project_layout.addWidget(project_label)
        project_layout.addWidget(project_button)
        project_layout.addStretch()
        link_layout.addLayout(project_layout)

        # 社区地址
        community_layout = QHBoxLayout()
        community_label = QLabel('<strong>社区地址：</strong>')
        community_button = QPushButton('访问社区')
        community_button.setStyleSheet('background-color: #007bff; color: white; border-radius: 3px; padding: 5px 10px;')
        community_button.clicked.connect(lambda: QtGui.QDesktopServices.openUrl(QUrl('https://lifesa.cn')))
        community_layout.addWidget(community_label)
        community_layout.addWidget(community_button)
        community_layout.addStretch()
        link_layout.addLayout(community_layout)

        layout.addLayout(link_layout)

        # 确定按钮
        ok_button = QPushButton('确定')
        ok_button.clicked.connect(dialog.accept)
        layout.addWidget(ok_button, alignment=Qt.AlignCenter)
        # 禁止移动
        dialog.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        dialog.setLayout(layout)
        dialog.exec_()


if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    # 设置DPI 300
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    # 设置全局字体大小为14
    font = QFont()
    font.setPointSize(12)
    font.setFamily("SimHei")
    app.setFont(font)
    window = PythonAppManager()
    window.show()
    sys.exit(app.exec_())


// ... existing code ...
        # 加载应用数据并分组显示
        self.load_and_group_apps()

    def load_and_group_apps(self):
        """加载应用数据并按组分类显示"""
        self.app_tree.clear()
        apps = self.load_apps()  # 假设已存在加载应用的方法
        groups = {}

        # 创建所有组和应用项
        for app in apps:
            group_name = app.get('group', '默认组')
            app_name = app.get('name', '未命名应用')

            # 创建组节点（如果不存在）
            if group_name not in groups:
                group_item = QTreeWidgetItem([group_name])
                group_item.setFlags(group_item.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
                self.app_tree.addTopLevelItem(group_item)
                groups[group_name] = group_item

            # 创建应用子节点
            app_item = QTreeWidgetItem([app_name])
            app_item.setData(0, Qt.UserRole, app)  # 存储完整应用数据
            app_item.setFlags(app_item.flags() | Qt.ItemIsUserCheckable)
            app_item.setCheckState(0, Qt.Unchecked)
            groups[group_name].addChild(app_item)

        # 展开所有组
        for group_item in groups.values():
            self.app_tree.expandItem(group_item)

    def load_apps(self):
        """加载应用数据"""
        apps = self.app_data_manager.get_all_apps()
        for app in apps:
            item = QListWidgetItem(f"{app.name} (ID: {app.id})")
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, app.id)
            self.app_list.addItem(item)
            # 存储应用ID作为item的数据
            self.app_list.item(self.app_list.count() - 1).setData(Qt.UserRole, app.id)

    def add_app(self):
        """添加新应用"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择Python应用", "", "Python Files (*.py);;All Files (*)"
        )
        if file_path:
            # 获取文件名作为应用名称
            app_name = os.path.splitext(os.path.basename(file_path))[0]
            # 规范化路径
            file_path = os.path.normpath(file_path)
            file_path = os.path.abspath(file_path)
            # 检查路径是否包含空格
            if ' ' in file_path:
                QMessageBox.warning(self, "警告", "应用路径不能包含空格")
                return
            # 添加到数据库
            app = self.app_data_manager.add_app(
                name=app_name,
                path=file_path,
                arguments=self.args_input.text(),
                working_directory=self.cwd_input.text()
            )
            app = self.app_data_manager.get_app_by_id(app.id)
            # 添加到列表
            # 显式创建列表项以确保item不为None
            # 可勾选
            item = QListWidgetItem(f"{app.name} ({app.id})")
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, app.id)
            self.app_list.addItem(item)
            self.app_list.setCurrentItem(item)
            # 初始化新应用配置
            section_name = str(app.id)
            if not self.config.has_section(section_name):
                self.config.add_section(section_name)
            self.config.set(section_name, 'args', '')
            self.config.set(section_name, 'cwd', '')
            with open(app_settings_ini_path, 'w') as f:
                self.config.write(f)
            self.save_app_settings()
            QMessageBox.information(self, "成功", f"应用 '{app.name}' 添加成功")
            self.logger.info(f"Added application: {app_name} ({file_path})")

    def remove_app(self):
        current_item = self.app_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请选择要删除的应用")
            return

        app_id = current_item.data(Qt.UserRole)
        current_app = self.app_data_manager.get_app_by_id(app_id)
        if not current_app:
            QMessageBox.warning(self, "警告", "无法获取应用路径")
            return

        # 检查应用是否正在运行
        if app_id in self.app_processes:
            QMessageBox.warning(self, "警告", "应用正在运行，无法删除")
            return

        # 二次确认删除
        reply = QMessageBox.question(self, "确认删除", "确定要删除此应用吗？此操作不可恢复。",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

            # 从数据库中删除应用
            try:
                self.app_data_manager.delete_app(current_app.id)
                # 删除对应的配置
                section_name = str(current_app.id)
                if self.config.has_section(section_name):
                    self.config.remove_section(section_name)
                    with open(app_settings_ini_path, 'w') as f:
                        self.config.write(f)
                # 从应用设置中移除
                if current_app.id in self.app_settings:
                    del self.app_settings[current_app.id]
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除应用失败: {str(e)}")
                self.logger.error(f"删除应用失败 {current_app.name}: {str(e)}")
                return
        # 清理相关资源
        if app_id in self.app_tabs:
            del self.app_tabs[app_id]
        if app_id in self.output_widgets:
            del self.output_widgets[app_id]
        # 从列表中移除
        # 使用takeItem而非removeItemWidget，确保从列表模型中彻底移除项
        index = self.app_list.row(current_item)
        self.app_list.takeItem(index)
        # 刷新应用列表
        self.load_apps_from_database()
        # 只显示文件名而非完整路径，提升用户体验
        app_name = current_app.name
        QMessageBox.information(self, "成功", f"应用 '{app_name}' 删除成功")
        self.logger.info(f"已删除应用: {app_name}")

    def on_process_finished(self, pid, app_id):
        """应用进程结束时的处理"""
        if app_id in self.app_processes:
            del self.app_processes[app_id]
            del self.output_readers[app_id]

        # 更新数据库中所有应用的运行状态
        for i in range(self.app_list.count()):
            item = self.app_list.item(i)
            item_app_id = item.data(Qt.UserRole)
            app = self.app_data_manager.get_app_by_id(item_app_id)
            if app and app.id == app_id:
                self.app_data_manager.update_app_status(app_id, False)
                break

        self.logger.info(f"Application process finished: {app_id}")

    def stop_app(self, current_item=None):
        if not current_item:
            for i in range(self.app_list.count()):
                item = self.app_list.item(i)
                if item.checkState() == Qt.Checked:
                    self.stop_app(item)
            return
        if current_item:
            self.stop_app_by_id(current_item.data(Qt.UserRole))

    def _cleanup_ui_resources(self, app_id):
        """清理应用相关的UI资源"""
        # if app_id in self.app_tabs:
        self.tabWidget.removeTab(self.tabWidget.indexOf(self.app_tabs[app_id]))
        del self.app_tabs[app_id]
        # if app_id in self.output_widgets:
        del self.output_widgets[app_id]
        # if app_id in self.app_processes:
        del self.app_processes[app_id]

    def stop_app_by_id(self, app_id):
        self.logger.info(f"Stopping application: {app_id} {self.app_processes}")
        if app_id in self.app_processes:
            # 二次确认关闭
            app_name = self.app_data_manager.get_app_by_id(app_id).name
            reply = QMessageBox.question(self, "确认关闭", f"确定要关闭应用 '{app_name}' 吗？",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply != QMessageBox.Yes:
                return

            process_info = self.app_processes[app_id]
            try:
                parent = psutil.Process(process_info.pid)
                # 终止所有子进程
                for child in parent.children(recursive=True):
                    try:
                        child.terminate()
                    except psutil.NoSuchProcess:
                        pass
                # 终止父进程
                parent.terminate()

                # 等待进程终止
                try:
                    parent.wait(timeout=5)
                except psutil.TimeoutExpired:
                    # 超时后尝试强制终止
                    parent.kill()
                    parent.wait(timeout=2)

                # 检查进程是否已终止
                if parent.is_running():
                    raise RuntimeError(f"进程 {parent.pid} 无法终止")

                # 进程成功终止，清理UI资源
                self._cleanup_ui_resources(app_id)
                self.logger.info(f"关闭应用: {self.app_data_manager.get_app_by_id(app_id).name}")

            except psutil.NoSuchProcess:
                self.logger.warning(f"进程 {process_info.pid} 已不存在")
                self._cleanup_ui_resources(app_id)
            except Exception as e:
                self.logger.error(f"关闭应用失败: {str(e)}")
                QMessageBox.critical(self, "错误", f"关闭应用失败: {str(e)}")

    def restart_app(self, app_id):
        """重启应用"""
        self.logger.info(f"Restarting application: {app_id}")
        # 先停止应用
        self.stop_app_by_id(app_id)
        # 查找应用列表项并重新启动
        for i in range(self.app_list.count()):
            item = self.app_list.item(i)
            if item.data(Qt.UserRole) == app_id:
                # 延迟启动以确保进程已终止
                QTimer.singleShot(1000, lambda item=item: self.start_app(item))
                break

    def update_output(self, app_id, text):
        """更新指定应用Tab页中的输出内容"""
        if app_id in self.output_widgets:
            self.output_widgets[app_id].append(text)

    def load_app_settings(self, app_id):
        """加载应用配置"""
        config = configparser.ConfigParser()
        config.read(app_settings_ini_path)
        settings = {}
        if str(app_id) in config:
            settings = dict(config[str(app_id)])
        return settings

    def start_app(self, current_item=None):
        """启动选中的应用"""
        if not current_item:
            for i in range(self.app_list.count()):
                item = self.app_list.item(i)
                if item.checkState() == Qt.Checked:
                    self.start_app(item)
            return
        if not current_item or current_item.checkState() != Qt.Checked:
            QMessageBox.warning(self, "警告", "请先选择一个应用")
            return

        app_id = current_item.data(Qt.UserRole)
        app = self.app_data_manager.get_app_by_id(app_id)
        if not app:
            QMessageBox.critical(self, "错误", "应用数据不存在")
            return

        # 检查是否已有该应用的tab，如果有则切换并清空输出
        if app_id in self.app_tabs:
            tab_index = self.tabWidget.indexOf(self.app_tabs[app_id])
            self.tabWidget.setCurrentIndex(tab_index)
            output_text = self.output_widgets.get(app_id)

            # 检查进程是否正在运行
            process = self.app_processes.get(app_id)
            if process and process.poll() is None:
                # 进程仍在运行，仅清空输出
                if output_text:
                    output_text.clear()
                QMessageBox.information(self, "提示", f"应用 '{app.name}' 已在运行中，已切换到对应的Tab页面")
                return
            else:
                # 进程已停止，清空输出并准备重新启动
                if output_text:
                    output_text.clear()
        else:
            # 创建新的tab内容widget和布局
            tab_widget = QWidget()
            tab_layout = QVBoxLayout(tab_widget)

            # 创建按钮布局
            button_layout = QHBoxLayout()
            restart_btn = QPushButton("重启")
            close_btn = QPushButton("关闭")
            button_layout.addWidget(restart_btn)
            button_layout.addWidget(close_btn)

            # 创建输出文本框
            output_text = QTextEdit()
            output_text.setReadOnly(True)
            font = QFont()
            font.setFamily("SimHei")
            output_text.setFont(font)

            # 将按钮布局和输出文本框添加到垂直布局
            tab_layout.addLayout(button_layout)
            tab_layout.addWidget(output_text)

            # 添加tab
            tab_index = self.tabWidget.addTab(tab_widget, app.name)
            self.app_tabs[app_id] = tab_widget  # 存储整个widget
            self.output_widgets[app_id] = output_text  # 存储输出文本框
            self.tabWidget.setCurrentIndex(tab_index)

            # 连接按钮信号
            restart_btn.clicked.connect(lambda: self.restart_app(app_id))
            close_btn.clicked.connect(lambda: self.stop_app_by_id(app_id))

        # 获取应用路径
        app_path = app.path
        if not os.path.exists(app_path):
            QMessageBox.critical(self, "错误", f"应用路径不存在: {app_path}")
            return

        # 规范化应用路径
        app_path = os.path.normpath(app_path)
        app_path = os.path.abspath(app_path)

        # 迁移旧配置
        old_section = f"{app.name} (ID: {app.id})"
        sanitized_path = app_path
        if self.config.has_section(old_section) and not self.config.has_section(sanitized_path):
            # 创建新section
            self.config.add_section(sanitized_path)
            # 复制设置
            for key, value in self.config.items(old_section):
                self.config.set(sanitized_path, key, value)
            # 删除旧section
            self.config.remove_section(old_section)
            # 保存配置文件
            try:
                with open(app_settings_ini_path, 'w') as f:
                    self.config.write(f)
                self.logger.info(f"迁移设置从旧section '{old_section}' 到新section '{sanitized_path}'")
            except Exception as e:
                self.logger.error(f"迁移设置失败: {str(e)}")

        # 加载应用设置
        settings = self.app_settings.get(app.id, {})
        arguments = settings.get('args', '')
        cwd = settings.get('cwd', '')

        # 处理工作目录
        if cwd and os.path.isdir(cwd):
            working_dir = cwd
        else:
            working_dir = os.path.dirname(app_path) or os.getcwd()

        # 格式化参数
        formatted_args = arguments.format(app_path=app_path, app_id=app_id, app_name=app.name)

        # 构建命令
        # 使用全局Python解释器路径
        app_python_path = settings.get('python_path', '').strip()
        # 增强Python路径获取逻辑，确保正确使用应用设置的解释器路径
        app_python_path = app_python_path.strip() if app_python_path else None
        global_python_path = self.global_settings.get('python_path', '').strip()
        python_path = app_python_path if app_python_path else (global_python_path if global_python_path else sys.executable)
        command = [python_path, app_path] + shlex.split(formatted_args)

        # 启动应用进程
        try:
            process = subprocess.Popen(
                command,
                cwd=working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            self.app_processes[app_id] = process

            # 更新tab标题显示PID
            self.tabWidget.setTabText(tab_index, f"{app.name} (PID: {process.pid})")

            # 创建输出阅读器
            reader = ProcessOutputReader(process)
            reader.output_received.connect(lambda text: self.update_output(app_id, text))
            reader.start()

            # 连接进程完成信号
            output_reader = ProcessOutputReader(process)
            output_reader.finished.connect(
                lambda pid=process.pid, app_path=app.path: self.on_process_finished(pid, app_path))
            output_reader.output_received.connect(lambda text: self.update_output(app_id, text))
            self.logger.info(f"启动应用: {app.name}, PID: {process.pid}")
        except Exception as e:
            QMessageBox.critical(self, "启动失败", f"无法启动应用: {str(e)}")
            self.logger.error(f"启动应用失败: {str(e)}")
            if app_id in self.app_tabs:
                tab_index = self.tabWidget.indexOf(self.app_tabs[app_id])
                self.tabWidget.removeTab(tab_index)
                del self.app_tabs[app_id]
                del self.output_widgets[app_id]

    def show_about_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('关于作者')
        # 如果屏幕大于2k，设置dialog大小
        if self.screen().size().height() > 2000:
            dialog.setMinimumSize(500, 1000)
        else:
            dialog.setMinimumSize(350, 500)

        layout = QVBoxLayout()

        # 作者图片
        pixmap = QtGui.QPixmap(':images/author.jpg')
        # 调整图片大小保持比例
        scaled_pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image_label = QLabel()
        image_label.setPixmap(scaled_pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(image_label)

        # 作者信息
        info_text = '''<h3>关于作者</h3>
    <p><strong>作者笔名：</strong>龙翔</p>
    <p>作者从2021年开始深耕跨境电商领域ERP、办公自动化开发多年，构建了社区开发团队，如果你感兴趣，欢迎前来咨询</p>
    <p>期望各位开发者多多指点，如果有业务需要合作，也请与我们联系。</p>
    '''
        info_browser = QTextBrowser()
        info_browser.setHtml(info_text)
        layout.addWidget(info_browser)

        # 项目地址和社区地址 - 使用PyQt5组件
        link_layout = QVBoxLayout()

        # 项目地址
        project_layout = QHBoxLayout()
        project_label = QLabel('<strong>项目地址：</strong>')
        project_button = QPushButton('打开项目')
        project_button.setStyleSheet('background-color: #007bff; color: white; border-radius: 3px; padding: 5px 10px;')
        project_button.clicked.connect(lambda: QtGui.QDesktopServices.openUrl(QUrl('https://github.com/NelsonLongxiang/py-app-pilot')))
        project_layout.addWidget(project_label)
        project_layout.addWidget(project_button)
        project_layout.addStretch()
        link_layout.addLayout(project_layout)

        # 社区地址
        community_layout = QHBoxLayout()
        community_label = QLabel('<strong>社区地址：</strong>')
        community_button = QPushButton('访问社区')
        community_button.setStyleSheet('background-color: #007bff; color: white; border-radius: 3px; padding: 5px 10px;')
        community_button.clicked.connect(lambda: QtGui.QDesktopServices.openUrl(QUrl('https://lifesa.cn')))
        community_layout.addWidget(community_label)
        community_layout.addWidget(community_button)
        community_layout.addStretch()
        link_layout.addLayout(community_layout)

        layout.addLayout(link_layout)

        # 确定按钮
        ok_button = QPushButton('确定')
        ok_button.clicked.connect(dialog.accept)
        layout.addWidget(ok_button, alignment=Qt.AlignCenter)
        # 禁止移动
        dialog.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        dialog.setLayout(layout)
        dialog.exec_()


if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    # 设置DPI 300
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    # 设置全局字体大小为14
    font = QFont()
    font.setPointSize(12)
    font.setFamily("SimHei")
    app.setFont(font)
    window = PythonAppManager()
    window.show()
    sys.exit(app.exec_())


// ... existing code ...
        # 初始化应用列表（改为树形结构支持分组）
        self.app_tree = QTreeWidget()
        self.app_tree.setHeaderLabel("应用列表")
        self.app_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.app_tree.customContextMenuRequested.connect(self.show_app_context_menu)
        layout.addWidget(self.app_tree)

        # 加载应用数据并分组显示
        self.load_and_group_apps()

    def load_apps(self):
        """加载应用数据"""
        apps = self.app_data_manager.get_all_apps()
        for app in apps:
            item = QListWidgetItem(f"{app.name} (ID: {app.id})")
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, app.id)
            self.app_list.addItem(item)
            # 存储应用ID作为item的数据
            self.app_list.item(self.app_list.count() - 1).setData(Qt.UserRole, app.id)

    def add_app(self):
        """添加新应用"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择Python应用", "", "Python Files (*.py);;All Files (*)"
        )
        if file_path:
            # 获取文件名作为应用名称
            app_name = os.path.splitext(os.path.basename(file_path))[0]
            # 规范化路径
            file_path = os.path.normpath(file_path)
            file_path = os.path.abspath(file_path)
            # 检查路径是否包含空格
            if ' ' in file_path:
                QMessageBox.warning(self, "警告", "应用路径不能包含空格")
                return
            # 添加到数据库
            app = self.app_data_manager.add_app(
                name=app_name,
                path=file_path,
                arguments=self.args_input.text(),
                working_directory=self.cwd_input.text()
            )
            app = self.app_data_manager.get_app_by_id(app.id)
            # 添加到列表
            # 显式创建列表项以确保item不为None
            # 可勾选
            item = QListWidgetItem(f"{app.name} ({app.id})")
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, app.id)
            self.app_list.addItem(item)
            self.app_list.setCurrentItem(item)
            # 初始化新应用配置
            section_name = str(app.id)
            if not self.config.has_section(section_name):
                self.config.add_section(section_name)
            self.config.set(section_name, 'args', '')
            self.config.set(section_name, 'cwd', '')
            with open(app_settings_ini_path, 'w') as f:
                self.config.write(f)
            self.save_app_settings()
            QMessageBox.information(self, "成功", f"应用 '{app.name}' 添加成功")
            self.logger.info(f"Added application: {app_name} ({file_path})")

    def remove_app(self):
        current_item = self.app_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请选择要删除的应用")
            return

        app_id = current_item.data(Qt.UserRole)
        current_app = self.app_data_manager.get_app_by_id(app_id)
        if not current_app:
            QMessageBox.warning(self, "警告", "无法获取应用路径")
            return

        # 检查应用是否正在运行
        if app_id in self.app_processes:
            QMessageBox.warning(self, "警告", "应用正在运行，无法删除")
            return

        # 二次确认删除
        reply = QMessageBox.question(self, "确认删除", "确定要删除此应用吗？此操作不可恢复。",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

            # 从数据库中删除应用
            try:
                self.app_data_manager.delete_app(current_app.id)
                # 删除对应的配置
                section_name = str(current_app.id)
                if self.config.has_section(section_name):
                    self.config.remove_section(section_name)
                    with open(app_settings_ini_path, 'w') as f:
                        self.config.write(f)
                # 从应用设置中移除
                if current_app.id in self.app_settings:
                    del self.app_settings[current_app.id]
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除应用失败: {str(e)}")
                self.logger.error(f"删除应用失败 {current_app.name}: {str(e)}")
                return
        # 清理相关资源
        if app_id in self.app_tabs:
            del self.app_tabs[app_id]
        if app_id in self.output_widgets:
            del self.output_widgets[app_id]
        # 从列表中移除
        # 使用takeItem而非removeItemWidget，确保从列表模型中彻底移除项
        index = self.app_list.row(current_item)
        self.app_list.takeItem(index)
        # 刷新应用列表
        self.load_apps_from_database()
        # 只显示文件名而非完整路径，提升用户体验
        app_name = current_app.name
        QMessageBox.information(self, "成功", f"应用 '{app_name}' 删除成功")
        self.logger.info(f"已删除应用: {app_name}")

    def on_process_finished(self, pid, app_id):
        """应用进程结束时的处理"""
        if app_id in self.app_processes:
            del self.app_processes[app_id]
            del self.output_readers[app_id]

        # 更新数据库中所有应用的运行状态
        for i in range(self.app_list.count()):
            item =
