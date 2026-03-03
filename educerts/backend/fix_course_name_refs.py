#!/usr/bin/env python3
"""
Script to remove all course_name references from main.py
"""
import re

def fix_course_name_references():
    """Remove all course_name references from main.py"""
    
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove course_name from data_payload references
    content = re.sub(r'"course_name": item\["course_name"\],', '', content)
    content = re.sub(r'"course": item\["course_name"\], # Alias', '', content)
    content = re.sub(r'"subject": item\["course_name"\], # Alias', '', content)
    
    # Remove course_name from database model creation
    content = re.sub(r'course_name=item\["course_name"\],', '', content)
    
    # Remove course_name from issued_certs
    content = re.sub(r'"course_name": item\["course_name"\], ', '', content)
    
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Removed all course_name references from main.py")

if __name__ == "__main__":
    fix_course_name_references()
