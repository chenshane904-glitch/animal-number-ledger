# -*- coding: utf-8 -*-
"""
跨平台字体管理模块
为不同操作系统提供合适的字体
"""
import sys
import platform


class FontManager:
    """字体管理器"""

    # Windows 字体映射到 macOS/Linux
    FONT_MAPPING = {
        'Microsoft YaHei': {
            'darwin': 'PingFang SC',  # macOS
            'linux': 'WenQuanYi Micro Hei',  # Linux
        },
        'SimHei': {
            'darwin': 'Heiti SC',
            'linux': 'WenQuanYi Zen Hei',
        },
        'SimSun': {
            'darwin': 'Songti SC',
            'linux': 'AR PL UMing CN',
        },
        'Consolas': {
            'darwin': 'Menlo',
            'linux': 'DejaVu Sans Mono',
        },
        'Arial': {
            'darwin': 'Helvetica Neue',
            'linux': 'Liberation Sans',
        },
    }

    # 各平台默认字体
    DEFAULT_FONTS = {
        'win32': 'Microsoft YaHei',
        'darwin': 'PingFang SC',
        'linux': 'WenQuanYi Micro Hei',
    }

    # 各平台等宽字体
    MONOSPACE_FONTS = {
        'win32': 'Consolas',
        'darwin': 'Menlo',
        'linux': 'DejaVu Sans Mono',
    }

    @classmethod
    def get_font(cls, windows_font: str, fallback: str = None) -> str:
        """
        获取跨平台字体

        Args:
            windows_font: Windows 字体名称
            fallback: 备用字体

        Returns:
            当前平台适用的字体名称
        """
        current_platform = sys.platform

        if current_platform == 'win32':
            # Windows 直接返回
            return windows_font

        # 查找映射
        if windows_font in cls.FONT_MAPPING:
            mapped = cls.FONT_MAPPING[windows_font].get(current_platform)
            if mapped:
                return mapped

        # 使用备用字体
        if fallback:
            return fallback

        # 使用平台默认字体
        return cls.DEFAULT_FONTS.get(current_platform, 'sans-serif')

    @classmethod
    def get_default_font(cls) -> str:
        """获取平台默认字体"""
        return cls.DEFAULT_FONTS.get(sys.platform, 'sans-serif')

    @classmethod
    def get_monospace_font(cls) -> str:
        """获取等宽字体"""
        return cls.MONOSPACE_FONTS.get(sys.platform, 'monospace')

    @classmethod
    def get_ui_font(cls, size: int = 11, weight: str = 'normal') -> tuple:
        """
        获取 UI 字体元组（用于 Tkinter）

        Args:
            size: 字号
            weight: 粗细 ('normal', 'bold')

        Returns:
            (字体名, 字号, 粗细) 元组
        """
        font_name = cls.get_default_font()
        return (font_name, size, weight)

    @classmethod
    def replace_font_in_config(cls, font_config: tuple) -> tuple:
        """
        替换字体配置中的 Windows 字体

        Args:
            font_config: (字体名, 字号, ...) 元组

        Returns:
            替换后的字体配置
        """
        if not font_config or not isinstance(font_config, tuple):
            return font_config

        if len(font_config) == 0:
            return font_config

        # 获取字体名
        font_name = font_config[0]

        # 替换为跨平台字体
        new_font_name = cls.get_font(font_name)

        # 构造新的元组
        return (new_font_name,) + font_config[1:]


# 便捷函数
def get_font(windows_font: str, fallback: str = None) -> str:
    """获取跨平台字体（便捷函数）"""
    return FontManager.get_font(windows_font, fallback)


def get_default_font() -> str:
    """获取平台默认字体（便捷函数）"""
    return FontManager.get_default_font()


def get_monospace_font() -> str:
    """获取等宽字体（便捷函数）"""
    return FontManager.get_monospace_font()


def get_ui_font(size: int = 11, weight: str = 'normal') -> tuple:
    """获取 UI 字体元组（便捷函数）"""
    return FontManager.get_ui_font(size, weight)


if __name__ == '__main__':
    # 测试
    print("="*70)
    print("跨平台字体测试")
    print("="*70)
    print(f"\n当前平台: {sys.platform}")
    print(f"系统: {platform.system()} {platform.release()}")

    print(f"\n默认字体: {get_default_font()}")
    print(f"等宽字体: {get_monospace_font()}")

    print(f"\nWindows 字体映射:")
    test_fonts = ['Microsoft YaHei', 'SimHei', 'Consolas', 'Arial']
    for font in test_fonts:
        mapped = get_font(font)
        print(f"  {font} -> {mapped}")

    print(f"\nUI 字体配置:")
    print(f"  普通: {get_ui_font(11, 'normal')}")
    print(f"  加粗: {get_ui_font(12, 'bold')}")
    print(f"  大号: {get_ui_font(14, 'bold')}")

    print("="*70)
