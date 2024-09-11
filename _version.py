__version__ :str = "v1.2.1"
__author__:str = "tbjuechen <1324374092@qq.com>"
__license__:str = "MIT"
__date__:str = "2024-09-11"
__description__:list[str] = [f'阴阳师自动化脚本工具 {__version__}',
                             '游戏版本:20240911-周年庆']
__online__:bool = True

from util import format_output_info

__description__ = format_output_info(__description__, 50)

from performer import loader
from logger import logger

try:
    remote_version = loader.check_remote_version()
    if remote_version != __version__:
        if __version__[:4] == remote_version[:4]:
            logger.warning(f'检测到新版本: {remote_version}，请前往Github下载')
        else:
            logger.error(f'检测到新版本: {remote_version}，当前版本: {__version__}已过期')
            while True:...
    else:
        logger.info('当前版本为最新版本')
except Exception as e:
    logger.debug(f'检查版本失败: {type(e).__name__} - {str(e)}')
    if type(e).__name__ == 'ReadTimeout':
        logger.error('请检查网络连接')
        logger.info('进入离线模式')
        logger.warning('请注意，离线模式下无法检查版本获得更新并加载最新资源！')
        __online__ = False
    else:
        while True:...