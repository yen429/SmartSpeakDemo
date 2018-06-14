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
#include <alsa/asoundlib.h>
#include "voice.h"

int main(int argc, char *argv[])
{
	// xfyun appid & device name
	voice_init("5ad6f5c5", "default");
	start_voice_recognition();
	return 0;
}
