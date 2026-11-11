import re
import subprocess
import sys

# Verify pytest is available
pytest_check = subprocess.run(
    ["python3", "-m", "pytest", "--version"],
    capture_output=True,
    text=True,
)
if pytest_check.returncode != 0:
    sys.stderr.write("Error: pytest is unavailable\n")
    sys.exit(1)

cmd = ["python3", "-m", "pytest", "tests/test_matrix_calculator.py"]
cmd_str = " ".join(cmd)
print(f"Command: {cmd_str}")

proc = subprocess.run(cmd, capture_output=True, text=True)

if proc.stdout:
    print(proc.stdout, end="")
if proc.stderr:
    sys.stderr.write(proc.stderr)

match = re.search(r"(\d+)\s+passed", proc.stdout)
passed_count = int(match.group(1)) if match else 0
print(f"Tests passed: {passed_count}")

if passed_count == 0:
    sys.exit(1)

sys.exit(proc.returncode)
