"""
检查配置
"""
import sys
from pathlib import Path

# 添加项目路径
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir.parent))

try:
    from config import config
    
    print("🔧 配置检查")
    print("=" * 60)
    
    # 获取默认配置
    default_config = config.get('default')
    if default_config:
        print("默认配置:")
        for key in ['DEBUG', 'SQLALCHEMY_DATABASE_URI', 'SECRET_KEY']:
            if hasattr(default_config, key):
                print(f"  {key}: {getattr(default_config, key)}")
    
    # 获取开发配置
    dev_config = config.get('development')
    if dev_config:
        print("\n开发配置:")
        for key in ['DEBUG', 'BACKEND_PORT', 'BACKEND_HOST']:
            if hasattr(default_config, key):
                print(f"  {key}: {getattr(default_config, key)}")
                
except Exception as e:
    print(f"❌ 检查配置失败: {e}")