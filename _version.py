__version__ :str = "v1.0.3"
__author__:str = "tbjuechen <1324374092@qq.com>"
__license__:str = "MIT"
__date__:str = "2024-08-14"
__description__:str = f'''
+---------------------------------------------+
|  阴阳师自动化脚本工具 {__version__}                |
|  游戏版本: 1.8.2.1613621 (sp烟烟罗)         |
+---------------------------------------------+
'''
# def generate_border(x_width:int, lines:list[str])->str:
#     '''Generate a border with the specified width and lines

#     Parameters
#     ----------
#     x_width : int
#         The width of the border
#     lines : list[str]
#         The lines to be displayed in the border

#     Returns
#     -------
#     str
#         The border
#     '''
#     border:str = ''
#     for line in lines:
#         border += f'| {line}{" "*(x_width-len(line))}|\n'
#     return f'+{"-"*(x_width-2)}+\n{border}+{"-"*(x_width-2)}+'

# __description__ = generate_border(44, [f'阴阳师自动化脚本工具 {__version__}', f'游戏版本: 1.8.2.1613621 (sp烟烟罗)'])