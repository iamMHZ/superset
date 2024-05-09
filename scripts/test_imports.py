import os
import re
import subprocess
import sys
from typing import List

EXCLUDE_FILE_PATTERNS: List[str] = [
    "migrations/",
]


def test_module_import(file_path: str) -> str | None:
    """Test if a module can be imported independently"""
    module_path = file_path.replace(".py", "").replace("/", ".")
    # if module_path.endswith("__init__"):
    #    module_path = module_path.replace(".__init__", "")
    splitted = ["superset"] + module_path.split(".")
    from_part = ".".join(splitted[:-1])
    import_part = splitted[-1]
    import_statement = f"from {from_part} import {import_part}"
    try:
        subprocess.run(
            ["python", "-c", import_statement],
            check=True,
        )
        return None
    except subprocess.CalledProcessError as e:
        if e.stderr:
            print(f"ERROR: {e.stderr}")
        return e.stderr


def get_all_module_paths(package_path: str) -> list[str]:
    paths = []
    for root, dirs, files in os.walk(package_path):
        for file in files:
            filepath = os.path.normpath(os.path.join(root, file))
            relative_path = os.path.relpath(filepath, package_path)
            if file.endswith(".py") and all(
                not re.match(pattern, relative_path)
                for pattern in EXCLUDE_FILE_PATTERNS
            ):
                paths.append(relative_path)
    return paths


def test_import(package_path: str) -> None:
    """Test importability of all modules within a package"""
    error_count = 0
    processed_count = 0
    paths = get_all_module_paths(package_path)
    for path in sorted(paths):
        error = test_module_import(path)
        processed_count += 1
        message = f"[{processed_count}/{len(paths)}] {path}"
        if error:
            print(f"❌ {message}")
            error_count += 1
        else:
            print(f"✅ {message}")

    print(f"Total errors: {error_count}")
    if error_count:
        sys.exit(1)


if __name__ == "__main__":
    package_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "../superset")
    )
    print(f"Processing package located at: {package_path}")
    test_import(package_path)
