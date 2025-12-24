"""
AI教学平台后端包
"""

import os
import sys
from pathlib import Path

__version__ = '1.0.0'
__author__ = 'AI Teaching Platform Team'

# 修复导入路径
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# 导出数据库实例（将在 models/__init__.py 中定义）
__all__ = []