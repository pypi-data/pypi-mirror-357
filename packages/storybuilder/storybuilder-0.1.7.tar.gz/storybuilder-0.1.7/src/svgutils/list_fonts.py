import os
from AppKit import NSFontManager

def list_system_fonts():
    """列出系统中所有可用的字体名称
    
    Returns:
        list: 字体名称列表
    """
    # 获取字体管理器实例
    font_manager = NSFontManager.sharedFontManager()
    
    # 获取所有字体名称
    font_names = sorted(set(font_manager.availableFontFamilies()))
    
    return font_names

def main():
    # 获取所有字体
    fonts = list_system_fonts()
    
    print("\n可用的系统字体:")
    print("=" * 50)
    for i, font in enumerate(fonts, 1):
        print(f"{i:3d}. {font}")
    print("\n总计: ", len(fonts), "个字体")

if __name__ == '__main__':
    main() 