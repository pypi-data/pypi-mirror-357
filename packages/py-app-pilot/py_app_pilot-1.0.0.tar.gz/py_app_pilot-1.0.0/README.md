# PyAppPilot
### AI模型：豆包1.6 推理模型
### IDE：TRAE CN

PyPilot是一款功能强大的Python应用管理工具，由AI驱动开发，专为开发者设计，提供直观的界面来管理、监控和控制多个Python应用程序。

## 功能特性

- **应用管理**：轻松添加、删除、启动和关闭Python应用
- **多标签界面**：每个应用拥有独立的标签页，显示实时输出和状态
- **进程监控**：精确控制应用进程，包括强制终止和子进程清理
- **日志查看**：集中查看所有应用的运行日志
- **系统信息**：实时监控系统资源使用情况
- **全局Python环境**：统一管理应用使用的Python解释器
- **应用参数配置**：为每个应用自定义命令行参数和工作目录

## 安装指南

### 前提条件
- Python 3.10
- PyQt5
- psutil
- configparser
- sqlalchemy
- loguru

### 安装步骤

1. 安装依赖
```bash
uv venv
call venv/scripts/activate
uv pip install py-app-pilot
```

2. 运行应用
```bash
python -m py_app_pilot
```

## 使用说明

### 添加应用
1. 点击"添加应用"按钮
2. 选择Python文件(.py)
3. 应用将自动添加到列表中

### 配置应用
1. 从列表中选择应用
2. 在右侧面板设置命令行参数和工作目录
3. 点击"保存设置"按钮

### 管理应用
- **启动**：勾选应用并点击"启动应用"
- **关闭**：选择应用并点击"关闭应用"
- **重启**：在应用标签页中点击"重启"按钮
- **删除**：选择应用并点击"删除应用"

## 项目结构
```
py-app-pilot/
├── __init__.py          # 包入库
├── py_app_pilot.py      # 主程序入口
├── resources/           # 资源文件
│   ├── logo_rc.py          # 图标
│   ├── author_rc.py
└── utils/               # 工具函数
    ├── database.py      # 数据库操作
    ├── eunm.py          # 枚举定义
    └── log_util.py      # 日志工具
```

## 技术栈
- **前端框架**：PyQt5
- **后端**：Python 3.10
- **数据库**：SQLite
- **进程管理**：psutil, subprocess
- **日志系统**：logging

## 许可证
本项目采用MIT许可证 - 详情参见LICENSE文件

## 作者
龙翔

## 联系方式
1169207670@qq.com

---
*版本: 1.0.0*