#!/usr/bin/env python3
"""
Fix ELF check issues for modules with missing 32-bit dependencies,
renamed shim libraries, or unresolved symbols.
"""

import re
import sys

# Modules that need check_elf_files: false
MODULES_CHECK_ELF_FALSE = [
    "libxml",
    "libconfigdb",
    "libwfdmmsrc_system",
    "libwfdinput",
    "libwfdservice",
    "libwfdnative",
]

# Modules that need allow_undefined_symbols: true
MODULES_ALLOW_UNDEFINED = [
    "libwvhidl",
    "libwvdrmengine",
]

def add_property_to_module(content, module_name, property_name, property_value):
    """Add a property to a module if not already present."""
    # Find the module block
    pattern = rf'(cc_prebuilt_library_shared\s*\{{\s*name:\s*"{module_name}",.*?compile_multilib:\s*"[^"]+",)'
    
    match = re.search(pattern, content, flags=re.DOTALL)
    if not match:
        print(f"Warning: Module {module_name} not found")
        return content
    
    block = match.group(1)
    
    # Check if property already exists in this block
    if f'{property_name}:' in block:
        print(f"Skipping {module_name}: {property_name} already exists")
        return content
    
    # Add property after compile_multilib
    new_block = re.sub(
        r'(compile_multilib:\s*"[^"]+",)',
        rf'\1\n\t{property_name}: {property_value},',
        block
    )
    
    return content.replace(block, new_block)

def main():
    if len(sys.argv) < 2:
        print("Usage: fix_elf_checks.py <Android.bp>")
        sys.exit(1)
    
    bp_file = sys.argv[1]
    
    with open(bp_file, 'r') as f:
        content = f.read()
    
    for module in MODULES_CHECK_ELF_FALSE:
        content = add_property_to_module(content, module, "check_elf_files", "false")
        print(f"Fixed check_elf_files: {module}")
    
    for module in MODULES_ALLOW_UNDEFINED:
        content = add_property_to_module(content, module, "allow_undefined_symbols", "true")
        print(f"Fixed allow_undefined_symbols: {module}")
    
    with open(bp_file, 'w') as f:
        f.write(content)
    
    print(f"Fixed ELF checks in {bp_file}")

if __name__ == "__main__":
    main()
