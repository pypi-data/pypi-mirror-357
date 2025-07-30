# src/opsbot/cli.py

import argparse
import os
import sys
import click

from .core import create_prompt_from_directory
from .config import (
    OpsBotConfig,
    create_initial_config,
    initialize_project_structure,
    get_package_version
)
from .api_client import ApiClient
from .chat_session import ChatSession
from .file_handler import read_file_for_prompt

def handle_init(args):
    """处理 opsbot init 命令。实际的输出在调用的函数中处理。"""
    if create_initial_config():
        initialize_project_structure()

def handle_gp(args):
    """处理 opsbot gp 命令"""
    config = OpsBotConfig()

    if args.ext:
        allowed_extensions = args.ext
    else:
        allowed_extensions = config.allowed_extensions
    
    if args.blacklist:
        blacklist_folders = args.blacklist
    else:
        blacklist_folders = config.blacklist_folders

    if "opsbot" not in blacklist_folders:
        blacklist_folders.append("opsbot")

    if not os.path.isdir(args.target_dir):
        click.echo(click.style(f"错误: 目录 '{args.target_dir}' 不存在。", fg='red'), err=True)
        sys.exit(1)
    
    create_prompt_from_directory(
        target_dir=args.target_dir,
        output_file=args.output,
        allowed_ext=allowed_extensions,
        blacklist_folders=blacklist_folders
    )

def handle_chat(args):
    """处理 opsbot chat 命令"""
    config = OpsBotConfig()
    api_client = ApiClient(config)
    session = ChatSession(api_client, config=config, session_id=args.session)

    if args.prompt_file:
        if not os.path.exists(args.prompt_file):
            click.echo(click.style(f"错误: 提示文件 '{args.prompt_file}' 不存在。", fg='red'), err=True)
            sys.exit(1)
            
        file_content_for_prompt = read_file_for_prompt(args.prompt_file)
        
        if file_content_for_prompt and "Error" not in file_content_for_prompt:
            initial_user_message = (
                "请首先仔细阅读并理解我提供的以下项目上下文信息。在后续的对话中，我希望你能基于这些信息进行回答和操作。\n"
                f"{file_content_for_prompt}"
            )
            session.messages.append({"role": "user", "content": initial_user_message})
            click.echo(click.style(f"已将 '{args.prompt_file}' 内容作为第一条消息注入到会话中。", fg='yellow'))
        else:
            click.echo(click.style(file_content_for_prompt, fg='red'), err=True)
            sys.exit(1)
    
    session.start()

def main():
    parser = argparse.ArgumentParser(
        prog="opsbot",
        description="一个CLI工具，用于与项目交互并与AI模型通信。"
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'%(prog)s {get_package_version()}'
    )
    subparsers = parser.add_subparsers(dest="command", help="可用的子命令")
    subparsers.required = True # 确保至少有一个子命令被调用

    parser_init = subparsers.add_parser("init", help="在当前目录初始化项目配置和数据结构。")
    parser_init.set_defaults(func=handle_init)

    parser_gp = subparsers.add_parser("gp", aliases=['get-prompt'], help="扫描项目并生成用于AI的上下文提示文件。")
    parser_gp.add_argument("target_dir", nargs='?', default='.', help="要扫描的目标目录 (默认为当前目录)。")
    parser_gp.add_argument("-o", "--output", default="output.txt", help="输出文件的名称 (默认为 'output.txt')。")
    parser_gp.add_argument("-e", "--ext", action='append', help="覆盖配置：要包含的文件后缀。")
    parser_gp.add_argument("-b", "--blacklist", action='append', help="覆盖配置：要排除的文件夹名。")
    parser_gp.set_defaults(func=handle_gp)

    parser_chat = subparsers.add_parser("chat", help="启动一个交互式聊天会话。")
    parser_chat.add_argument("-s", "--session", help="要恢复的聊天会话ID。")
    parser_chat.add_argument("-p", "--prompt-file", help="将文件内容作为初始上下文注入聊天。")
    parser_chat.set_defaults(func=handle_chat)

    if len(sys.argv) <= 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()