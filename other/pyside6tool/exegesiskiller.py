import os
import re

def remove_comments_from_code(file_path):
    """读取文件内容，移除注释并覆盖写回文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()

    # 移除单行注释
    code = re.sub(r'#.*', '', code)

    # 移除多行注释（使用三引号）
    code = re.sub(r'(""".*?"""|\'\'\'.*?\'\'\')', '', code, flags=re.DOTALL)

    # 去掉多余的空行，保留行数一致
    lines = code.splitlines()
    code_without_comments = "\n".join(line if line.strip() else "" for line in lines)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(code_without_comments)

def process_directory(directory_path):
    """遍历目录，找到所有 .py 文件并处理"""
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                print(f"Processing: {file_path}")
                remove_comments_from_code(file_path)

if __name__ == "__main__":
    target_directory = r"D:\Code\QQbot\Code\QQbot"
    process_directory(target_directory)
    print("注释清理完成。")
