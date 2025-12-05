#!/usr/bin/env python3
import sys

def add_imports(bp_file, imports_to_add):
    with open(bp_file, 'r') as f:
        lines = f.readlines()

    existing_imports = []
    
    # First pass: collect existing imports
    in_soong_namespace = False
    in_imports = False
    
    for line in lines:
        if 'soong_namespace {' in line:
            in_soong_namespace = True
        if in_soong_namespace and 'imports: [' in line:
            in_imports = True
            continue
        if in_imports and '],' in line:
            in_imports = False
            continue
        if in_imports:
            # Extract import path
            import_match = line.strip().replace('"', '').replace(',', '').strip()
            if import_match:
                existing_imports.append(import_match)

    # Second pass: add new imports (skip existing ones)
    new_lines = []
    in_soong_namespace = False
    in_imports = False
    imports_added = False
    
    for line in lines:
        if 'soong_namespace {' in line:
            in_soong_namespace = True
            new_lines.append(line)
            continue

        if in_soong_namespace and 'imports: [' in line:
            in_imports = True
            new_lines.append(line)
            # Add our imports here (only if not already present)
            for imp in imports_to_add:
                if imp not in existing_imports:
                    new_lines.append(f'\t\t"{imp}",\n')
                    imports_added = True
            continue

        if in_imports and '],' in line:
            in_imports = False
            new_lines.append(line)
            continue
        
        if in_soong_namespace and '}' in line and not in_imports:
             in_soong_namespace = False
             new_lines.append(line)
             continue

        new_lines.append(line)

    with open(bp_file, 'w') as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        bp_file = sys.argv[1]
    else:
        bp_file = "vendor/lenovo/sm6225-common/Android.bp"

    imports = [
        "vendor/qcom/opensource/commonsys/display",
        "vendor/qcom/opensource/commonsys-intf/display",
        "vendor/qcom/opensource/display",
        "hardware/qcom-caf/sm8250/display/libdebug",
        "device/lenovo/sm6225-common",
        "hardware/qcom-caf/wlan/cld80211-lib",
        "vendor/qcom/opensource/dataservices",
    ]
    add_imports(bp_file, imports)
    print(f"Added imports to {bp_file}")
