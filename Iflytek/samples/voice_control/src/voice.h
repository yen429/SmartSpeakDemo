/*
 * author: WhisperHear <1348351139@qq.com>
 * github: https://github.com/WhisperHear
 * date:   2017.12.26
 * brief:
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * version 3 as published by the Free Software Foundation.
 */
 
#ifndef __VOICE_H_
#define __VOICE_H_

#include <pthread.h>
#include <unistd.h>
#include <signal.h>
#include "qisr.h"
#include "qtts.h"
#include "qivw.h"

#include "msp_cmn.h"
#include "msp_errors.h"

/*
 *声音模块
 */

#define VOICE_PIN 22          //蜂鸣器阵脚
#define VOICE_LIGHT_PIN  1    //语音控制指示灯，表示说话时灯亮，可以识别时灯灭
#define VOICE_DETECT_PIN 0    //检测有无声音发出的阵脚, 此针脚引发一个中断
#define RECORD_CMD_LEN 150
#define SWITCH_ON   48       //开关标识，开
#define SWITCH_OFF  49       //开关标识，关
#define NETWORK_CONNECTED    111 //网络连接成功标志
#define NETWORK_DISCONNECTED 222 //网络连接失败标志

#define TULING123_API_KEY_LEN   50     //图灵机器人API的key值
#define XFYUN_APPID_LEN         20     //科大讯飞开发包的APPID
#define USB_AUDIO_ADDR_LEN      50     //USB声卡的地址信息
#define SMART_REPLY_TEXT_LEN    1024   //存放图灵机器人接口智能回复的文字的空间大小
#define SMART_REPLY_CODE_LEN    10     //存放图灵机器人接口智能回复文字类型的空间大小
#define CONDITION_TEXT_LEN      350    //存放机器人自身环境状态信息的空间的大小，如果添加了其他的环境信息记得增大此值，否则会造成溢出。
#define ARECORD_PROCESS_CMD_LEN 117+USB_AUDIO_ADDR_LEN //录音进程命令字符数量
#define PARAMS_LEN              1024   //输出语音的参数空间大小

//科大讯飞语音读写需要
//#define BUFFER_SIZE     40960
#define BUFFER_SIZE     4096 //40960
#define FRAME_LEN       640 
#define HINTS_SIZE      100


//State Control
#define INITIAL_STATE  0x00
#define IDLE_STATE     0x01
#define LISTEN_STATE    0x02
#define THINK_STATE    0x03
#define SPEAK_STATE 0x04

typedef struct {
	int voice_main_switch;                       //声音总开关（如果语音初始化失败，则为关闭状态！）
	int recongnition_switch;                     //标识当前是否打开语音识别 （高）
	int sound_box_ongoing_flag;                  //标识当前音箱状态，等于0为没有说话，小于0为正在说话
	char question_text[BUFFER_SIZE];   //音频转换成文字后保存到这里
	const char *answer_jason;
	const char *answer_text;
	char smart_reply_text[SMART_REPLY_TEXT_LEN]; //放图灵机器人接口智能回复的文字
	char smart_reply_code[SMART_REPLY_CODE_LEN]; //存放图灵机器人接口智能回复文字的类型，比如天气、股票、市场价格
	char condition_text[CONDITION_TEXT_LEN];     //存放机器人自身环境状态信息的空间（播放时，就播放这些文字）

	char output_voice_params[PARAMS_LEN];        //音频输出的参数包括：发音人，语速，音量，语调，是否有背景音乐
	pthread_mutex_t mutex_voice_params;	     //声音参数内存空间的线程锁

	char tuling123_api_key[TULING123_API_KEY_LEN];             //图灵机器人API的key值（字符串长度暂定）
    char xfyun_appid[XFYUN_APPID_LEN];                         //科大讯飞提供的树莓派开发包的appid; （字符串长度暂定）
	char usb_audio_addr[USB_AUDIO_ADDR_LEN];                   //USB声卡的地址信息（字符串长度暂定）
	int state_machine;
	snd_pcm_t* pcm_playback_handle;
	snd_pcm_t* pcm_capture_handle;
}Voice;

/*
 *功能：初始化语音模块
 *xfyun_appid：科大讯飞开发包的APPID
 */
extern void voice_init(const char *xfyun_appid, const char *usb_audio_addr);

/*
 *功能：开启语音识别控制
 *返回值：成功返回0，失败返回-1
 *说明：打开后在检测到声音（声音大于一定的阀值）后才进行录音，识别。
 */
extern int start_voice_recognition(void);

#endif
