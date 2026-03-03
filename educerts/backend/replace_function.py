import re

# Read the current main.py
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Read the fixed function
with open('bulk_issue_fixed.py', 'r', encoding='utf-8') as f:
    fixed_function = f.read()

# Find the start of the broken function
start_pattern = '@app.post("/api/templates/bulk-issue-excel")'
start_idx = content.find(start_pattern)

if start_idx != -1:
    # Find the end of the function (next function or section)
    end_pattern = '# ─────────────────────────────────────────────────────────────────────────────'
    end_idx = content.find(end_pattern, start_idx)
    
    if end_idx == -1:
        # If no end marker found, go to end of file
        end_idx = len(content)
    
    # Replace the broken function
    new_content = content[:start_idx] + fixed_function + content[end_idx:]
    
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print('✅ Successfully replaced bulk_issue_from_excel function')
else:
    print('❌ Could not find bulk_issue_from_excel function')
