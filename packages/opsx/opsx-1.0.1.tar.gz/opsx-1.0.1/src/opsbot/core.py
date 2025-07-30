# src/core.py

import os
import click

def get_all_files(root_dir, extensions, blacklist_dirs=None):
    if blacklist_dirs is None: blacklist_dirs = []
    file_paths = []
    normalized_blacklist = {os.path.normpath(d) for d in blacklist_dirs}
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=True):
        dirnames[:] = [d for d in dirnames if d not in normalized_blacklist]
        for filename in filenames:
            if os.path.splitext(filename)[1].lower() in extensions:
                file_paths.append(os.path.join(dirpath, filename))
    return sorted(file_paths)

def generate_file_tree(root_dir, file_paths):
    processed_dirs = set()
    output = []
    root_name = os.path.basename(root_dir.rstrip(os.sep))
    if not root_name: root_name = os.path.basename(os.path.abspath(root_dir))
    output.append(f"{root_name}/")
    processed_dirs.add(os.path.normpath(root_dir))
    for path in file_paths:
        rel_path = os.path.relpath(path, root_dir)
        parts = rel_path.split(os.sep)
        current_path_prefix = ""
        for i in range(len(parts) - 1):
            current_path_prefix = os.path.join(current_path_prefix, parts[i])
            current_abs_dir = os.path.join(root_dir, current_path_prefix)
            if os.path.normpath(current_abs_dir) not in processed_dirs:
                indent = "    " * (i + 1)
                output.append(f"{indent}{parts[i]}/")
                processed_dirs.add(os.path.normpath(current_abs_dir))
        indent = "    " * len(parts)
        output.append(f"{indent}{parts[-1]}")
    return "\n".join(output)

def format_content(file_path, root_dir):
    rel_path = os.path.relpath(file_path, root_dir)
    extension = os.path.splitext(file_path)[1][1:]
    try:
        with open(file_path, "r", encoding="utf-8") as f: content = f.read()
        return f"//--- {rel_path} ---\n```{extension}\n{content}\n```\n\n"
    except Exception as e:
        return f"//--- {rel_path} ---\n// Error reading file: {str(e)}\n\n"

def get_project_context_string(target_dir: str, allowed_ext: list, blacklist_folders: list) -> str:
    click.echo(click.style(f"正在扫描目录: {os.path.abspath(target_dir)} ...", fg='yellow'))
    files = get_all_files(target_dir, [ext.lower() for ext in allowed_ext], blacklist_folders)
    if not files: return "在指定目录中未找到任何匹配的文件。"
    file_tree = generate_file_tree(target_dir, files)
    contents = "".join([format_content(f, target_dir) for f in files])
    final_context = (
        "该项目的文件结构如下:\n"
        "```\n" f"{file_tree}\n" "```\n\n"
        "以下是项目中每个文件的完整源代码:\n\n" f"{contents}"
    )
    click.echo(click.style("上下文生成完毕。", fg='green'))
    return final_context

def create_prompt_from_directory(target_dir: str, output_file: str, allowed_ext: list, blacklist_folders: list):
    context_string = get_project_context_string(target_dir, allowed_ext, blacklist_folders)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(context_string)
    click.echo(click.style(f"处理完成，结果已写入当前目录下的 {output_file} 文件中。", fg='green', bold=True))