import sys
import re

def fix_wfd_deps(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    # Regex to find libwfdservice definition and its android_arm shared_libs
    # We look for the module, then the android_arm block, then shared_libs
    # This is a bit complex with regex, so we'll do a simpler approach:
    # Iterate lines, find module, find target, find android_arm, find shared_libs, modify line.
    
    lines = content.splitlines()
    new_lines = []
    in_libwfdservice = False
    in_android_arm = False
    in_shared_libs = False
    
    for line in lines:
        if 'name: "libwfdservice",' in line:
            in_libwfdservice = True
        
        if in_libwfdservice and 'android_arm: {' in line:
            in_android_arm = True
        
        if in_libwfdservice and in_android_arm and 'shared_libs: [' in line:
            # Remove the conflicting dependency
            line = line.replace('"android.media.audio.common.types-V1-cpp", ', '')
            line = line.replace(', "android.media.audio.common.types-V1-cpp"', '') # Handle end of list case
            # Also handle if it's the only item or formatted differently?
            # The file format is usually: shared_libs: ["liba", "libb", ...],
            # Let's be robust.
            if "android.media.audio.common.types-V1-cpp" in line:
                 line = line.replace('"android.media.audio.common.types-V1-cpp"', '')
                 # Clean up double commas if any
                 line = line.replace(', ,', ',')
                 line = line.replace('[,', '[')
                 line = line.replace(', ]', ' ]')
            
        if in_libwfdservice and in_android_arm and '},' in line:
            in_android_arm = False
            
        if in_libwfdservice and '}' in line and not in_android_arm: # End of module (roughly)
             # Resetting at the end of module is tricky with nested braces.
             # But since we only care about android_arm inside libwfdservice, once we exit android_arm we are mostly done for this module.
             pass

        if in_libwfdservice and line.strip() == '}':
             in_libwfdservice = False

        new_lines.append(line)

    with open(file_path, 'w') as f:
        f.write('\n'.join(new_lines) + '\n')
    print(f"Processed {file_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        fix_wfd_deps(sys.argv[1])
    else:
        print("Usage: python3 fix_wfd_deps.py <path_to_android_bp>")
