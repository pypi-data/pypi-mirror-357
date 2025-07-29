import select
import sys
import os
import subprocess
import shlex
from typing import Dict, Any, Optional

from PyQt5 import QtCore

from .utils.log_util import logger
import psutil


import platform
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QTextEdit, QTreeWidget,
    QTreeWidgetItem, QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QMessageBox, QFileDialog, QMenu, QAction, QDialog, QTextBrowser, QInputDialog, QComboBox,
    QCheckBox, QStyledItemDelegate
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject, QTimer, QCoreApplication, QUrl, QSize
from PyQt5.QtGui import QFont
from .utils.database import AppDataManager
from .utils.log_util import logger
from .utils.eunm import app_manager_log_path
from .resources import logo_rc, author_rc
import PyQt5.QtGui as QtGui


import datetime

class ProcessOutputReader(QThread):
    output_received = pyqtSignal(int, str)
    error_occurred = pyqtSignal(str)

    def __init__(self, process, app_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.process = process
        self.app_id = app_id
        self.running = True

    def run(self):
        while self.running and self.process.poll() is None:
            try:
                output = self.process.stdout.readline()
                if output:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.output_received.emit(self.app_id, f"[{timestamp}] {output.strip()}")
            except Exception as e:
                self.error_occurred.emit(f"读取输出失败: {str(e)}")
                break
        
        if self.running:
            try:
                remaining = self.process.stdout.read()
                if remaining:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.output_received.emit(self.app_id, f"[{timestamp}] {remaining.strip()}")
            except Exception as e:
                self.error_occurred.emit(f"读取剩余输出失败: {str(e)}")

    def stop(self):
        self.running = False


class ConfigManager(QObject):
    setting_changed = pyqtSignal(str, str)  # key, value
    _instance: Optional['ConfigManager'] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        super().__init__()
        if hasattr(self, 'initialized'):
            return
        self.app_data_manager = AppDataManager()
        self._cache: Dict[str, Any] = {}
        self._default_settings = {
            'Global': {
                'python_path': sys.executable,
                'log_level': 'INFO',
                'auto_start': 'false'
            }
        }
        self.logger = logger
        self._initialize_default_settings()
        self.initialized = True

    def _initialize_default_settings(self) -> None:
        """初始化默认配置，确保关键配置项存在"""
        for section, settings in self._default_settings.items():
            for key, default_value in settings.items():
                # 检查配置是否存在，不存在则设置默认值
                current_value = self.get_setting(section, key)
                if current_value is None:
                    self.save_setting(section, key, default_value)
                    self.logger.info(f"初始化默认配置: {section}.{key} = {default_value}")

    @classmethod
    def get_instance(cls) -> 'ConfigManager':
        if cls._instance is None:
            cls._instance = ConfigManager()
        return cls._instance

    def get_setting(self, section: str, key: str, default: Any = None) -> Any:
        """获取指定节的配置，优先使用缓存"""
        cache_key = f"{section}.{key}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        value = self.app_data_manager.get_global_setting(key, default)
        self._cache[cache_key] = value
        self.logger.debug(f"Loaded setting: {section}.{key} = {value}")
        return value

    def save_setting(self, section: str, key: str, value: Any) -> bool:
        """保存指定节的配置并更新缓存"""
        try:
            # 验证配置值有效性
            if not self._validate_setting(key, value):
                self.logger.error(f"Invalid value for setting {section}.{key}: {value}")
                return False
            self.app_data_manager.save_global_setting(key, value)
            cache_key = f"{section}.{key}"
            self._cache[cache_key] = value
            self.setting_changed.emit(f"{section}.{key}", value)
            self.logger.info(f"Saved setting: {section}.{key} = {value}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save setting {section}.{key}: {str(e)}", exc_info=True)
            return False

    def _validate_setting(self, key: str, value: Any) -> bool:
        """验证配置项值的有效性"""
        if key == 'log_level':
            return value in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        elif key == 'auto_start':
            return str(value).lower() in ['true', 'false']
        elif key == 'python_path':
            return os.path.exists(value) and os.path.isfile(value) and os.access(value, os.X_OK)
        return True

    def validate_config(self) -> bool:
        """验证所有配置项的完整性和有效性"""
        valid = True
        for section, settings in self._default_settings.items():
            for key in settings:
                value = self.get_setting(section, key)
                if not self._validate_setting(key, value):
                    default_value = self._default_settings[section][key]
                    self.logger.warning(f"Invalid {section}.{key} setting '{value}', using default: {default_value}")
                    self.save_setting(section, key, default_value)
                    valid = False
        return valid


class ProcessFinishedSignal(QObject):
    finished = pyqtSignal(int, str)  # 参数：进程PID，应用路径

class MinimumSizeDelegate(QStyledItemDelegate):
    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        return QtCore.QSize(max(size.width(), 30), max(size.height(), 30))

class PythonAppManager(QMainWindow):
    def __init__(self):
        super().__init__()
        # 设置全局暗色调样式
        self.setStyleSheet(
                           "QMainWindow, QWidget {background-color: #2d2d2d; color: #ffffff;}"
                           "QPushButton {background-color: #4a4a4a; color: white; border: 1px solid #666; border-radius: 4px; padding: 5px 10px;}"
                           "QPushButton:hover {background-color: #5a5a5a;}"
                           "QPushButton:pressed {background-color: #3a3a3a;}"
                           "QTreeWidget {background-color: #3d3d3d; border: 1px solid #555; border-radius: 4px;}"
                           "QTreeWidget::item {padding: 5px; border-bottom: 1px solid #444; min-height: 30px; min-width: 30px;}"
                           "QTreeWidget::section {background-color: #FFA500; color: black; font-weight: bold;}"
                           "QTreeWidget::item:selected {background-color: #5a5a5a; color: white;}"
                           "QTreeWidget::indicator {width: 30px; height: 30px;}"
                           "QTreeWidget::indicator:unchecked {image: url(:images/unchecked.png);}"
                           "QTreeWidget::indicator:checked {image: url(:images/checked.png);}"
                           "QTabWidget::pane {border: 1px solid #555; background-color: #2d2d2d;}"
                           "QHeaderView::section {background-color: #FFA500; color: black; font-weight: bold;}"
                           "QTabBar::tab {background-color: #3d3d3d; color: white; padding: 8px 16px; border: 1px solid #555; border-bottom-color: #555; border-top-left-radius: 4px; border-top-right-radius: 4px;}"
                           "QTabBar::tab:selected {background-color: #2d2d2d; border-bottom-color: #2d2d2d;}"
                           "QTabBar::tab:hover:!selected {background-color: #4a4a4a;}"
                           "QLineEdit, QTextEdit {background-color: #3d3d3d; color: white; border: 1px solid #555; border-radius: 4px; padding: 5px;}"
                           "QLabel {color: #ffffff;}"

                           )
        self.app_data_manager = AppDataManager()
        self.processes = {}
        self.global_settings = {}

        self.logger = logger
        self.config_manager = ConfigManager.get_instance()
        self.config_manager.setting_changed.connect(self.on_setting_changed)
        # 验证配置完整性
        if not self.config_manager.validate_config():
            self.logger.warning("部分配置无效，已自动使用默认值")
        self.statusBar().showMessage("部分配置无效，已自动使用默认值", 5000)
        self.init_ui()
        self.app_tree.setItemDelegate(MinimumSizeDelegate())
        self.app_processes = {}
        self.output_readers = {}
        self.app_tabs = {}
        self.output_widgets = {}
        self.process_finished_signals = {}  # 新增：跟踪应用对应的tab索引

        self.load_apps_from_database()

    def init_ui(self) -> None:
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



    def init_app_management_ui(self) -> None:
        # 创建主横向布局
        main_layout = QHBoxLayout()

        # 左侧应用列表和操作按钮区域
        left_layout = QVBoxLayout()

        # 分组管理控件
        group_layout = QHBoxLayout()
        self.group_label = QLabel("分组名称:")
        self.group_name_edit = QLineEdit()
        self.save_group_btn = QPushButton("保存分组")
        group_layout.addWidget(self.group_label)
        group_layout.addWidget(self.group_name_edit)
        group_layout.addWidget(self.save_group_btn)
        left_layout.addLayout(group_layout)

        # 应用列表
        self.app_tree = QTreeWidget()
        self.app_tree.setHeaderLabel("应用列表")
        self.app_tree.itemSelectionChanged.connect(self.on_app_selected)
        self.app_tree.itemSelectionChanged.connect(self.update_group_edit)
        self.save_group_btn.clicked.connect(self.save_group_name)
        left_layout.addWidget(self.app_tree)

        # 增加右键菜单 全选和取消全选
        self.app_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.app_tree.customContextMenuRequested.connect(self.show_context_menu)

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

    def init_log_viewer_ui(self) -> None:
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

    def _get_or_create_group(self, group_name):
        # 查找现有分组
        for i in range(self.app_tree.topLevelItemCount()):
            item = self.app_tree.topLevelItem(i)
            if item.text(0) == group_name:
                return item
        # 创建新分组
        group_item = QTreeWidgetItem([group_name])
        group_item.setFlags(group_item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
        group_item.setCheckState(0, Qt.Unchecked)
        self.app_tree.addTopLevelItem(group_item)
        return group_item

    def init_system_management_ui(self) -> None:
        layout = QVBoxLayout()
        self.system_info_label = QLabel()
        self.system_info_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        # 全局设置区域
        global_settings_group = QGroupBox("全局设置")
        global_settings_form = QFormLayout()

        # Python路径设置
        self.global_python_path_input = QLineEdit()
        self.browse_global_python_btn = QPushButton("浏览...")
        self.browse_global_python_btn.clicked.connect(self.browse_global_python_path)
        python_path_layout = QHBoxLayout()
        python_path_layout.addWidget(self.global_python_path_input)
        python_path_layout.addWidget(self.browse_global_python_btn)
        global_settings_form.addRow("Python解释器路径:", python_path_layout)

        # 日志级别设置
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        global_settings_form.addRow("日志级别:", self.log_level_combo)

        # 自动启动设置
        self.auto_start_check = QCheckBox()
        global_settings_form.addRow("启动时自动运行应用:", self.auto_start_check)

        # 保存按钮
        self.save_global_btn = QPushButton("保存全局设置")
        self.save_global_btn.clicked.connect(self.save_global_settings)
        global_settings_form.addRow(self.save_global_btn)

        global_settings_group.setLayout(global_settings_form)

        # 获取系统信息
        system_info = self.get_system_info()
        self.system_info_label.setText(f"系统信息:\n{system_info}")

        layout.addWidget(global_settings_group)
        layout.addWidget(self.system_info_label)
        self.system_management_widget.setLayout(layout)

        # 从数据库加载全局配置
        python_path = self.config_manager.get_setting('Global', 'python_path', sys.executable)
        self.global_python_path_input.setText(python_path)
        self.global_settings['python_path'] = python_path

        log_level = self.config_manager.get_setting('Global', 'log_level', 'INFO')
        self.log_level_combo.setCurrentText(log_level)

        auto_start = self.config_manager.get_setting('Global', 'auto_start', 'false').lower() == 'true'
        self.auto_start_check.setChecked(auto_start)

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

    def get_memory_usage(self) -> str:
        """获取内存使用情况"""
        mem = psutil.virtual_memory()
        total = self.format_bytes(mem.total)
        available = self.format_bytes(mem.available)
        used = self.format_bytes(mem.used)
        percent = mem.percent
        return f"总计: {total}, 可用: {available}, 已用: {used} ({percent}%)"

    def format_bytes(self, bytes: int, decimals: int = 2) -> str:
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

    def show_context_menu(self, pos: QtCore.QPoint) -> None:
        menu = QMenu(self)
        select_all_action = menu.addAction("全选")
        deselect_all_action = menu.addAction("取消全选")
        action = menu.exec_(self.app_tree.mapToGlobal(pos))

        if action == select_all_action:
            for i in range(self.app_tree.topLevelItemCount()):
                group_item = self.app_tree.topLevelItem(i)
                for j in range(group_item.childCount()):
                    child_item = group_item.child(j)
                    child_item.setCheckState(0, Qt.Checked)
        elif action == deselect_all_action:
            for i in range(self.app_tree.topLevelItemCount()):
                group_item = self.app_tree.topLevelItem(i)
                for j in range(group_item.childCount()):
                    child_item = group_item.child(j)
                    child_item.setCheckState(0, Qt.Unchecked)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        # 应用未关闭完之前，不允许关闭窗口
        if self.app_processes:
            self.logger.warning("请先关闭所有运行中的应用")
            self.statusBar().showMessage("请先关闭所有运行中的应用", 5000)
            event.ignore()
            return
        super().closeEvent(event)



    def browse_python_path(self) -> None:
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
        """保存全局设置到数据库"""
        try:
            # 保存Python路径
            new_path = self.global_python_path_input.text().strip() or sys.executable
            self.config_manager.save_setting('Global', 'python_path', new_path)
            self.global_settings['python_path'] = new_path

            # 保存日志级别
            log_level = self.log_level_combo.currentText()
            self.config_manager.save_setting('Global', 'log_level', log_level)

            # 保存自动启动设置
            auto_start = self.auto_start_check.isChecked()
            self.config_manager.save_setting('Global', 'auto_start', 'true' if auto_start else 'false')

            self.logger.info("全局设置已保存")
            self.logger.info("全局设置已保存")
            self.statusBar().showMessage("全局设置已保存", 5000)
        except Exception as e:
            self.logger.error(f"保存全局设置失败: {str(e)}")
            self.statusBar().showMessage(f"保存全局设置失败: {str(e)}", 5000)

    def save_app_settings(self):
        current_item = self.app_tree.currentItem()
        if not current_item or current_item.parent() is None:
            self.logger.warning("请选择一个应用")
            self.statusBar().showMessage("请选择一个应用", 5000)
            return
        if not current_item:
            return

        current_item = self.app_tree.currentItem()
        if not current_item:
            self.logger.warning("请先选择一个应用")
            self.statusBar().showMessage("请先选择一个应用", 5000)
            return
        current_item = self.app_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择一个应用")
            return
        app_id = current_item.data(0, Qt.UserRole)
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

        # 保存到配置文件
        # 更新应用名称
        new_name = self.name_input.text().strip()
        if new_name and new_name != app.name:
            self.app_data_manager.update_app(app_id, name=new_name)
            # 更新列表项显示
            current_item.setText(0,f"{new_name} (ID: {app_id})")
            app.name = new_name

        try:
            # 同步更新到数据库
            app = self.app_data_manager.get_app_by_id(app_id)
            if app:
                self.app_data_manager.update_app(app_id, python_path=self.python_path_input.text(), arguments=args, working_directory=cwd)
            self.logger.info(f"应用设置已保存: {app_id}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存应用设置失败: {str(e)}")
            self.logger.error(f"保存应用设置失败: {str(e)}")

        # 同时保存全局Python路径
        self.save_global_settings()

    def update_group_edit(self):
        selected_items = self.app_tree.selectedItems()
        if selected_items:
            current_item = selected_items[0]
            # 检查是否为分组项（没有父项且有子项）
            if not current_item.parent() and current_item.childCount() > 0:
                self.group_name_edit.setText(current_item.text(0))
            else:
                # 如果选择的是应用项，获取其父分组
                parent = current_item.parent()
                if parent:
                    self.group_name_edit.setText(parent.text(0))
                else:
                    self.group_name_edit.clear()
        else:
            self.group_name_edit.clear()

    def save_group_name(self):
        selected_items = self.app_tree.selectedItems()
        if selected_items and self.group_name_edit.text().strip():
            current_item = selected_items[0]
            new_name = self.group_name_edit.text().strip()
            # 处理分组项
            if not current_item.parent() and current_item.childCount() > 0:
                old_name = current_item.text(0)
                current_item.setText(0, new_name)
                # 更新数据库中的分组名称
                self.app_data_manager.update_group_name(old_name, new_name)
            else:
                # 处理应用项的父分组
                parent = current_item.parent()
                if parent:
                    old_name = parent.text(0)
                    parent.setText(0, new_name)
                    self.app_data_manager.update_group_name(old_name, new_name)

    def on_app_selected(self):
        current_item = self.app_tree.currentItem()
        if current_item and current_item.parent() is not None:  # 确保选择的是应用项而非组
            app_id = current_item.data(0, Qt.UserRole)
            app = self.app_data_manager.get_app_by_id(app_id)
            if not app:
                return
            app_path = app.path.strip('" ').strip()
            app_path = os.path.normpath(app_path)
            app_path = os.path.abspath(app_path)
            self.settings_group.setEnabled(True)
            # 加载应用设置并替换参数占位符
            self.load_settings()

            # 重新加载设置
            self.load_settings()
            # 使用应用对象设置UI控件
            self.name_input.setText(app.name)
            self.args_input.setText(app.arguments)
            self.cwd_input.setText(app.working_directory)
            self.python_path_input.setText(app.python_path or '')
            # 连接编辑完成信号到保存方法
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
        """从数据库加载应用列表到树形结构"""
        self.app_tree.clear()
        apps = self.app_data_manager.get_all_apps()
        
        # 创建默认组
        default_group = QTreeWidgetItem(['默认组'])
        default_group.setFlags(default_group.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
        # 创建分组字典
        groups = {}
        
        for app in apps:
            # 获取应用分组，默认为"默认组"
            group_name = app.group.strip() if hasattr(app, 'group') and app.group else "默认组"
            
            # 如果分组不存在则创建
            if group_name not in groups:
                group_item = QTreeWidgetItem([group_name])
                group_item.setFlags(group_item.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
                # 增大分组项尺寸
                group_item.setSizeHint(0, QSize(0, 35))  # 设置分组项高度为35px
                self.app_tree.addTopLevelItem(group_item)
                groups[group_name] = group_item
            
            # 创建应用子项并添加到对应分组
            item = QTreeWidgetItem([f"{app.name} (ID: {app.id})"])

            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(0, Qt.Unchecked)
            item.setData(0, Qt.UserRole, app.id)
            groups[group_name].addChild(item)

    def add_app(self):
        """添加新应用"""
        # 获取分组名称，默认为"默认组"
        group, ok = QInputDialog.getText(self, "应用分组", "请输入分组名称:", text="默认组")
        if not ok or not group.strip():  # 确保分组名称有效
            group = "默认组"
        group = group.strip()
        
        # 选择应用文件
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
                working_directory=self.cwd_input.text(),
                group=group
            )
            app = self.app_data_manager.get_app_by_id(app.id)
            # 添加到列表
            # 显式创建列表项以确保item不为None
            # 可勾选
            # 获取或创建默认组
            # 获取或创建分组
            group_item = self._get_or_create_group(group)
            
            # 创建应用子项
            item = QTreeWidgetItem([f"{app.name} ({app.id})"])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(0, Qt.Unchecked)
            item.setData(0, Qt.UserRole, app.id)
            group_item.addChild(item)
            self.app_tree.setCurrentItem(item)
            self.app_tree.expandItem(group_item)
            # 初始化新应用配置
            # 初始化新应用配置到数据库
            self.app_data_manager.update_app(
                app_id=app.id,
                arguments='',
                working_directory=''
            )
            QMessageBox.information(self, "成功", f"应用 '{app.name}' 添加成功")
            self.logger.info(f"Added application: {app_name} ({file_path})")

    def remove_app(self):
        current_item = self.app_tree.currentItem()
        if current_item and current_item.parent() is None: current_item = None
        if not current_item:
            QMessageBox.warning(self, "警告", "请选择要删除的应用")
            return

        app_id = current_item.data(0, Qt.UserRole)
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
                # 通过数据库删除应用配置
                self.app_data_manager.delete_app_settings(current_app.id)

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
        parent = current_item.parent()
        if parent:
            parent.removeChild(current_item)
            # 如果组为空则删除组
            if parent.childCount() == 0:
                top_level_index = self.app_tree.indexOfTopLevelItem(parent)
                self.app_tree.takeTopLevelItem(top_level_index)
        # 刷新应用列表
        self.load_apps_from_database()
        # 只显示文件名而非完整路径，提升用户体验
        app_name = current_app.name
        self.logger.info(f"应用 '{app_name}' 删除成功")
        self.statusBar().showMessage(f"应用 '{app_name}' 删除成功", 5000)
        self.logger.info(f"已删除应用: {app_name}")

    def on_process_finished(self, pid, app_id):
        """应用进程结束时的处理"""
        if app_id in self.app_processes:
            del self.app_processes[app_id]
            del self.output_readers[app_id]

        # 更新数据库中所有应用的运行状态
        for i in range(self.app_tree.topLevelItemCount()):
            group = self.app_tree.topLevelItem(i)
            for j in range(group.childCount()):
                item = group.child(j)
                item_app_id = item.data(0, Qt.UserRole)
            app = self.app_data_manager.get_app_by_id(item_app_id)
            if app and app.id == app_id:
                self.app_data_manager.update_app_status(app_id, False)
                break

        self.logger.info(f"Application process finished: {app_id}")

    def stop_app(self, current_item=None):
        if not current_item:
            for i in range(self.app_tree.topLevelItemCount()):
                group = self.app_tree.topLevelItem(i)
                for j in range(group.childCount()):
                    item = group.child(j)
                    if item.checkState(0) == Qt.Checked:
                        self.stop_app(item)
            return
        reply = QMessageBox.question(self, "确认关闭", "确定要关闭[{0}]应用吗？ ".format(current_item.text(0)),
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        if current_item:
            self.stop_app_by_id(current_item.data(0, Qt.UserRole))

    def _cleanup_ui_resources(self, app_id):
        """清理应用相关的UI资源"""
        # if app_id in self.app_tabs:
        self.tabWidget.removeTab(self.tabWidget.indexOf(self.app_tabs[app_id]))
        del self.app_tabs[app_id]
        # if app_id in self.output_widgets:
        del self.output_widgets[app_id]
        # if app_id in self.app_processes:
        del self.app_processes[app_id]

    def on_item_changed(self, item, column):
        if column != 0:
            return
        
        # 处理分组项选中状态变化
        if not item.parent():  # 顶层项目（分组）
            check_state = item.checkState(0)
            for i in range(item.childCount()):
                child = item.child(i)
                child.setCheckState(0, check_state)
        else:  # 子项
            parent = item.parent()
            child_count = parent.childCount()
            checked_count = 0
            for i in range(child_count):
                if parent.child(i).checkState(0) == Qt.Checked:
                    checked_count += 1
            
            if checked_count == 0:
                parent.setCheckState(0, Qt.Unchecked)
            elif checked_count == child_count:
                parent.setCheckState(0, Qt.Checked)
            else:
                parent.setCheckState(0, Qt.PartiallyChecked)

    def stop_app_by_id(self, app_id):
        self.logger.info(f"Stopping application: {app_id} {self.app_processes}")
        if app_id in self.app_processes:
            app_name = self.app_data_manager.get_app_by_id(app_id).name
            self.logger.info(f"关闭应用 '{app_name}'")

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

                # 停止输出读取线程
                if app_id in self.output_readers:
                    self.output_readers[app_id].stop()
                    self.output_readers[app_id].wait()
                    del self.output_readers[app_id]

                # 进程成功终止，清理UI资源
                self._cleanup_ui_resources(app_id)
                self.logger.info(f"关闭应用: {app_name}")
                self.statusBar().showMessage(f"关闭应用成功: {app_name}", 5000)

            except psutil.NoSuchProcess:
                self.logger.warning(f"进程 {process_info.pid} 已不存在")
                self._cleanup_ui_resources(app_id)
                self.statusBar().showMessage(f"应用已关闭: {app_name}", 5000)
            except Exception as e:
                self.logger.error(f"关闭应用失败: {str(e)}")
                self.statusBar().showMessage(f"关闭应用失败: {str(e)}", 5000)
        else:
            self.logger.warning(f"应用未运行: {app_id}")
            self.statusBar().showMessage(f"应用未运行: {app_id}", 5000)

    def restart_app(self, app_id):
        """重启应用"""
        self.logger.info(f"Restarting application: {app_id}")
        # 先停止应用
        self.stop_app_by_id(app_id)
        # 查找应用列表项并重新启动
        for i in range(self.app_tree.topLevelItemCount()):
            group = self.app_tree.topLevelItem(i)
            for j in range(group.childCount()):
                item = group.child(j)
                if item.data(0, Qt.UserRole) == app_id:
                    # 延迟启动以确保进程已终止
                    QTimer.singleShot(1000, lambda item=item: self.start_app())
                    break

    def update_output(self, app_id, text):
        """更新指定应用Tab页中的输出内容"""
        if app_id in self.output_widgets:
            self.output_widgets[app_id].append(text)

    def load_app_settings(self, app_id):
        """从数据库加载应用配置"""
        return self.app_data_manager.get_app_settings(app_id)

    def load_settings(self):
        """从数据库加载应用设置并更新UI控件"""
        current_item = self.app_tree.currentItem()
        if current_item and current_item.parent() is not None:
            app_id = current_item.data(0, Qt.UserRole)
            app_settings = self.app_data_manager.get_app_settings(app_id)
            self.name_input.setText(app_settings.get('name', ''))
            self.args_input.setText(app_settings.get('arguments', ''))
        
        

    def _create_app_tab(self, app) -> QTextEdit:
        """创建应用专属Tab页并返回输出控件"""
        app_id = app.id
        app_name = app.name
        
        # 创建Tab页部件
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
        output_text.setStyleSheet("background-color: #1E1E1E; color: #FFFFFF;")

        # 将按钮布局和输出文本框添加到垂直布局
        tab_layout.addLayout(button_layout)
        tab_layout.addWidget(output_text)

        # 添加tab
        tab_index = self.tabWidget.addTab(tab_widget, app_name)
        self.app_tabs[app_id] = tab_widget  # 存储整个widget
        self.output_widgets[app_id] = output_text  # 存储输出文本框
        self.tabWidget.setCurrentIndex(tab_index)

        # 连接按钮信号
        restart_btn.clicked.connect(lambda: self.restart_app(app_id))
        close_btn.clicked.connect(lambda: self.stop_app_by_id(app_id))

        return output_text

    def _start_app_process(self, app):
        """启动应用进程并处理相关逻辑"""
        app_id = app.id
        app_name = app.name

        # 获取应用路径
        app_path = app.path
        if not os.path.exists(app_path):
            self.logger.error(f"应用路径不存在: {app_path}")
            self.statusBar().showMessage(f"应用路径不存在: {app_path}", 5000)
            return None

        # 规范化应用路径
        app_path = os.path.normpath(app_path)
        app_path = os.path.abspath(app_path)

        # 迁移旧配置
        old_section = f"{app.name} (ID: {app.id})"
        sanitized_path = app_path
        # 使用数据库更新分组名称
        self.app_data_manager.update_group_name(old_section, sanitized_path)

        # 加载应用设置
        app_settings = self.app_data_manager.get_app_settings(app_id)
        args = app.arguments
        cwd = app.working_directory

        # 处理工作目录
        if cwd and os.path.isdir(cwd):
            working_dir = cwd
        else:
            working_dir = os.path.dirname(app_path) or os.getcwd()

        # 格式化参数
        formatted_args = app.arguments.format(app_path=app_path, app_id=app_id, app_name=app.name)

        # 获取Python解释器路径
        python_path = self._get_python_path(app)
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
            tab_index = self.tabWidget.indexOf(self.app_tabs[app_id])
            self.tabWidget.setTabText(tab_index, f"{app.name} (PID: {process.pid})")

            # 启动线程捕获输出
            self._start_output_capture(process, app_id)

            self.logger.info(f"启动应用: {app.name}, PID: {process.pid}")
            return process
        except Exception as e:
            self.logger.error(f"无法启动应用: {str(e)}")
            self.statusBar().showMessage(f"无法启动应用: {str(e)}", 5000)
            if app_id in self.app_tabs:
                tab_index = self.tabWidget.indexOf(self.app_tabs[app_id])
                self.tabWidget.removeTab(tab_index)
                del self.app_tabs[app_id]
                del self.output_widgets[app_id]
            return None

    def start_app(self,current_item=None) -> None:
        """启动选中的应用程序"""
        
        if not current_item:
            for i in range(self.app_tree.topLevelItemCount()):
                group = self.app_tree.topLevelItem(i)
                for j in range(group.childCount()):
                    item = group.child(j)
                    if item.checkState(0) == Qt.Checked:
                        self.start_app(item)
            return

        app_id = current_item.data(0, Qt.UserRole)
        app = self.app_data_manager.get_app_by_id(app_id)
        if not app:
            self.logger.warning("应用不存在")
            self.statusBar().showMessage("应用不存在", 5000)
            return

        # 检查应用是否已在运行
        if app_id in self.app_processes and self.app_processes[app_id].poll() is None:
            self.logger.warning(f"应用已在运行: {app.name}")
            # 切换到对应的tab
            if app_id in self.app_tabs:
                tab_index = self.tabWidget.indexOf(self.app_tabs[app_id])
                self.tabWidget.setCurrentIndex(tab_index)
            return

        # 创建应用Tab页
        self._create_app_tab(app)

        # 启动应用进程
        process = self._start_app_process(app)

        # 连接进程完成信号
        if process and app_id not in self.process_finished_signals:
            self.process_finished_signals[app_id] = ProcessFinishedSignal()
            self.process_finished_signals[app_id].finished.connect(
                lambda pid=process.pid, app_path=app.path: self.on_process_finished(pid, app_path))

    def _start_output_capture(self, process, app_id):
        """启动应用输出捕获，将输出重定向到日志和UI"""
        self.output_readers[app_id] = ProcessOutputReader(process, app_id)
        self.output_readers[app_id].output_received.connect(self.update_output)
        self.output_readers[app_id].error_occurred.connect(lambda msg: self.logger.error(msg))
        self.output_readers[app_id].start()

    def _get_python_path(self, app) -> str:
        """获取并验证Python解释器路径，优先使用应用配置"""
        # 优先使用应用设置中的解释器路径
        app_settings = self.app_data_manager.get_app_settings(app.id)
        if app_settings and 'python_path' in app_settings:
            python_path = app_settings['python_path']
            if self._validate_python_path(python_path):
                return python_path
            self.logger.warning(f"应用配置的Python路径 '{python_path}' 无效，将使用全局配置")
        
        # 回退到全局配置
        python_path = self.config_manager.get_setting('Global', 'python_path', sys.executable)
        if self._validate_python_path(python_path):
            return python_path
        
        # 自动修复为系统默认Python
        self.logger.warning(f"全局Python路径 '{python_path}' 无效，已自动使用默认路径")
        python_path = sys.executable
        self.config_manager.save_global_setting('python_path', python_path)
        self.global_python_path_input.setText(python_path)
        return python_path

    def _validate_python_path(self, path: Optional[str] = None) -> bool:
        """验证Python解释器路径有效性"""
        path = path or self.config_manager.get_global_setting('python_path', sys.executable)
        if not path or not os.path.exists(path):
            self.logger.warning(f"Python路径不存在: {path}")
            return False
        if not os.path.isfile(path) or not os.access(path, os.X_OK):
            self.logger.warning(f"Python路径不是可执行文件: {path}")
            return False
        # 验证是否为Python解释器
        try:
            result = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=2)
            if result.returncode != 0:
                self.logger.warning(f"不是有效的Python解释器: {path}")
                return False
            self.logger.debug(f"Python路径验证通过: {path}")
            return True
        except Exception as e:
            self.logger.error(f"验证Python路径失败: {str(e)}")
            return False

    def on_setting_changed(self, key: str, value: Any) -> None:
        """配置变更监听器"""
        if key == 'python_path':
            self.global_python_path_input.setText(value)
            self.logger.info(f"配置已更新: {key} = {value}")
            return
        elif key == 'auto_start':
            # 处理自动启动设置变更
            self.logger.info(f"自动启动设置已更新: {value}")
            return

        # 其他设置变更处理
        current_item = self.app_tree.currentItem()
        if not current_item:
            return
        app_id = current_item.data(0, Qt.UserRole)
        app = self.app_data_manager.get_app_by_id(app_id)
        if not app:
            self.logger.error("应用数据不存在")
            self.statusBar().showMessage("应用数据不存在", 5000)
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
                self.logger.info(f"应用 '{app.name}' 已在运行中，已切换到对应的Tab页面")
                self.statusBar().showMessage(f"应用 '{app.name}' 已在运行中", 5000)
                return
            else:
                # 进程已停止，清空输出并准备重新启动
                if output_text:
                    output_text.clear()

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