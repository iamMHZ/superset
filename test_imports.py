import os

# mypy: ignore-errors

# pylint: skip-file
# pylint: disable-all


def generate_import_statements(root_dir):
    import_statements = set()
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".py"):
                module_path = os.path.relpath(os.path.join(dirpath, filename), root_dir)
                module_name = os.path.splitext(module_path.replace(os.path.sep, "."))[0]
                splitted = module_name.split(".")
                if splitted[-1] == "__init__":
                    splitted.pop()
                if len(splitted) > 1 and "migration" not in module_path:
                    package = ".".join(splitted[:-1])
                    import_statements.add(
                        f"from superset.{package} import {splitted[-1]}"
                    )
    return sorted(import_statements)


if __name__ == "__main__":
    root_dir = "superset"
    import_statements = generate_import_statements(root_dir)
    for statement in import_statements:
        print(statement)
