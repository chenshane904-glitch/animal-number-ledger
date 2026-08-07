"""
启动包装脚本 - 修复 darkdetect 模块缺失问题
在导入主应用前先 mock darkdetect
"""
import sys

# Mock darkdetect 模块
class MockDarkDetect:
    """模拟 darkdetect 模块"""
    @staticmethod
    def theme():
        return "Light"

    @staticmethod
    def isDark():
        return False

    @staticmethod
    def isLight():
        return True

    @staticmethod
    def listener(callback):
        pass

# 注入 mock 模块
sys.modules['darkdetect'] = MockDarkDetect()

# 导入并运行主应用
from app import main

if __name__ == '__main__':
    main()
