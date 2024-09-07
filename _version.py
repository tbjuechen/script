__version__ :str = "v1.2.0"
__author__:str = "tbjuechen <1324374092@qq.com>"
__license__:str = "MIT"
__date__:str = "2024-09-08"
__description__:list[str] = [f'阴阳师自动化脚本工具 {__version__}',
                             '游戏版本: 1.8.2.1613621 (源赖光)',
                             f'作者: {__author__}']

from util import format_output_info

__description__ = format_output_info(__description__, 50)

from performer import loader
from logger import logger

remote_version = loader.check_remote_version()
if remote_version != __version__:
    if __version__[:4] == remote_version[:4]:
        logger.warning(f'检测到新版本: {remote_version}，请前往Github下载')
    else:
        logger.error(f'检测到新版本: {remote_version}，当前版本: {__version__}已过期')
        while True:...
else:
    logger.info('当前版本为最新版本')