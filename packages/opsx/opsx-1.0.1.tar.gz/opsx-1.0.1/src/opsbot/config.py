# src/opsbot/config.py

import os
import shutil
import configparser
from importlib import metadata
from importlib import resources
import sys

# ANSI escape codes for colors
C_RED = '\033[91m'
C_YELLOW = '\033[93m'
C_END = '\033[0m'

# --- Constants ---
CONFIG_FILE_NAME = ".ops"
DATA_DIR_NAME = "opsbot_data"
CHATS_DIR_NAME = "chats"
PROMPTS_DIR_NAME = "prompts"  # 用户侧的prompts目录名

# 指向用户本地的默认提示词文件路径
LOCAL_DEFAULT_PROMPT_FILE = os.path.join(DATA_DIR_NAME, PROMPTS_DIR_NAME, "default_code_prompt.txt")

# 默认的文件包含/排除列表
DEFAULT_EXTENSIONS = [".jsx", ".py", ".js", ".html", ".css", ".sql", ".md", ".json", ".ts", ".tsx", "Dockerfile", ".sh", ".yaml", ".yml"]
DEFAULT_BLACKLIST = ["node_modules", ".git", "__pycache__", "dist", "build", "venv", ".venv", "target", "docs", DATA_DIR_NAME]


def get_package_version():
    """获取包的版本号"""
    try:
        return metadata.version('opsbot-prompt-generator')
    except metadata.PackageNotFoundError:
        return "0.0.0-dev"

class OpsBotConfig:
    def __init__(self, path=CONFIG_FILE_NAME):
        self.path = path
        self.config = configparser.ConfigParser()
        if os.path.exists(self.path):
            self.config.read(self.path, encoding='utf-8')

    def get_or_else(self, section, option, fallback=None):
        return self.config.get(section, option, fallback=fallback)

    def get_list(self, section, option, fallback=None):
        value = self.get_or_else(section, option)
        if value:
            return [item.strip() for item in value.split(',') if item.strip()]
        return fallback if fallback is not None else []

    # --- OpenAI specific properties ---
    @property
    def openai_api_key(self):
        return self.get_or_else('openai', 'api_key')

    @property
    def openai_base_url(self):
        return self.get_or_else('openai', 'base_url', fallback='https://api.openai.com/v1')

    @property
    def openai_default_model(self):
        return self.get_or_else('openai', 'default_model', fallback='gpt-4o')

    # --- Chat specific properties ---
    @property
    def default_system_prompt_file(self):
        return self.get_or_else('chat', 'default_system_prompt_file', fallback=LOCAL_DEFAULT_PROMPT_FILE)

    # --- Prompt Generator specific properties ---
    @property
    def allowed_extensions(self):
        return self.get_list('prompt_generator', 'allowed_extensions', fallback=DEFAULT_EXTENSIONS)

    @property
    def blacklist_folders(self):
        return self.get_list('prompt_generator', 'blacklist_folders', fallback=DEFAULT_BLACKLIST)


def create_initial_config():
    """生成并写入初始配置文件 .ops"""
    if os.path.exists(CONFIG_FILE_NAME):
        overwrite = input(f"'{CONFIG_FILE_NAME}' 文件已存在。是否要覆盖? [y/N]: ").lower()
        if overwrite != 'y':
            print("操作已取消。")
            return False  # 返回 False 表示未创建

    config = configparser.ConfigParser()
    
    config['opsbot'] = {'version': get_package_version()}
    
    config['openai'] = {
        'base_url': 'https://api.openai.com/v1',
        'api_key': 'YOUR_OPENAI_API_KEY_HERE',
        'default_model': 'gpt-4o'
    }

    config['chat'] = {
        '# 默认系统提示词文件路径': '',
        'default_system_prompt_file': LOCAL_DEFAULT_PROMPT_FILE
    }
    
    config['prompt_generator'] = {
        '# 以逗号分隔的文件后缀名列表': '',
        'allowed_extensions': ', '.join(DEFAULT_EXTENSIONS),
        '# 以逗号分隔的要排除的文件夹名列表': '',
        'blacklist_folders': ', '.join(DEFAULT_BLACKLIST)
    }

    with open(CONFIG_FILE_NAME, 'w', encoding='utf-8') as configfile:
        config.write(configfile)
    
    print(f"配置文件 '{CONFIG_FILE_NAME}' 已成功生成。")
    print("请记得在文件中填入你的 OpenAI API Key。")
    return True # 返回 True 表示已创建或覆盖


def initialize_project_structure():
    """创建 opsbot_data 目录结构，并复制默认提示词。"""
    print(f"正在初始化 OpsBot 结构...")

    # 1. 创建数据目录
    if not os.path.exists(DATA_DIR_NAME):
        os.makedirs(DATA_DIR_NAME)
        print(f"  - 已创建数据目录: {DATA_DIR_NAME}")

    # 2. 创建聊天记录子目录
    chats_path = os.path.join(DATA_DIR_NAME, CHATS_DIR_NAME)
    if not os.path.exists(chats_path):
        os.makedirs(chats_path)
        print(f"  - 已创建聊天记录目录: {chats_path}")
        
    # 3. 创建用户侧的提示词子目录
    prompts_path = os.path.join(DATA_DIR_NAME, PROMPTS_DIR_NAME)
    if not os.path.exists(prompts_path):
        os.makedirs(prompts_path)
        print(f"  - 已创建提示词目录: {prompts_path}")

    # 4. 从包内复制默认提示词文件到用户目录
    try:
        # 使用 importlib.resources 安全地访问包内文件
        # 'opsbot.prompts' 是包路径，'default_code_prompt.txt' 是文件名
        with resources.files('opsbot.prompts').joinpath('default_code_prompt.txt').open('rb') as source_file:
            # 目标路径是我们定义好的本地路径
            target_path = LOCAL_DEFAULT_PROMPT_FILE
            with open(target_path, 'wb') as target_file:
                shutil.copyfileobj(source_file, target_file)
            print(f"  - 已将默认系统提示词复制到: {target_path}")
            print(f"{C_YELLOW}  - 你可以编辑此文件来自定义机器人的核心行为。{C_END}")

    except (FileNotFoundError, ModuleNotFoundError) as e:
        print(f"{C_RED}错误: 无法找到包内的默认提示词文件。请确保使用 'pip install -e .' 正确安装。{e}{C_END}", file=sys.stderr)
    except Exception as e:
        print(f"{C_RED}复制默认提示词时发生未知错误: {e}{C_END}", file=sys.stderr)