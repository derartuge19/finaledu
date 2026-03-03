#!/usr/bin/env python3
"""
Script to fix the bulk_issue_from_excel function
"""
import re

def fix_bulk_issue_function():
    """Fix the bulk_issue_from_excel function structure"""
    
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the function and fix indentation
    start_marker = "@app.post(\"/api/templates/bulk-issue-excel\")"
    end_marker = "# ─────────────────────────────────────────────────────────────────────────────"
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker, start_idx)
    
    if start_idx == -1 or end_idx == -1:
        print("❌ Could not find bulk_issue_from_excel function")
        return
    
    # Extract the function
    function_content = content[start_idx:end_idx]
    
    # Fix indentation issues
    fixed_content = re.sub(r'^    ', '        ', function_content, flags=re.MULTILINE)
    
    # Replace the function in the file
    new_content = content[:start_idx] + fixed_content + content[end_idx:]
    
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Fixed bulk_issue_from_excel function indentation")

if __name__ == "__main__":
    fix_bulk_issue_function()
