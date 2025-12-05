#!/usr/bin/env python3
import sys
import re

def fix_compile_multilib(bp_file, modules_to_fix):
    """
    Change compile_multilib from "both" to "64" for specified modules.
    """
    with open(bp_file, 'r') as f:
        lines = f.readlines()
    
    # Track which module we're in
    current_module = None
    in_module = False
    brace_depth = 0
    
    for i, line in enumerate(lines):
        # Check if we're starting a new cc_prebuilt_library_shared block
        if 'cc_prebuilt_library_shared {' in line:
            in_module = True
            brace_depth = 1
            current_module = None
            continue
        
        if in_module:
            # Track brace depth
            brace_depth += line.count('{')
            brace_depth -= line.count('}')
            
            # Check if this is the name line
            if current_module is None and 'name:' in line:
                for module_name in modules_to_fix:
                    if f'"{module_name}"' in line:
                        current_module = module_name
                        break
            
            # If we're in a module that needs fixing, replace compile_multilib
            if current_module and 'compile_multilib:' in line and '"both"' in line:
                lines[i] = line.replace('"both"', '"64"')
                print(f"Fixed: {current_module}")
            
            # Reset when module block closes
            if brace_depth == 0:
                in_module = False
                current_module = None
    
    with open(bp_file, 'w') as f:
        f.writelines(lines)
    
    print(f"Processed {bp_file}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        bp_file = sys.argv[1]
    else:
        bp_file = "/home/blacksun/Lineage23/vendor/lenovo/sm6225-common/Android.bp"
    
    # Modules that need to be 64-bit only
    modules_to_fix = [
        "vendor.qti.hardware.btconfigstore@1.0-impl",  # depends on bluetooth@1.0-impl-qti (64-bit only)
        "vendor.qti.hardware.btconfigstore@2.0-impl",  # depends on bluetooth@1.0-impl-qti (64-bit only)
        "vendor.qti.hardware.bluetooth_sar@1.1-impl",  # depends on bluetooth@1.0-impl-qti (64-bit only)
        "libdpmframework",  # depends on libdiag_system (64-bit only)
        "libdpmfdmgr",  # depends on libdiag_system
        "libdpmtcm",  # depends on libdpmframework, libdiag_system
        "libdpmctmgr",  # depends on libdpmframework, libdiag_system
    ]
    
    fix_compile_multilib(bp_file, modules_to_fix)
