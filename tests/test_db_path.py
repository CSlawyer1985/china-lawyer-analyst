#!/usr/bin/env python3
"""测试数据库路径"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from tools.advisor.reinforcement_engine import ReinforcementEngine

# 打印路径
engine = ReinforcementEngine()
print(f'数据库路径: {engine.db_path}')
print(f'文件是否存在: {Path(engine.db_path).exists()}')

# 测试连接
try:
    conn = engine._get_connection()
    print('连接成功!')
    engine.close()
except Exception as e:
    print(f'连接失败: {e}')
    import traceback
    traceback.print_exc()