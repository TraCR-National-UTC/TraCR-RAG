import os
import re
import shutil

def copy_files_with_numbered_parentheses(root_dir):
    """
    Find files with parentheses containing numbers (e.g., file(12).pdf)
    and create a copy renamed with underscores (e.g., file(_12_).pdf)
    in the same directory.
    """
    # Pattern to match filenames containing (number)
    pattern = re.compile(r"\((\d+)\)")

    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            match = pattern.search(filename)
            if match:
                number = match.group(1)
                new_filename = pattern.sub(f"(_{number}_)", filename)
                src_path = os.path.join(dirpath, filename)
                dst_path = os.path.join(dirpath, new_filename)

                # Only copy if destination file doesn’t already exist
                if not os.path.exists(dst_path):
                    shutil.copy2(src_path, dst_path)
                    print(f"Copied:\n  {src_path}\n→ {dst_path}")
                else:
                    print(f"Skipped (already exists): {dst_path}")

if __name__ == "__main__":
    directory = input("Enter the directory path to search: ").strip()
    copy_files_with_numbered_parentheses(directory)
