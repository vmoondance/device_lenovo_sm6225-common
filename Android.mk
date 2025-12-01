#
# Copyright (C) 2022 The LineageOS Project
#
# SPDX-License-Identifier: Apache-2.0
#

LOCAL_PATH := $(call my-dir)

ifneq ($(filter tb128fu,$(TARGET_DEVICE)),)

include $(call all-makefiles-under,$(LOCAL_PATH))

include $(CLEAR_VARS)

endif

<<<<<<< Updated upstream
# include hardware/xiaomi/aidl/power-libperfmgr/Android.mk

=======
ifneq ($(wildcard hardware/xiaomi/aidl/power-libperfmgr/Android.mk),)
include hardware/xiaomi/aidl/power-libperfmgr/Android.mk
endif
>>>>>>> Stashed changes
