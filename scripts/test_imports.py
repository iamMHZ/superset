#!/usr/bin/env python

# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
import argparse
import os
import re
import subprocess
import sys
from concurrent.futures import as_completed, ThreadPoolExecutor
from typing import List

EXCLUDE_FILE_PATTERNS: List[str] = [
    "migrations/",
]


def test_module_import(file_path: str) -> str | None:
    """Test if a module can be imported independently"""
    module_path = file_path.replace(".py", "").replace("/", ".")
    splitted = ["superset"] + module_path.split(".")
    from_part = ".".join(splitted[:-1])
    import_part = splitted[-1]
    import_statement = f"from {from_part} import {import_part}"
    try:
        subprocess.run(
            ["python", "-c", import_statement],
            stdout=subprocess.PIPE,  # Redirect stdout to PIPE
            stderr=subprocess.PIPE,  # Redirect stderr to PIPE
            check=True,
        )
        return None
    except subprocess.CalledProcessError as e:
        if e.stderr:
            return e.stderr.decode().strip()
        return str(e)


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


def test_import(package_path: str, max_workers: int | None = None) -> None:
    """Test importability of all modules within a package"""
    error_count = 0
    processed_count = 0
    paths = get_all_module_paths(package_path)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(test_module_import, path): path for path in paths}
        for future in as_completed(futures):  # Use as_completed
            path = futures[future]
            processed_count += 1
            message = f"[{processed_count}/{len(paths)}] {path}"
            error = future.result()
            if error:
                print(f"❌ {message}")
                print(error)
                error_count += 1
            else:
                print(f"✅ {message}")

    print(f"Total errors: {error_count}")
    if error_count:
        sys.exit(1)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Test importability of all modules within a package with parallel execution support."
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=os.cpu_count(),
        help="Number of worker threads for parallel execution (default is number of CPU cores)",
    )
    parser.add_argument(
        "glob",
        metavar="glob",
        type=str,
        help="Glob pattern to search for Python files",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    print(f"Processing package located at: {args.glob}")
    test_import(args.glob, args.workers)
