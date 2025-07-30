import os
import re
import subprocess

from stv_repy.core.stv_parse import stv_parse
from stv_repy.core.traverser import traverse_dirs
from stv_repy.utils.diyhelp import print_help
from stv_repy.utils.lang_utils import set_cn
from stv_repy.utils.utils import output
from stv_utils import system_check, is_ch

__version__ = '0.0.3'

def main(__version__ = __version__):

    parser, args, remaining = stv_parse()

    if args.rp_help:
        print_help(parser)
        return

    if args.rp_version:
        print(__version__)
        return

    if args.rp_license:
        try:
            from stv_repy.utils.lic import return_mit
            print(f"\033[33m{return_mit}\033[0m")
        except ImportError:
            print(f"\033[96mThis Project Follow MIT License\033[0m")
        return

    if args.rp_set_lang:
        print("Success") if set_cn("chinese") else print("Failed")
        return

    if args.rp_clear_lang_setting:
        print("Success!") if set_cn("rm") else print("Failed")
        return

    # 分离路径模式、传递给脚本的参数和传递给Python解释器的参数
    script_args = []
    python_args = []
    patterns = []
    
    # 首先查找 '--' 分隔符
    split_index = None
    if '--' in remaining:
        split_index = remaining.index('--')
        pre_dash_args = remaining[:split_index]
        python_args = remaining[split_index+1:]
    else:
        pre_dash_args = remaining

    # 处理 '--' 之前的参数，分离路径模式和脚本参数
    path_patterns_done = False
    for arg in pre_dash_args:
        if not path_patterns_done:
            # 检查是否是路径模式
            if os.path.exists(arg) or '*' in arg or '?' in arg:
                patterns.append(arg)
            else:
                # 如果遇到非路径参数，说明路径模式部分结束
                path_patterns_done = True
                script_args.append(arg)
        else:
            # 路径模式部分已结束，所有后续参数都是脚本参数
            script_args.append(arg)

    compiled_patterns = []
    for raw_pattern in patterns:
        abs_pattern = os.path.abspath(raw_pattern)
        drive, path = os.path.splitdrive(abs_pattern)
        path = path.replace('\\', '/').lstrip('/')
        layers = [p for p in path.split('/') if p]

        regex_layers = []
        for layer in layers:
            regex_str = '^'
            for c in layer:
                if c == '*':
                    regex_str += '[^/]*'
                else:
                    regex_str += re.escape(c)
            regex_str += '$'
            regex = re.compile(regex_str, re.IGNORECASE)
            regex_layers.append(regex)

        start_dir = os.path.join(drive, '/') if drive else os.getcwd()
        compiled_patterns.append((start_dir, regex_layers))

    # 文件匹配和命令执行
    matches = []
    for start_dir, regex_layers in compiled_patterns:
        traverse_dirs(start_dir, regex_layers, 0, args, matches)

    if not matches:
        print("未找到匹配文件。") if is_ch() else print("No matching file found.")
        print("Not Support Unix-Like, Just Support Windows") if not system_check() else print(end='')
        return

    # 构建命令，正确排列参数
    cmd = ['python'] + python_args + matches + script_args
    output(cmd)

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print()
    except KeyboardInterrupt:
        print()
    print("Exit Regular Python Program.")