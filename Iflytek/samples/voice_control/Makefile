#common makefile header

TOP_PATH = $(shell pwd)
DIR_INC = ../../include
          
DIR_BIN = ../../bin
DIR_LIB = ../../libs
SRC_PATH = $(TOP_PATH)/src

TARGET	= voice_control
BIN_TARGET = $(DIR_BIN)/$(TARGET)

CROSS_COMPILE = 
CFLAGS = -g -Wall -I$(DIR_INC)

#可根据实际需要修改，选择所需平台SDK，默认为x64或x86平台。
ifdef ARM_BUILD
LDFLAGS := -L$(DIR_LIB)/arm
else
LDFLAGS := -L$(DIR_LIB)/x64 
endif

LDFLAGS += -lmsc -lrt -ldl -lpthread -lasound -lifly

#OBJECTS := $(patsubst %.c,%.o,$(wildcard *.c))
OBJECTS := $(TOP_PATH)/src/main.c \
           $(TOP_PATH)/src/voice.c \
           $(TOP_PATH)/src/pcm.c \
		   $(TOP_PATH)/src/fifo.c 
		   

$(BIN_TARGET) : $(OBJECTS)
	$(CROSS_COMPILE)g++ $(CFLAGS) $^ -o $@ $(LDFLAGS)

%.o : %.c
	$(CROSS_COMPILE)g++ -c $(CFLAGS) $< -o $@
clean:
	@rm -f *.o $(BIN_TARGET)

.PHONY:clean

#common makefile foot
