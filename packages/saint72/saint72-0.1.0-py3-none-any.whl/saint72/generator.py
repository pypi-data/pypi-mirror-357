import os

def create_code_file(filename="saint72_generated.py", code="# Ваш код здесь"):
    project_root = os.getcwd()
    file_path = os.path.join(project_root, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)
    return file_path
