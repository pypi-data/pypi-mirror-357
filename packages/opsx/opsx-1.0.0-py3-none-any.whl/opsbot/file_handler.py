# src/file_handler.py

import os
import shutil
import re
import patch_ng
import click

def colorize_diff(diff_text: str) -> str:
    """为 diff 文本的每一行添加颜色，使用 click.style。"""
    colored_lines = []
    for line in diff_text.splitlines():
        if line.startswith('+'):
            colored_lines.append(click.style(line, fg='green'))
        elif line.startswith('-'):
            colored_lines.append(click.style(line, fg='red'))
        elif line.startswith('@@'):
            colored_lines.append(click.style(line, fg='cyan'))
        else:
            colored_lines.append(line)
    return "\n".join(colored_lines)

def extract_and_sanitize_diff(response_text: str) -> str | None:
    """
    从AI响应中提取diff块，并逐行净化，确保其格式绝对正确。
    """
    # 1. 更宽松的正则表达式来捕获整个块
    match = re.search(r"```(?:diff)?\s*\n(.*?)```", response_text, re.DOTALL)
    if not match:
        return None
    
    raw_diff_text = match.group(1).strip()
    
    # 2. 逐行验证和净化
    sanitized_lines = []
    valid_start_tokens = ('---', '+++', '@@', ' ', '+', '-', '\\', 'diff --git', 'index', 'new file mode', 'deleted file mode', 'rename from', 'rename to', 'similarity index', 'dissimilarity index')
    
    for line in raw_diff_text.splitlines():
        # 检查每一行是否以合法的 diff 标记开头
        if any(line.startswith(token) for token in valid_start_tokens):
            sanitized_lines.append(line)
        # 如果当前行是空的，并且前一行不是空行（避免多个连续空行），也保留它
        elif not line.strip() and (not sanitized_lines or sanitized_lines[-1].strip()):
             sanitized_lines.append(line)
             
    if not sanitized_lines:
        return None

    # 3. 重新组合成一个干净的 diff 字符串
    return "\n".join(sanitized_lines)

def extract_diff_from_response(response_text: str) -> str | None:
    match = re.search(r"```diff\n(.*?)\n```", response_text, re.DOTALL)
    if match: return match.group(1).strip()
    match = re.search(r"```\n(.*?)\n```", response_text, re.DOTALL)
    if match and (match.group(1).strip().startswith('--- a/') or match.group(1).strip().startswith('diff --git')):
        return match.group(1).strip()
    return None

def get_files_from_diff(diff_text: str) -> list[str]:
    paths = set()
    for line in diff_text.splitlines():
        if line.startswith('--- a/') or line.startswith('+++ b/'):
            if '/dev/null' not in line:
                path = line.split(' ', 1)[1][2:]
                paths.add(path)
    return sorted(list(paths))

def create_backup(file_paths: list[str], operation_id: str) -> str | None:
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
    files_to_modify = get_files_from_diff(diff_text)
    if not files_to_modify:
        click.echo(click.style("警告: 在diff中未找到任何有效的文件路径。", fg='yellow'), err=True)
        return False
    
    click.echo("将要修改以下文件:")
    for f in files_to_modify: click.echo(f"  - {f}")
        
    if create_backup(files_to_modify, operation_id) is None: return False

    try:
        os.makedirs(os.path.join("opsbot_data", "diff_logs"), exist_ok=True)
        with open(os.path.join("opsbot_data", "diff_logs", f"{operation_id}.diff"), 'w', encoding='utf-8') as f:
            f.write(diff_text)
        patch_set = patch_ng.fromstring(diff_text.encode('utf-8'))
        if not patch_set:
            click.echo(click.style("应用补丁失败：AI生成的diff格式无效或无法解析。", fg='red'), err=True)
            return False
        if not patch_set.apply():
            click.echo(click.style("应用补丁失败。请检查diff内容是否正确，或文件是否已被修改。", fg='red'), err=True)
            click.echo(click.style("正在从备份中恢复...", fg='yellow'))
            revert_from_backup(operation_id)
            return False
        
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

def read_file_for_prompt(file_path: str) -> str | None:
    if not os.path.exists(file_path):
        return f"\n--- Error: File '{file_path}' not found. ---\n"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"\n--- content of {file_path} ---\n{content}\n--- end of content for {file_path} ---\n"
    except Exception as e:
        return f"\n--- Error reading file '{file_path}': {e} ---\n"