import os
import re
import subprocess
from typing import List

EXCLUDE_FILE_PATTERNS: List[str] = [
    "migrations/",
]


def test_module_import(file_path: str) -> None:
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
        # print(f"✅ {import_statement}")
    except subprocess.CalledProcessError as e:
        print(f"❌ {import_statement}")
        if e.stderr:
            print(f"ERROR: {e.stderr}")


def test_import(package_path: str) -> None:
    """Test importability of all modules within a package"""
    for root, dirs, files in os.walk(package_path):
        for file in files:
            filepath = os.path.normpath(os.path.join(root, file))
            relative_path = os.path.relpath(filepath, package_path)
            if file.endswith(".py") and all(
                not re.match(pattern, relative_path)
                for pattern in EXCLUDE_FILE_PATTERNS
            ):
                test_module_import(relative_path)


if __name__ == "__main__":
    package_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "../superset")
    )
    print(f"Processing package located at: {package_path}")
    test_import(package_path)
