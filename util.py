import os 
from typing import List
from wcwidth import wcswidth

def format_output_info(output:List[str], width:int)->str:
    '''format the output info like  
    +---------------------------------+  
    |&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;|  
    |&emsp;&emsp;&emsp;info&nbsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;|  
    |&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;|  
    +---------------------------------+  

    Parameters
    ----------
    output : List[str]
        The output info
    width : int
        The width of the output info
    
    Returns
    -------
    str
        The formatted output info
    '''
    terminal_width = os.get_terminal_size().columns
    max_width = wcswidth(max(*output, key=wcswidth))
    width = width if width > max_width else max_width
    line_spcace = int((width - max_width)/2)
    format_space = int((terminal_width - width - 10)/2)
    ans = f'{" "*format_space}+{"-"*width}+\n'
    for item in output:
        ans += f'{" "*format_space}|{" "*(line_spcace) + item + " "*(width-line_spcace-wcswidth(item))}|\n'
    ans += f'{" "*format_space}+{"-"*width}+\n'
    return ans
