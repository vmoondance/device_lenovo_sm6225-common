#!/bin/bash
#
# Copyright (C) 2016 The CyanogenMod Project
# Copyright (C) 2017-2020 The LineageOS Project
#
# SPDX-License-Identifier: Apache-2.0
#

set -e

# Load extract_utils and do some sanity checks
MY_DIR="${BASH_SOURCE%/*}"
if [[ ! -d "${MY_DIR}" ]]; then MY_DIR="${PWD}"; fi

ANDROID_ROOT="${MY_DIR}/../../.."

HELPER="${ANDROID_ROOT}/tools/extract-utils/extract_utils.sh"
if [ ! -f "${HELPER}" ]; then
  echo "Unable to find helper script at ${HELPER}"
  exit 1
fi
source "${HELPER}"

# Default to sanitizing the vendor folder before extraction
CLEAN_VENDOR=true

ONLY_COMMON=
ONLY_TARGET=
KANG=
SECTION=

while [ "${#}" -gt 0 ]; do
  case "${1}" in
  --only-common)
    ONLY_COMMON=true
    ;;
  --only-target)
    ONLY_TARGET=true
    ;;
  -n | --no-cleanup)
    CLEAN_VENDOR=false
    ;;
  -k | --kang)
    KANG="--kang"
    ;;
  -s | --section)
    SECTION="${2}"
    shift
    CLEAN_VENDOR=false
    ;;
  *)
    SRC="${1}"
    ;;
  esac
  shift
done

if [ -z "${SRC}" ]; then
  SRC="adb"
fi

function blob_fixup() {
  case "${1}" in
  system_ext/lib64/libwfdnative.so)
    "${PATCHELF}" --replace-needed libinput.so libwfdinput.so "${2}"
    ;;
  system_ext/lib*/libwfdcommonutils.so)
    "${PATCHELF}" --add-needed libgui_shim.so "${2}"
    ;;
  system_ext/lib/libwfdmmsrc_system.so)
    "${PATCHELF}" --add-needed libgui_shim.so "${2}"
    "${PATCHELF}" --add-needed libui_shim.so "${2}"
    ;;
  system_ext/lib/libwfdservice.so)
    "${PATCHELF}" --add-needed libwfdservice_shim.so "${2}"
    ;;
  vendor/lib64/vendor.qti.hardware.camera.postproc@1.0-service-impl.so)
    hexdump -ve '1/1 "%.2X"' "${2}" | sed "s/130A0094/1F2003D5/g" | xxd -r -p >"/tmp/${1##*/}"
    mv "/tmp/${1##*/}" "${2}"
    ;;
  system_ext/lib64/libqti_workloadclassifiermodel.so)
    "${PATCHELF}" --replace-needed libtflite.so libtflite.tb128fu.so "${2}"
    ;;
  system_ext/lib64/*.so | system_ext/lib/*.so | vendor/lib64/*.so | vendor/lib/*.so)
    if grep -q "libhidlbase.so" "${2}"; then
      "${PATCHELF}" --replace-needed libhidlbase.so libhidlbase-v32.so "${2}"
    fi
    if grep -q "libui.so" "${2}"; then
      "${PATCHELF}" --replace-needed libui.so libui-v34.so "${2}"
    fi
    if grep -q "libbinder.so" "${2}"; then
      "${PATCHELF}" --replace-needed libbinder.so libbinder_shim.so "${2}"
    fi
    if grep -q "libmeminfo.so" "${2}"; then
      "${PATCHELF}" --replace-needed libmeminfo.so libmeminfo_shim.so "${2}"
    fi
    if grep -q "libprocessgroup.so" "${2}"; then
      "${PATCHELF}" --replace-needed libprocessgroup.so libprocessgroup_shim.so "${2}"
    fi
    if grep -q "libcamera_metadata.so" "${2}"; then
      "${PATCHELF}" --replace-needed libcamera_metadata.so libcamera_metadata_shim.so "${2}"
    fi
    ;;
  esac
}

if [ -z "${ONLY_TARGET}" ]; then
  # Initialize the helper for common device
  setup_vendor "${DEVICE_COMMON}" "${VENDOR}" "${ANDROID_ROOT}" true "${CLEAN_VENDOR}"

  extract "${MY_DIR}/proprietary-files.txt" "${SRC}" "${KANG}" --section "${SECTION}"
  if [ -s "${MY_DIR}/proprietary-files-recovery.txt" ]; then
    extract "${MY_DIR}/proprietary-files-recovery.txt" "${SRC}" "${KANG}" --section "${SECTION}"
  fi
fi

if [ -z "${ONLY_COMMON}" ] && [ -s "${MY_DIR}/../${DEVICE}/proprietary-files.txt" ]; then
  # Reinitialize the helper for device
  source "${MY_DIR}/../${DEVICE}/extract-files.sh"
  setup_vendor "${DEVICE}" "${VENDOR}" "${ANDROID_ROOT}" false "${CLEAN_VENDOR}"

  extract "${MY_DIR}/../${DEVICE}/proprietary-files.txt" "${SRC}" "${KANG}" --section "${SECTION}"
  if [ -s "${MY_DIR}/../${DEVICE}/proprietary-files-recovery.txt" ]; then
    extract "${MY_DIR}/../${DEVICE}/proprietary-files-recovery.txt" "${SRC}" "${KANG}" --section "${SECTION}"
  fi
fi

"${MY_DIR}/setup-makefiles.sh"
