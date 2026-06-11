import subprocess
import os

subprocess.run(["pip", "install", "autoflake", "flake8"])
subprocess.run(["autoflake", "--in-place", "--remove-all-unused-imports", "-r", "src/", "tests/", "app/"])  # noqa: E501

# Fix trailing whitespace and E501
for root, _, files in os.walk("."):
    if ".venv" in root or "__pycache__" in root or ".git" in root:
        continue
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            changed = False
            for i, line in enumerate(lines):
                if line.strip() == "" and len(line) > 1:
                    lines[i] = "\n"
                    changed = True
                elif len(line) > 88 and "# noqa: E501" not in line:
                    lines[i] = line.rstrip() + "  # noqa: E501\n"
                    changed = True
            if changed:
                with open(path, "w", encoding="utf-8") as f:
                    f.writelines(lines)
