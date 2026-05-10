def read_code_file(path):
    with open(path, "r", encoding="utf-8") as file:
        return file.read()
    
def save_report(content, path="outputs/report.md"):
    with open(path, "w", encoding="utf-8") as file:
        file.write(content)