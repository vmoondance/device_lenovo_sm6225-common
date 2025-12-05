#!/usr/bin/env python3
"""
Fix missing architecture keys in Android.bp files.
Replaces ": {" with "android_arm: {" or "android_arm64: {" based on srcs.
"""

import re
import sys

def fix_bp_syntax(bp_file):
    print(f"Processing {bp_file}...")
    
    with open(bp_file, 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    fixed_count = 0
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check for the broken syntax ": {"
        if re.match(r'^\s*:\s*\{\s*$', line):
            # Look ahead to find srcs
            arch = None
            j = i + 1
            while j < len(lines) and j < i + 10: # Look ahead a few lines
                if 'srcs:' in lines[j]:
                    if '/lib/' in lines[j]:
                        arch = 'android_arm'
                    elif '/lib64/' in lines[j]:
                        arch = 'android_arm64'
                    break
                j += 1
            
            if arch:
                indent = line.split(':')[0]
                new_line = f"{indent}{arch}: {{\n"
                new_lines.append(new_line)
                fixed_count += 1
                print(f"  Fixed line {i+1}: inferred {arch}")
            else:
                print(f"  ⚠️ Could not infer arch for line {i+1}, keeping as is")
                new_lines.append(line)
        else:
            new_lines.append(line)
        
        i += 1
    
    with open(bp_file, 'w') as f:
        f.writelines(new_lines)
    
    print(f"✅ Fixed {fixed_count} syntax errors in {bp_file}\n")

if __name__ == '__main__':
    files = [
        '/home/blacksun/Lineage23/vendor/lenovo/tb128fu/Android.bp',
        '/home/blacksun/Lineage23/vendor/lenovo/sm6225-common/Android.bp',
    ]
    
    for f in files:
        fix_bp_syntax(f)
