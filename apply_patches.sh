#!/bin/bash
#
# Apply patches to LineageOS source after repo sync
# Run this from the root of your LineageOS tree
#

DEVICE_COMMON_PATH="device/lenovo/sm6225-common"
PATCHES_DIR="${DEVICE_COMMON_PATH}/patches"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

apply_patches() {
    local patch_dir="$1"
    local target_dir="$2"
    
    if [ ! -d "$patch_dir" ]; then
        echo -e "${YELLOW}No patches found in: $patch_dir${NC}"
        return 0
    fi
    
    for patch_file in "$patch_dir"/*.patch; do
        if [ -f "$patch_file" ]; then
            echo -e "${GREEN}Applying: $(basename $patch_file) to $target_dir${NC}"
            cd "$target_dir"
            
            # Check if patch is already applied
            if git apply --check "$patch_file" 2>/dev/null; then
                git apply "$patch_file"
                if [ $? -eq 0 ]; then
                    echo -e "${GREEN}  ✓ Applied successfully${NC}"
                else
                    echo -e "${RED}  ✗ Failed to apply${NC}"
                fi
            else
                echo -e "${YELLOW}  ⚠ Patch already applied or conflicts${NC}"
            fi
            
            cd - > /dev/null
        fi
    done
}

echo "================================================"
echo "  Applying patches for sm6225-common"
echo "================================================"

# Get the root of the Android tree
if [ -z "$ANDROID_BUILD_TOP" ]; then
    ANDROID_BUILD_TOP=$(pwd)
fi

cd "$ANDROID_BUILD_TOP"

# Apply Display HAL patches
if [ -d "${PATCHES_DIR}/hardware_qcom-caf_sm8250_display" ]; then
    apply_patches "${ANDROID_BUILD_TOP}/${PATCHES_DIR}/hardware_qcom-caf_sm8250_display" \
                  "${ANDROID_BUILD_TOP}/hardware/qcom-caf/sm8250/display"
fi

# Apply Audio HAL patches (if any)
if [ -d "${PATCHES_DIR}/hardware_qcom-caf_sm8250_audio" ]; then
    apply_patches "${ANDROID_BUILD_TOP}/${PATCHES_DIR}/hardware_qcom-caf_sm8250_audio" \
                  "${ANDROID_BUILD_TOP}/hardware/qcom-caf/sm8250/audio"
fi

# Apply kernel patches (if any)
if [ -d "${PATCHES_DIR}/kernel_lenovo_tb128fu" ]; then
    apply_patches "${ANDROID_BUILD_TOP}/${PATCHES_DIR}/kernel_lenovo_tb128fu" \
                  "${ANDROID_BUILD_TOP}/kernel/lenovo/tb128fu"
fi

echo ""
echo "================================================"
echo "  Patches applied. Run 'source build/envsetup.sh' and build."
echo "================================================"
