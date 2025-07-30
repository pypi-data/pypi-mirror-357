# src/opsbot/file_handler.py

import os
import shutil
import re
import patch_ng
import click
from typing import Union, List # <-- 关键导入

def colorize_diff(diff_text: str) -> str:
    colored_lines = []
    for line in diff_text.splitlines():
        if line.startswith('+'): colored_lines.append(click.style(line, fg='green'))
        elif line.startswith('-'): colored_lines.append(click.style(line, fg='red'))
        elif line.startswith('@@'): colored_lines.append(click.style(line, fg='cyan'))
        else: colored_lines.append(line)
    return "\n".join(colored_lines)

# --- 这里是第一个修正 ---
def extract_and_sanitize_diff(response_text: str) -> Union[str, None]:
    """
    用最简单、最可靠的方式从AI响应中提取diff块。
    """
    match = re.search(r"```(?:diff)?\n(.*?)\n```", response_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def get_files_from_diff(diff_text: str) -> List[str]: # 使用 List 而不是 list
    paths = set()
    for line in diff_text.splitlines():
        if line.startswith('--- a/') or line.startswith('+++ b/'):
            if '/dev/null' not in line:
                path = line.split(' ', 1)[1][2:]
                paths.add(path)
    return sorted(list(paths))

def fix_diff_paths_for_src_layout(diff_text: str) -> str:
    lines = diff_text.splitlines()
    needs_fixing = False
    for line in lines:
        if line.startswith('--- a/') and '/dev/null' not in line:
            path_without_prefix = line.split(' ', 1)[1][2:]
            if not os.path.exists(path_without_prefix) and os.path.exists(os.path.join('src', path_without_prefix)):
                click.echo(click.style(f"检测到 src-layout 结构，自动修正 diff 路径...", fg='magenta'))
                needs_fixing = True
            break
    if not needs_fixing: return diff_text
    fixed_lines = []
    for line in lines:
        if line.startswith('--- a/') or line.startswith('+++ b/'):
            parts = line.split(' ', 1)
            fixed_path = 'a/src/' + parts[1][2:] if parts[1].startswith('a/') else 'b/src/' + parts[1][2:]
            fixed_lines.append(f"{parts[0]} {fixed_path}")
        else:
            fixed_lines.append(line)
    return "\n".join(fixed_lines)

# --- 这里是第二个修正 ---
def create_backup(file_paths: List[str], operation_id: str) -> Union[str, None]:
    backup_path = os.path.join("opsbot_data", "backups", operation_id)
    try:
        os.makedirs(backup_path, exist_ok=True)
        for file_path in file_paths:
            if os.path.exists(file_path):
                dest_path = os.path.join(backup_path, file_path)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(file_path, dest_path)
        return backup_path
    except Exception as e:
        click.echo(click.style(f"创建备份失败: {e}", fg='red'), err=True)
        return None

def apply_diff(diff_text: str, operation_id: str) -> bool:
    corrected_diff_text = fix_diff_paths_for_src_layout(diff_text)
    files_to_modify = get_files_from_diff(corrected_diff_text)
    if not files_to_modify:
        click.echo(click.style("警告: 在diff中未找到任何有效的文件路径。", fg='yellow'), err=True)
        return False
    click.echo("将要修改以下文件:")
    for f in files_to_modify: click.echo(f"  - {f}")
    if create_backup(files_to_modify, operation_id) is None: return False
    try:
        patch_set = patch_ng.fromstring(corrected_diff_text.encode('utf-8'))
        if not patch_set:
            click.echo(click.style("应用补丁失败：AI生成的diff格式无效或无法解析。", fg='red'), err=True)
            return False
        if not patch_set.apply():
            click.echo(click.style("应用补丁失败。可能是因为上下文不匹配（文件已被修改）。", fg='red'), err=True)
            click.echo(click.style("正在从备份中恢复...", fg='yellow'))
            revert_from_backup(operation_id)
            return False
        os.makedirs(os.path.join("opsbot_data", "diff_logs"), exist_ok=True)
        with open(os.path.join("opsbot_data", "diff_logs", f"{operation_id}.diff"), 'w', encoding='utf-8') as f:
            f.write(corrected_diff_text)
        click.echo(click.style("补丁已成功应用！", fg='green', bold=True))
        return True
    except Exception as e:
        click.echo(click.style(f"应用diff时发生未知错误: {e}", fg='red'), err=True)
        revert_from_backup(operation_id)
        return False

def revert_from_backup(operation_id: str) -> bool:
    backup_path = os.path.join("opsbot_data", "backups", operation_id)
    if not os.path.isdir(backup_path):
        click.echo(click.style(f"错误: 找不到操作ID为 '{operation_id}' 的备份。", fg='red'), err=True)
        return False
    try:
        for root, _, files in os.walk(backup_path):
            for file in files:
                backup_file_path = os.path.join(root, file)
                relative_path = os.path.relpath(backup_file_path, backup_path)
                original_file_path = relative_path
                os.makedirs(os.path.dirname(original_file_path), exist_ok=True)
                shutil.copy2(backup_file_path, original_file_path)
        click.echo(click.style(f"已成功从备份 '{operation_id}' 恢复文件。", fg='green'))
        return True
    except Exception as e:
        click.echo(click.style(f"从备份恢复时出错: {e}", fg='red'), err=True)
        return False

# --- 这里是第三个修正 ---
def read_file_for_prompt(file_path: str) -> Union[str, None]:
    if not os.path.exists(file_path):
        src_path = os.path.join('src', file_path)
        if os.path.exists(src_path): file_path = src_path
        else: return f"\n--- Error: File '{file_path}' not found. ---\n" # Technically this is a string, so it fits Union[str, None]
    try:
        with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
        return f"\n--- content of {file_path} ---\n{content}\n--- end of content for {file_path} ---\n"
    except Exception as e:
        return f"\n--- Error reading file '{file_path}': {e} ---\n"

def extract_diff_from_response(response_text: str) -> Union[str, None]:
    match = re.search(r"```diff\n(.*?)\n```", response_text, re.DOTALL)
    if match: return match.group(1).strip()
    match = re.search(r"```\n(.*?)\n```", response_text, re.DOTALL)
    if match and (match.group(1).strip().startswith('--- a/') or match.group(1).strip().startswith('diff --git')):
        return match.group(1).strip()
    return None