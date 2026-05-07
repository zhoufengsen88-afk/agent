'''
为整个工程提供同意的绝对路径
'''

import os

def get_project_root() -> str:
    '''
    获取工程所在的根目录
    :return:字符串和目录
    '''
    # 当前文件的绝对路径
    current_file = os.path.abspath(__file__) # abspath意思就是绝对路径,__file__表示当前代码文件

    # 获取工程根目录，先获得文件所在的文件夹绝对路径（utils文件夹）
    current_dir = os.path.dirname(current_file)

    # 获取工程根目录（agent项目工程文件夹）
    project_root = os.path.dirname(current_dir)
    return project_root

def get_abs_path(relative_path:str) -> str:
    '''
    传递相对路径，得到绝对路径
    :param relative_path:
    :return:
    '''
    project_root = get_project_root()
    return os.path.join(project_root,relative_path) # 项目根目录和文件子目录拼接得到完整绝对路径

if __name__ == '__main__':

    print(get_abs_path("config/config.txt"))