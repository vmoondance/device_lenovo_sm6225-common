DTBO_PREBUILT_SRC := $(BOARD_PREBUILT_DTBOIMAGE)
INSTALLED_DTBOIMAGE_TARGET := $(PRODUCT_OUT)/dtbo.img
DTBO_PARTITION_SIZE := $(BOARD_DTBOIMG_PARTITION_SIZE)
AVBTOOL := $(HOST_OUT_EXECUTABLES)/avbtool

$(INSTALLED_DTBOIMAGE_TARGET): $(DTBO_PREBUILT_SRC)
	@echo "Copy prebuilt DTBO $(DTBO_PREBUILT_SRC) -> $@"
	@mkdir -p $(dir $@)
	$(hide) cp -f $< $@
	$(hide) if [ -x "$(HOST_OUT_EXECUTABLES)/mkdtimg" ]; then \
	  sz="$$($(HOST_OUT_EXECUTABLES)/mkdtimg dump $@ | awk '/total_size/{print $$3; exit}')"; \
	  if [ -n "$$sz" ]; then \
	    pagesize=4096; \
	    rounded=$$(( ( ($$sz + pagesize - 1) / pagesize ) * pagesize )); \
	    echo "Truncating DTBO to $$rounded bytes (from $$sz)"; \
	    truncate -s $$rounded $@; \
	  fi; \
	fi
	$(hide) if [ -x "$(AVBTOOL)" ] && [ -n "$(DTBO_PARTITION_SIZE)" ]; then \
	  "$(AVBTOOL)" add_hash_footer --image $@ --partition_size $(DTBO_PARTITION_SIZE) --partition_name dtbo; \
	fi
