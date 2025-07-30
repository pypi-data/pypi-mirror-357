# src/opsbot/chat_session.py

import os
import json
import sys
import re
from datetime import datetime
import click

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import Style
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys  # <-- 关键导入
from prompt_toolkit.formatted_text import HTML

from .api_client import ApiClient
from .config import OpsBotConfig, DATA_DIR_NAME, CHATS_DIR_NAME
from .core import get_project_context_string
from .file_handler import (
    extract_diff_from_response, 
    apply_diff, 
    revert_from_backup,
    read_file_for_prompt,
    colorize_diff
)

PROMPT_STYLE = Style.from_dict({
    'prompt': 'ansigreen',
    'continuation': 'ansiblue',
})

class ChatSession:
    def __init__(self, api_client: ApiClient, config: OpsBotConfig, session_id: str = None):
        self.api_client = api_client
        self.config = config
        self.messages = []
        self.last_operation_id = None
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.chat_file_path = os.path.join(DATA_DIR_NAME, CHATS_DIR_NAME, f"{self.session_id}.json")

        # --- KeyBindings Setup ---
        kb = KeyBindings()

        # 使用正确的 Keys.ControlEnter 常量
        @kb.add(Keys.ShiftDown)
        def _(event):
            """当按下 Ctrl+Enter 时，插入一个换行符。"""
            event.current_buffer.insert_text("\n")

        # Enter 键用于提交
        @kb.add(Keys.Enter)
        def _(event):
            """当按下 Enter 时，提交输入。"""
            event.current_buffer.validate_and_handle()
        # --- End of KeyBindings Setup ---

        history_file = os.path.join(DATA_DIR_NAME, ".chat_history")
        os.makedirs(os.path.dirname(history_file), exist_ok=True)
        self.prompt_session = PromptSession(
            history=FileHistory(history_file), auto_suggest=AutoSuggestFromHistory(),
            style=PROMPT_STYLE, multiline=True, key_bindings=kb,
            prompt_continuation=HTML('<style bg="ansiblue" fg="ansiwhite"> > </style> ')
        )
        
        if session_id and os.path.exists(self.chat_file_path):
            self.load()
        else:
            prompt_path = self.config.default_system_prompt_file
            self.set_system_prompt_from_file(prompt_path, is_new_session=True)
            click.echo(click.style(f"新会话已开始。会话ID: {self.session_id}", fg='yellow'))

    # ... [ load, save, print_help, 等所有其他方法保持不变 ] ...
    def load(self):
        try:
            with open(self.chat_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.messages = data.get('messages', data)
                self.last_operation_id = data.get('last_operation_id')
            click.echo(click.style(f"成功加载历史会话: {self.session_id}", fg='yellow'))
        except (FileNotFoundError, json.JSONDecodeError) as e:
            click.echo(click.style(f"无法加载会话 {self.session_id}: {e}", fg='red'), err=True)
            self.set_system_prompt_from_file(self.config.default_system_prompt_file, is_new_session=True)

    def save(self):
        session_data = {'session_id': self.session_id, 'last_operation_id': self.last_operation_id, 'messages': self.messages}
        try:
            os.makedirs(os.path.dirname(self.chat_file_path), exist_ok=True)
            with open(self.chat_file_path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            click.echo(click.style(f"无法保存会话: {e}", fg='red'), err=True)

    def print_help(self):
        styled_help = f"""
{click.style('可用命令:', fg='yellow', bold=True)}
  /exit, /quit    - 退出聊天会话。
  /save           - 手动保存当前会话。
  /new            - 在当前会话中清空上下文，开始一个新话题。
  /help           - 显示此帮助信息。
  /sys_prompt <path> - 从文件设置一个新的系统提示词。
  /del_sys_prompt - 恢复到配置文件中指定的默认系统提示词。
  /reload         - 重载 .ops 配置 (API客户端和默认提示词会更新)。
  /back           - 回滚上一次成功的代码修改。
  /load_context   - 扫描当前项目，并将上下文注入到当前会话中。
  /fallback       - 撤销上一轮对话 (删除你的上一条消息和AI的回复)。
  /retry          - 让AI针对你的上一条消息重新生成回答。
{click.style('输入技巧:', fg='yellow', bold=True)}
  - 按 [Enter] 来提交输入。
  - 按 [Ctrl+Enter] (或 Cmd+Enter) 来插入一个新行。
  - 按 [Ctrl+D] 或输入 /exit 来退出。
  - 按 [上/下箭头] 浏览历史记录。
        """
        click.echo(styled_help)

    def set_system_prompt_from_file(self, file_path: str, is_new_session: bool = False):
        if not os.path.exists(file_path):
            click.echo(click.style(f"错误: 系统提示词文件 '{file_path}' 未找到。", fg='red'), err=True)
            if is_new_session: self.messages.append({"role": "system", "content": "You are a helpful AI assistant."})
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as f: prompt = f.read()
            if self.messages and self.messages[0]['role'] == 'system': self.messages[0]['content'] = prompt
            else: self.messages.insert(0, {"role": "system", "content": prompt})
            if not is_new_session: click.echo(click.style(f"系统提示词已从 '{file_path}' 更新。", fg='yellow'))
        except Exception as e: click.echo(click.style(f"读取系统提示词文件时出错: {e}", fg='red'), err=True)

    def handle_user_input(self, user_input: str) -> str:
        def replace_file_ref(match): return read_file_for_prompt(match.group(1))
        return re.sub(r"\$\{(.*?)\}", replace_file_ref, user_input)

    def handle_diff_application(self, diff_text: str):
        colored_diff = colorize_diff(diff_text)
        while True:
            click.echo(f"\n{click.style('--- 检测到以下DIFF修改 ---', fg='yellow')}\n{colored_diff}\n{click.style('--- 结束DIFF ---', fg='yellow')}")
            prompt_text = (
                f"是否应用此修改? "
                f"({click.style('y', fg='green')})es / "
                f"({click.style('n', fg='red')})o / "
                f"({click.style('d', fg='yellow')})etails / "
                f"({click.style('q', fg='red')})uit session: "
            )
            choice = input(prompt_text).lower()
            if choice in ['y', 'yes']:
                operation_id = f"{self.session_id}_{datetime.now().strftime('%H%M%S')}"
                if apply_diff(diff_text, operation_id):
                    self.last_operation_id = operation_id
                    click.echo(click.style(f"操作ID '{operation_id}' 已记录。可使用 /back 命令回退。", fg='green'))
                else: click.echo(click.style("应用修改失败。", fg='red'))
                break
            elif choice in ['n', 'no']: click.echo("操作已取消."); break
            elif choice in ['d', 'details']: click.echo("重新显示 diff 详情..."); continue
            elif choice in ['q', 'quit']: raise KeyboardInterrupt("User requested quit during diff confirmation.")
            else: click.echo(click.style("无效输入。请输入 y, n, d, 或 q。", fg='red'))

    def _trigger_ai_response(self):
        assistant_response = self.api_client.get_completion(self.messages)
        if assistant_response:
            self.messages.append({"role": "assistant", "content": assistant_response})
            self.save()
            diff_text = extract_diff_from_response(assistant_response)
            if diff_text: self.handle_diff_application(diff_text)

    def start(self):
        click.echo(click.style("聊天会话已启动。输入 '/help' 查看命令，'/exit' 退出。", fg='yellow'))
        click.echo("-" * 30)
        while True:
            try:
                prompt_message = HTML('<style bg="ansigreen" fg="ansiwhite"> You: </style> ')
                raw_user_input = self.prompt_session.prompt(prompt_message)
                
                if not raw_user_input.strip(): continue
                if raw_user_input.startswith('/'):
                    parts = raw_user_input.split(' ', 1)
                    command = parts[0].lower(); arg = parts[1].strip() if len(parts) > 1 else ""
                    if command in ["/exit", "/quit"]: click.echo(click.style("正在保存并退出会话...", fg='yellow')); self.save(); break
                    elif command == "/help": self.print_help(); continue
                    elif command == "/save": self.save(); click.echo(click.style(f"会话已手动保存到 {self.chat_file_path}", fg='yellow')); continue
                    elif command == "/new":
                        system_prompt = self.messages[0] if self.messages and self.messages[0]['role'] == 'system' else {"role": "system", "content": "You are a helpful AI assistant."}
                        self.messages = [system_prompt]; self.last_operation_id = None; self.save()
                        click.echo(click.style("上下文已清空。可以开始新话题了。", fg='yellow')); continue
                    elif command == "/sys_prompt":
                        if not arg: click.echo(click.style("用法: /sys_prompt <file_path>", fg='red')); continue
                        self.set_system_prompt_from_file(arg); self.save(); continue
                    elif command == "/del_sys_prompt": self.set_system_prompt_from_file(self.config.default_system_prompt_file); self.save(); continue
                    elif command == "/reload":
                        click.echo(click.style("正在重载配置...", fg='yellow'))
                        self.config = OpsBotConfig(); self.api_client = ApiClient(self.config)
                        self.set_system_prompt_from_file(self.config.default_system_prompt_file)
                        click.echo(click.style("配置已重载。", fg='yellow')); continue
                    elif command == "/back":
                        if self.last_operation_id:
                            click.echo(click.style(f"准备回滚操作: {self.last_operation_id}", fg='yellow'))
                            if revert_from_backup(self.last_operation_id): self.last_operation_id = None; self.save()
                        else: click.echo(click.style("没有可回退的操作。", fg='red'))
                        continue
                    elif command == "/load_context":
                        click.echo(click.style("正在加载项目上下文... (这可能需要一些时间)", fg='yellow'))
                        try:
                            context_string = get_project_context_string('.', self.config.allowed_extensions, self.config.blacklist_folders)
                            user_message = (f"请首先仔细阅读并理解我提供的以下项目上下文信息。在后续的对话中，我希望你能基于这些信息进行回答和操作。\n{context_string}")
                            self.messages.append({"role": "user", "content": user_message}); self.save()
                            click.echo(click.style("项目上下文已成功加载并注入到当前会话。", fg='green'))
                        except Exception as e: click.echo(click.style(f"加载上下文时出错: {e}", fg='red'), err=True)
                        continue
                    elif command == "/fallback":
                        if len(self.messages) >= 3 and self.messages[-1]['role'] == 'assistant' and self.messages[-2]['role'] == 'user':
                            self.messages.pop(); self.messages.pop(); self.save()
                            click.echo(click.style("已撤销上一轮对话。", fg='yellow'))
                        else: click.echo(click.style("没有可供撤销的对话。", fg='red'))
                        continue
                    elif command == "/retry":
                        if len(self.messages) >= 2 and self.messages[-1]['role'] == 'assistant':
                            click.echo(click.style("正在针对上一条消息重试...", fg='yellow')); self.messages.pop()
                            self._trigger_ai_response()
                        else: click.echo(click.style("没有可供重试的AI回复。", fg='red'))
                        continue
                    else: click.echo(click.style(f"未知命令: {command}。输入 /help 查看可用命令。", fg='red')); continue

                processed_input = self.handle_user_input(raw_user_input)
                self.messages.append({"role": "user", "content": processed_input})
                self._trigger_ai_response()
                        
            except EOFError: click.echo(click.style("\n检测到 EOF。正在保存并退出...", fg='yellow')); self.save(); break
            except KeyboardInterrupt as e:
                if "User requested quit" in str(e): click.echo(click.style("\n用户请求退出。正在保存会话...", fg='yellow'))
                else: click.echo(click.style("\n检测到中断。正在保存并退出...", fg='yellow'))
                self.save(); break
            except Exception as e:
                click.echo(click.style(f"发生意外错误: {e}", fg='red'), err=True)
                click.echo(click.style("正在尝试保存当前会话...", fg='yellow')); self.save(); break