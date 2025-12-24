# backend/routes/__init__.py
import sys
from pathlib import Path

# 修复导入路径
current_dir = Path(__file__).parent
backend_dir = current_dir.parent
project_root = backend_dir.parent

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# 导出蓝图
try:
    from .auth import auth_bp
except ImportError:
    auth_bp = None

try:
    from .user import user_bp
except ImportError:
    user_bp = None

try:
    from .quiz import quiz_bp
except ImportError:
    quiz_bp = None

__all__ = ['auth_bp', 'user_bp', 'quiz_bp']