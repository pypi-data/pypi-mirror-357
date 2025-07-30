import os
import sys

def setup_notebook_path():
    """设置notebook的Python路径，使其可以使用绝对导入。
    
    此函数应在notebook的第一个单元格中调用。
    它会将项目根目录添加到Python路径中，使得可以使用绝对导入。
    
    用法示例:
    ```python
    from src.storybuilder.utils.notebook_utils import setup_notebook_path
    setup_notebook_path()
    
    # 现在可以使用绝对导入
    from src.storybuilder.builders.pages.page import Page
    ```
    """
    # 获取当前工作目录
    current_dir = os.getcwd()
    
    # 查找项目根目录（包含src目录的目录）
    root_dir = current_dir
    while root_dir != '/':
        if os.path.exists(os.path.join(root_dir, 'src')):
            break
        root_dir = os.path.dirname(root_dir)
    
    if root_dir == '/':
        raise RuntimeError("找不到项目根目录（包含src目录的目录）")
    
    # 将项目根目录添加到Python路径
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)
        print(f"已将项目根目录添加到Python路径: {root_dir}")
    
def get_project_root():
    """获取项目根目录的绝对路径。
    
    Returns:
        str: 项目根目录的绝对路径
    """
    current_dir = os.getcwd()
    root_dir = current_dir
    
    while root_dir != '/':
        if os.path.exists(os.path.join(root_dir, 'src')):
            return root_dir
        root_dir = os.path.dirname(root_dir)
    
    raise RuntimeError("找不到项目根目录（包含src目录的目录）") 