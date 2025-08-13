# Fix the portfolio endpoint in app.js

import os

file_path = r"L:\Storage\NVMe\projects\wasenet\opusdev\js\app.js"

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the specific line
old_line = "return `/photos/user/${this.user?.uid}?portfolio_only=true`;"
new_line = "return '/photos/my-photos?portfolio_only=true';"

if old_line in content:
    content = content.replace(old_line, new_line)
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Successfully updated portfolio endpoint in app.js")
    print(f"Changed: {old_line}")
    print(f"To: {new_line}")
else:
    print("Line not found in file - it may have already been updated")

# Verify the change
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines[320:330], start=321):
        print(f"Line {i}: {line.rstrip()}")
