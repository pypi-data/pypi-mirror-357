file_path = r"E:\python_project\OSS\imagemagick\2025_6_20 error"

try:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        print(content)
except FileNotFoundError:
    print(f"文件不存在：{file_path}")
except UnicodeDecodeError:
    print("无法用 UTF-8 解码该文件；请确认它的实际编码，或尝试其他 encoding。")
except Exception as e:
    print(f"读取文件时发生错误：{e}")