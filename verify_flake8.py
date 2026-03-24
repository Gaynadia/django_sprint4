#!/usr/bin/env python
"""Verify flake8 fixes."""
import subprocess
import sys

files = [
    'check_project.py',
    'blogicum/blog/models.py',
    'blogicum/blog/urls.py'
]

result = subprocess.run(
    [sys.executable, '-m', 'flake8'] + files,
    capture_output=True,
    text=True
)

print("Output:")
if result.stdout:
    print(result.stdout)
else:
    print("No errors found!")

if result.stderr:
    print("Errors:")
    print(result.stderr)

print(f"\nReturn code: {result.returncode}")
sys.exit(result.returncode)
