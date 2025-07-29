import unittest
import os
import sys
from unittest.mock import Mock, patch
from src.py_app_pilot.py_app_pilot import ConfigManager

class TestConfigManager(unittest.TestCase):
    @patch('src.py_app_pilot.py_app_pilot.AppDataManager')
    def setUp(self, mock_app_data_manager):
        # 确保每次测试都是新的单例实例
        ConfigManager._instance = None
        self.mock_data_manager = mock_app_data_manager.return_value
        self.config_manager = ConfigManager.get_instance()
        self.config_manager.app_data_manager = self.mock_data_manager

    def test_singleton_instance(self):
        """测试ConfigManager是否为单例模式"""
        instance1 = ConfigManager.get_instance()
        instance2 = ConfigManager.get_instance()
        self.assertIs(instance1, instance2)

    def test_get_global_setting_with_cache(self):
        """测试获取全局配置时优先使用缓存"""
        # 设置模拟返回值
        self.mock_data_manager.get_global_setting.return_value = 'test_value'

        # 第一次获取 - 应该从数据管理器获取
        value1 = self.config_manager.get_global_setting('test_key', 'default')
        self.assertEqual(value1, 'test_value')
        self.mock_data_manager.get_global_setting.assert_called_once_with('test_key', 'default')

        # 第二次获取 - 应该从缓存获取
        value2 = self.config_manager.get_global_setting('test_key', 'default')
        self.assertEqual(value2, 'test_value')
        # 确保数据管理器只被调用一次
        self.mock_data_manager.get_global_setting.assert_called_once()

    def test_save_global_setting_updates_cache(self):
        """测试保存全局配置时更新缓存"""
        self.mock_data_manager.save_global_setting.return_value = True

        result = self.config_manager.save_global_setting('test_key', 'new_value')
        self.assertTrue(result)
        self.assertEqual(self.config_manager._cache['test_key'], 'new_value')
        self.mock_data_manager.save_global_setting.assert_called_once_with('test_key', 'new_value')

class TestPythonPathValidation(unittest.TestCase):
    @patch('src.py_app_pilot.py_app_pilot.os.path.exists')
    @patch('src.py_app_pilot.py_app_pilot.os.path.isfile')
    @patch('src.py_app_pilot.py_app_pilot.os.access')
    @patch('src.py_app_pilot.py_app_pilot.subprocess.run')
    def test_validate_python_path_valid(self, mock_run, mock_access, mock_isfile, mock_exists):
        """测试验证有效的Python路径"""
        from src.py_app_pilot.py_app_pilot import PythonAppManager
        app_manager = PythonAppManager()
        app_manager.config_manager = Mock()
        app_manager.config_manager.get_global_setting.return_value = sys.executable

        # 设置模拟返回值
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_access.return_value = True
        mock_run.return_value.returncode = 0

        result = app_manager._validate_python_path()
        self.assertTrue(result)

    @patch('src.py_app_pilot.py_app_pilot.os.path.exists')
    def test_validate_python_path_not_exists(self, mock_exists):
        """测试验证不存在的Python路径"""
        from src.py_app_pilot.py_app_pilot import PythonAppManager
        app_manager = PythonAppManager()
        app_manager.config_manager = Mock()
        app_manager.config_manager.get_global_setting.return_value = 'invalid_path'

        mock_exists.return_value = False

        result = app_manager._validate_python_path()
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()