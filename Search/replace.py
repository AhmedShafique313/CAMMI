import os

def replace_in_txt_files(input_folder, old_str, new_str):
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith(".txt"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    if old_str in content:
                        new_content = content.replace(old_str, new_str)
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        print(f"Updated: {file_path}")
                    else:
                        print(f"No changes: {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    input_folder = r"C:\Users\Kavtech AI Engineer\Documents\CAMMI\Bucket\downloads\input"
    old_str = "s3://cammi/output/"
    new_str = "output/"
    replace_in_txt_files(input_folder, old_str, new_str)
