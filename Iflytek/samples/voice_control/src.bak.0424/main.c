/*
 * author: WhisperHear <1348351139@qq.com>
 * github: https://github.com/WhisperHear
 * date:   2017.12.26
 * brief:
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * version 3 as published by the Free Software Foundation.
 */

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include "voice.h"

int main(int argc, char *argv[])
{
	voice_init(NETWORK_CONNECTED, "5ad6f5c5", "44ee05352ba9459aaca3205c421f5e4c", "default");
	/* 设置输出声音格式：(详见参数列表)
	 * 发音人 语速 音量 语调 不含背景音*/
	set_voice_params((char *)"xiaoyan", 50, 50, 50, 0);
	open_voice_recognition_chat_control();
	return 0;
}
