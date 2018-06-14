/*
 * author: WhisperHear <1348351139@qq.com>
 * github: https://github.com/WhisperHear
 * date:   2017.12.26
 * brief:
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * version 3 as published by the Free Software Foundation.
 *
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include "voice.h"
//#include <wiringPi.h>
#include <netdb.h>
#include <alsa/asoundlib.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include "ifly.h"

static Voice voice;

/* 合成的wav声音文件：默认wav音频头部数据 */
static wave_pcm_hdr default_wav_hdr = 
{
	{ 'R', 'I', 'F', 'F' },  // RIFF
	0,                       // File Size
	{'W', 'A', 'V', 'E'},    // WAVE
	{'f', 'm', 't', ' '},    // fmt
	16,                      // fmt_size
	1,                       // format_tag
	1,                       // channels
	16000,                   // samples_per_sec
	32000,                   // avg_bytes_per_sec
	2,                       // block_align
	16,                      // bits_per_sample
	{'d', 'a', 't', 'a'},    // data
	0                        // data size
};

/*
 * 功能：文字转声音并播放（在线播放）
 * 参数：播放的文字
 * 返回值：返回错误代码 
 */
static int text_to_speech(const char* src_text)
{
	if (NULL == src_text)
	{
		ERROR_MSG("src_text is null\n");
		return -1;
	}
	
	/******************播放声音的各种参数部分**********************/
	int rc;
	int ret = -1;
	int size;
	snd_pcm_t* handle; //PCI设备句柄
	snd_pcm_hw_params_t* pcm_params;//硬件信息和PCM流配置
	//unsigned int val;
	int dir=0;
	snd_pcm_uframes_t frames;

	int channels  = default_wav_hdr.channels; // 1
	unsigned int frequency = default_wav_hdr.samples_per_sec; // 16000
	int bit       = default_wav_hdr.bits_per_sample; // 16
	int datablock = default_wav_hdr.block_align; // 2
	
	DEBUG_MSG("[PCM Setup] Open Playback\n");
	rc=snd_pcm_open(&handle, "default", SND_PCM_STREAM_PLAYBACK, 0);
	if(rc < 0)
	{
		ERROR_MSG("open PCM device error\n");
		return -1;
	}

	snd_pcm_hw_params_alloca(&pcm_params); //分配params结构体
	if(rc < 0)
	{
		ERROR_MSG("snd_pcm_hw_params_alloca error\n");
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		return -1;
	}
	
	rc=snd_pcm_hw_params_any(handle, pcm_params);//初始化params
	if(rc < 0)
	{
		ERROR_MSG("snd_pcm_hw_params_any error\n");
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		return -1;
	}
	
	rc=snd_pcm_hw_params_set_access(handle, pcm_params, SND_PCM_ACCESS_RW_INTERLEAVED); //初始化访问权限
	if(rc < 0)
	{
		ERROR_MSG("sed_pcm_hw_set_access error\n");
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		return -1;
	}

	//采样位数
	DEBUG_MSG("[PCM Setup] bit=%d\n", bit);
	switch(bit/8)
	{
		case 1:
			DEBUG_MSG("[PCM Setup] SND_PCM_FORMAT_U8\n");
			snd_pcm_hw_params_set_format(handle, pcm_params, SND_PCM_FORMAT_U8);
			break;
        case 2:
			DEBUG_MSG("[PCM Setup] SND_PCM_FORMAT_S16_LE\n");
			snd_pcm_hw_params_set_format(handle, pcm_params, SND_PCM_FORMAT_S16_LE);
			break;
		case 3:
			DEBUG_MSG("[PCM Setup] SND_PCM_FORMAT_S24_LE\n");
			snd_pcm_hw_params_set_format(handle, pcm_params, SND_PCM_FORMAT_S24_LE);
			break;
		default:
			rc = -1;
			break;
	}
	
	if (rc < 0)	
	{
		ERROR_MSG("snd_pcm_hw_params_set_format error\n");
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		return -1;
	}
	
	DEBUG_MSG("[PCM Setup] channels=%d\n", channels);
	rc=snd_pcm_hw_params_set_channels(handle, pcm_params, channels); //设置声道,1表示单声>道，2表示立体声
	if(rc < 0)
	{
		ERROR_MSG("snd_pcm_hw_params_set_channels error\n");
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		return -1;
	}
	
	DEBUG_MSG("[PCM Setup] frequency=%d\n", frequency);
	rc=snd_pcm_hw_params_set_rate_near(handle, pcm_params, &frequency, &dir); //设置>频率
	if(rc < 0)
	{
		ERROR_MSG("snd_pcm_hw_params_set_rate_near error\n");
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		return -1;
	}

	rc = snd_pcm_hw_params(handle, pcm_params);
	if(rc < 0)
	{
		ERROR_MSG("snd_pcm_hw_params error\n");
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		return -1;
	}

	//下面的frames和size好像都没用了，因为参数传递进来了
	rc=snd_pcm_hw_params_get_period_size(pcm_params, &frames, &dir); /*获取周期长度*/
	if(rc < 0)
	{
		ERROR_MSG("snd_pcm_hw_params_get_period_size error\n");
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		return -1;
	}

	size = frames * datablock; /*4 代表数据快长度, frames = 512, datablock =2*/

	/**********************************tts的部分************************************/
	ret = -1;
	const char*  sessionID    = NULL;
	unsigned int audio_len    = 0;
	wave_pcm_hdr wav_hdr      = default_wav_hdr;
	int synth_status = MSP_TTS_FLAG_STILL_HAVE_DATA;
	//const char* params = "voice_name = xiaoyan, text_encoding = utf8, sample_rate = 16000, speed = 50, volume = 50, pitch = 50, rdn = 2";

	/* 开始合成 */
	pthread_mutex_lock(&(voice.mutex_voice_params)); //申请锁
	sessionID = QTTSSessionBegin(voice.output_voice_params, &ret);
	pthread_mutex_unlock(&(voice.mutex_voice_params)); //释放锁
	if (MSP_SUCCESS != ret)
	{
		ERROR_MSG("QTTSSessionBegin failed, error code: %d\n", ret);
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		return ret;
	}
	
	ret = QTTSTextPut(sessionID, src_text, (unsigned int)strlen(src_text), NULL);
	if (MSP_SUCCESS != ret)
	{
		ERROR_MSG("QTTSTextPut failed, error code: %d\n",ret);
		QTTSSessionEnd(sessionID, "TextPutError");
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		return ret;
	}

	char *buffer;                 //这个是播放的一帧数据
    buffer =(char*)malloc(size);  //size为1024， frames为512

	char *pcm_all = NULL;  //这个指针指向的空间将要保存所有的生成的音频
	int pcm_size = 0;

	int flag = 0; //这个用来遍历获取的音频
	//int first = 1;
	while (voice.sound_box_ongoing_flag >= 0)  //当前音箱资源没有被占用（可以播放声音）
	{
		/* 获取合成音频 */
		const void* data = QTTSAudioGet(sessionID, &audio_len, &synth_status, &ret);
		if (MSP_SUCCESS != ret)
		{
			ERROR_MSG("QTTSAudioGet failed, error code: %d.\n",ret);
			break;
		}

		if (data == NULL)
		{
			//DEBUG_MSG("iFly message is null\n");
			usleep(150*1000); //防止频繁占用CPU
		}
		
		if (NULL != data)
		{
			DEBUG_MSG("Get iFly message, audio_len = %d, pcm_size = %d\n", audio_len, pcm_size);
			char *temp_pcm = (char*)malloc((pcm_size + audio_len)*sizeof(char));
			if (temp_pcm == NULL)
			{
				ERROR_MSG("text_to_speech错误：播放声音缓存不足！\n");
				break;
			}
			
			memset(temp_pcm, 0, (pcm_size + audio_len)*sizeof(char));
			memcpy(temp_pcm, pcm_all, pcm_size); //先保存原来的
			memcpy(temp_pcm + pcm_size, data, audio_len); //再添加新的
			
			if(pcm_all != NULL)
			{
				//release the old memory.
				DEBUG_MSG("Free old pcm_all memory\n");
				free(pcm_all);
			}
			
			//set new pcm_all point.
			pcm_all = temp_pcm;
			pcm_size += audio_len;

			//播放
			while (voice.sound_box_ongoing_flag >= 0)
			{
				voice.sound_box_ongoing_flag--; //占用资源，减一
				if ((flag + 1024) > pcm_size)
                {
					voice.sound_box_ongoing_flag++;
					DEBUG_MSG("实时播放语音日志：读取的剩余的音频文件不足1024大小，请继续接收！\n");
					break;
				}
				memset(buffer, 0, 1024);
				memcpy(buffer, pcm_all + flag, 1024);
				
				//写音频数据到PCM设备
				//DEBUG_MSG("snd_pcm_writei, flag = %d\n", flag);
				ret = snd_pcm_writei(handle, buffer, 512);
				if( ret < 0)
				{
					usleep(2000);
					if (ret == -EPIPE)
					{
						/* EPIPE means underrun */
						ERROR_MSG("Underrun occurred\n");
						//完成硬件参数设置，使设备准备好
						snd_pcm_prepare(handle);
					}
					else if (ret < 0)
					{
						DEBUG_MSG("Error from writei: %s\n", snd_strerror(ret));
					}
				}
				else
				{
					//DEBUG_MSG("一帧数据播放完毕！buffer大小：%d,  frames大小：%d\n", size, (int)frames);
					flag += 1024;
				}
				voice.sound_box_ongoing_flag++;
			}
			wav_hdr.data_size += audio_len; //计算data_size大小
			DEBUG_MSG("audio_len=%d, wav_hdr.data_size=%d, pcm_size=%d\n", audio_len, wav_hdr.data_size,pcm_size);      
		}

		if (MSP_TTS_FLAG_DATA_END == synth_status)
		{
			DEBUG_MSG("text_to_speech end!!\n");
			break;
		}
	}
	
	/* 合成完毕 */
	ret = QTTSSessionEnd(sessionID, "Normal");
	if (MSP_SUCCESS != ret)
	{
		ERROR_MSG("QTTSSessionEnd failed, error code: %d.\n",ret);
	}
	snd_pcm_drain(handle);
	snd_pcm_close(handle);
	free(buffer);
	free(pcm_all);
	return ret;
}


/*
 * 功能：设置输出声音的参数
 * 说明：voice_name：发音人，不同的发音人代表了不同的音色，如男声、女声、童声等，详细请参照《发音人列表》（photos目录）
 * 	 speed：语速，合成音频对应的语速，取值范围：[0,100]，数值越大语速越快。
 *       volume：音量，合成音频的音量，取值范围：[0,100]，数值越大音量越大。
 *       pitch：语调，	合成音频的音调，取值范围：[0,100]，数值越大音调越高。
 *       bgm：背景音，合成音频中的背景音，支持参数：0：无背景音乐，1：有背景音乐 
 *
 * 返回值：成功返回0，失败返回-1
 */
int set_voice_params(char *voice_name, int speed, int volume, int pitch, int bgm)
{
	if(strlen(voice_name) > 15 || speed>100 || speed<0 || volume>100 || volume<0 || pitch>100 || pitch<0 || bgm<0||bgm>1)
		return -1; //参数出错
	//voice_name = xiaoyan, text_encoding = utf8, sample_rate = 16000, speed = 50, volume= 50, pitch = 50, rdn = 2"
	char s_speed[10] = {0};
	sprintf(s_speed, "%d", speed);
	char s_volume[10] = {0};
	sprintf(s_volume, "%d", volume);
	char s_pitch[10] = {0};
	sprintf(s_pitch, "%d", pitch);


	pthread_mutex_lock(&(voice.mutex_voice_params)); //申请锁
	
	memset(voice.output_voice_params, 0, sizeof(voice.output_voice_params));
	strcat(voice.output_voice_params, "voice_name = ");
	strcat(voice.output_voice_params, voice_name); //注意：如果当前名字不符合科大讯飞提供的名字，系统会出错，这里不进行正确检查
	strcat(voice.output_voice_params, ", text_encoding = utf8, sample_rate = 16000, ");
	strcat(voice.output_voice_params, "speed = ");
	strcat(voice.output_voice_params, s_speed);
	strcat(voice.output_voice_params, ", volume = ");
	strcat(voice.output_voice_params, s_volume);
	strcat(voice.output_voice_params, ", pitch = ");
	strcat(voice.output_voice_params, s_pitch);
	if (bgm == 0)
		strcat(voice.output_voice_params, ", rdn = 2, background_sound = 0");
	else
		strcat(voice.output_voice_params, ", rdn = 2, background_sound = 1");
	
	pthread_mutex_unlock(&(voice.mutex_voice_params)); //释放锁
	
	return 0;
}


/*
 * 功能：设置voice的工作模式
 * 说明：远程连接模式：可以支持语音聊天控制
	     wifi连接模式：仅仅支持蜂鸣器报警
 */
int set_voice_mode(int mode)
{
	if (mode == NETWORK_CONNECTED)
    {
		if (voice.voice_main_switch == SWITCH_ON) //如果当前已经开启语音功能，即登陆过科大讯飞
		{
			return 0;	
		}
		
        int ret = MSP_SUCCESS;
        //登陆到科大讯飞，登陆参数
        char login_params[100];
        memset(login_params, 0, sizeof(login_params));
        strcat(login_params, "appid = ");
        strcat(login_params, voice.xfyun_appid);
		strcat(login_params, ", engine_start = ivw, ivw_res_path =fo|res/ivw/wakeupresource.jet"); //for wakeup function
        strcat(login_params, ", work_dir = .");
		
        /* 用户登录 */
        ret = MSPLogin(NULL, NULL, login_params); //第一个参数是用户名，第二个参数是密码，均传NULL即可，第三个参数是登录参数    
        if (MSP_SUCCESS != ret)
        {
            ERROR_MSG("MSPLogin failed (科大讯飞账号登陆失败！) , Error code %d.\n", ret);
            ERROR_MSG("voice初始化：语音识别初始化失败！\n");
            MSPLogout();                                      //退出登录
            return -1;
        }

		//设置默认输出音频格式
		pthread_mutex_lock(&(voice.mutex_voice_params)); //申请锁
		memset(voice.output_voice_params, 0, sizeof(voice.output_voice_params));
		strcpy(voice.output_voice_params, "voice_name = xiaoyan, text_encoding = utf8, sample_rate = 16000, speed = 50, volume = 50, pitch = 50, rdn = 2");
		pthread_mutex_unlock(&(voice.mutex_voice_params)); //释放锁
        voice.voice_main_switch = SWITCH_ON;
        INFO_MSG("voice设置启动模式：网络连接模式，语音识别系统启动.\n");
		return 0;
    }
    else if (mode ==  NETWORK_DISCONNECTED)
    {
		voice.voice_main_switch = SWITCH_OFF;
		ERROR_MSG("voice设置启动模式：wifi连接模式，不支持语音聊天控制！\n");
		return 0;
    }		
	else
	{
		ERROR_MSG("voice设置启动模式：出错，当前启动模式不存在！\n");
		return -1;
	}
}

/*
 *功能：初始化语音模块
 *参数：mode:联网模式； xfyun_appid：科大讯飞开发包的APPID；tuling123_api_key：图灵机器人API的key值
 */
void voice_init(int mode, const char *xfyun_appid, const char *tuling123_api_key, const char *usb_audio_addr)
{
	voice.voice_main_switch = SWITCH_OFF;
	voice.recongnition_switch = SWITCH_OFF;
	voice.sound_box_ongoing_flag = 0;
    voice.state_machine = INITIAL_STATE;
	
	pthread_mutex_init(&(voice.mutex_voice_params), NULL);  //默认属性初始化声音参数内存空间的线程锁

	memset(voice.output_voice_params, 0, sizeof(voice.output_voice_params));
	memset(voice.voice_recongnition_text, 0, sizeof(voice.voice_recongnition_text));
	memset(voice.smart_reply_text, 0, sizeof(voice.smart_reply_text));
	memset(voice.smart_reply_code, 0, sizeof(voice.smart_reply_code));
	memset(voice.tuling123_api_key, 0, sizeof(voice.tuling123_api_key));
	memset(voice.xfyun_appid, 0, sizeof(voice.xfyun_appid));
	memset(voice.usb_audio_addr, 0, sizeof(voice.usb_audio_addr));

	//科大讯飞
	if (xfyun_appid == NULL || strlen(xfyun_appid) <= 0)
	{
		ERROR_MSG("voice初始化错误：讯飞APPID为空，语音聊天控制功能将有限制！\n");
	}
	else
	{
		strcpy(voice.xfyun_appid, xfyun_appid);	
	}
	
	//图灵机器人
	if (tuling123_api_key == NULL || strlen(tuling123_api_key) <= 0)
	{
		ERROR_MSG("voice初始化错误：图灵机器人API的key为空，语音聊天功能将有限制！\n");
	}
	else
	{
		strcpy(voice.tuling123_api_key, tuling123_api_key);
	}
	
	//USB声卡
	if (usb_audio_addr == NULL || strlen(usb_audio_addr) <= 0)
	{
		ERROR_MSG("voice初始化错误：USB声卡地址信息为空，语音聊天控制功能将有限制！\n");
		
	}
	else
	{
		strcpy(voice.usb_audio_addr, usb_audio_addr);
	}

	//设置voice模式
	if (set_voice_mode(mode) < 0)
	{
		ERROR_MSG("voice初始化失败：设置启动模式错误！\n");
		return ;
	}
	
	INFO_MSG("Voice Initial Success\n");
}

int cb_ivw_msg_proc( const char *sessionID, int msg, int param1, int param2, const void *info, void *userData )
{
	if (MSP_IVW_MSG_ERROR == msg) //唤醒出错消息
	{
		ERROR_MSG("\n\nMSP_IVW_MSG_ERROR errCode = %d\n\n", param1);
	}
	else if (MSP_IVW_MSG_WAKEUP == msg) //唤醒成功消息
	{
		DEBUG_MSG("MSP_IVW_MSG_WAKEUP result = %s\n", (char *)info);
		INFO_MSG("IFLY is Wakeup\n");
		voice.state_machine = AWAKE_STATE;
	}
	return 0;
}

static int speech_awake(void)
{
	/******************录制声音的各种参数部分**********************/	
	int rc;
	int size;
	snd_pcm_t* handle; //PCI设备句柄
	snd_pcm_hw_params_t* pcm_params;//硬件信息和PCM流配置
	int dir = 0;
	snd_pcm_uframes_t frames;
	int channels  = default_wav_hdr.channels;
	unsigned int frequency = default_wav_hdr.samples_per_sec;
	int bit       = default_wav_hdr.bits_per_sample;
	int datablock = default_wav_hdr.block_align;
	int final_return = -1;  //程序最终返回值，放到这里
	
	/* Open PCM device for recording (capture). */
	INFO_MSG("[PCM Setup] Open Capture\n");
	rc = snd_pcm_open(&handle, voice.usb_audio_addr, SND_PCM_STREAM_CAPTURE, 0);
	if (rc < 0)
	{
		ERROR_MSG("Unable to open pcm device: %s/n",  snd_strerror(rc));
		sleep(1);	 //可能出现频繁调用该函数，所以休眠一下
        return -1;
    }

	snd_pcm_hw_params_alloca(&pcm_params); //分配params结构体
	if(rc < 0)
	{
		ERROR_MSG("snd_pcm_hw_params_alloca error\n");
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		sleep(1); 
		return -1;
	}
        
	rc = snd_pcm_hw_params_any(handle, pcm_params);//初始化params
	if(rc<0)
	{
		ERROR_MSG("snd_pcm_hw_params_any error\n");
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		sleep(1); 
		return -1;
	}

	rc=snd_pcm_hw_params_set_access(handle, pcm_params, SND_PCM_ACCESS_RW_INTERLEAVED); //初始化访问权限
	if(rc<0)
	{
		ERROR_MSG("sed_pcm_hw_set_access error\n");
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		sleep(1);
		return -1;
	}
	
	//采样位数
	DEBUG_MSG("[PCM Setup] bit=%d\n", bit);
	switch(bit/8)
	{
		case 1:
			DEBUG_MSG("[PCM Setup] SND_PCM_FORMAT_U8\n");
			rc=snd_pcm_hw_params_set_format(handle, pcm_params, SND_PCM_FORMAT_U8);
			break ;
		case 2:
			DEBUG_MSG("[PCM Setup] SND_PCM_FORMAT_S16_LE\n");
			rc=snd_pcm_hw_params_set_format(handle, pcm_params, SND_PCM_FORMAT_S16_LE);
			break ;
		case 3:
			DEBUG_MSG("[PCM Setup] SND_PCM_FORMAT_S24_LE\n");
			rc=snd_pcm_hw_params_set_format(handle, pcm_params, SND_PCM_FORMAT_S24_LE);
			break ;
		default:
			rc = -1;
    }
	if (rc < 0)
	{
		ERROR_MSG("snd_pcm_hw_params_set_format error\n");
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		sleep(1);
		return -1;
	}
	
	DEBUG_MSG("[PCM Setup] channels=%d\n", channels);
	rc=snd_pcm_hw_params_set_channels(handle, pcm_params, channels); //设置声道,1表示单声>道，2表示立体声
	if(rc<0)
	{
		ERROR_MSG("snd_pcm_hw_params_set_channels error\n");
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		sleep(1);
		return -1;
	}

	DEBUG_MSG("[PCM Setup] frequency=%d\n", frequency);
	rc=snd_pcm_hw_params_set_rate_near(handle, pcm_params, &frequency, &dir); //设置>频率
	if(rc<0)
	{
		ERROR_MSG("snd_pcm_hw_params_set_rate_near error\n");
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		sleep(1);
		return -1;
	}
	usleep(500*1000);
	rc = snd_pcm_hw_params(handle, pcm_params);   //这个函数有延时！大概1s左右，原因不知道！
	if(rc<0)
	{
		ERROR_MSG("snd_pcm_hw_params error\n");
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		sleep(1);
		return -1;
	}

	//下面的frames和size好像都没用了，因为参数传递进来了
	rc=snd_pcm_hw_params_get_period_size(pcm_params, &frames, &dir); /*获取周期长度*/
	if(rc<0)
	{
		ERROR_MSG("snd_pcm_hw_params_get_period_size error\n");
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		sleep(1);
		return -1;
	}
	size = frames * datablock; /*4 代表数据快长度*/
	
	INFO_MSG("PCM Setup is done\n");
	/****************语音识别初始化部分*********************/
	const char* session_id  = NULL;
	//char rec_result[BUFFER_SIZE];
	//char hints[100]; //hints为结束本次会话的原因描述，由用户自定义
	int aud_stat = MSP_AUDIO_SAMPLE_CONTINUE; //音频状态
	int errcode = MSP_SUCCESS;
	
	char *once_upload_pcm_buffer = NULL; //该音频缓冲区一旦满足len（下方）就上传科大讯飞
	unsigned int upload_buffer_size = 0;   //此值满足len就上传
	char *rec_pcm_buffer = (char *)malloc(size); //此时size大小应该为1024
	int first = 1;
	unsigned int len = 10 * FRAME_LEN; //每次写入200ms音频(16k，16bit)：1帧音频20ms，10帧=200ms。16k采样率的16位音频，一帧的大小为640Byte
	int err_code = MSP_SUCCESS;
	char sse_hints[128];
	const char* session_begin_params = "ivw_threshold=0:-20,sst=wakeup";
	int count=0;

	session_id = QIVWSessionBegin(NULL, session_begin_params, &errcode); //
	if (MSP_SUCCESS != errcode)
	{
		ERROR_MSG("QIVWSessionBegin failed! error code:%d\n", errcode);
		final_return = -1;
		goto iat_exit;
	}
	
	err_code = QIVWRegisterNotify(session_id, cb_ivw_msg_proc, NULL);
	if (err_code != MSP_SUCCESS)
	{
		snprintf(sse_hints, sizeof(sse_hints), "QIVWRegisterNotify errorCode=%d", err_code);
		ERROR_MSG("QIVWRegisterNotify failed! error code:%d\n",err_code);
		goto iat_exit;
	}

	while (voice.recongnition_switch == SWITCH_ON && voice.state_machine == IDLE_STATE)
	{
		int ret = 0;
		//录制一次音频！大小为size(1024)
		memset(rec_pcm_buffer, 0, size);
		rc = snd_pcm_readi(handle, rec_pcm_buffer, frames);  //frames大小应该为512， size大小为1024
		if (rc == -EPIPE)
		{
			ERROR_MSG("overrun occurred/n");
			//sleep(5);
			snd_pcm_prepare(handle);
		}
		else if (rc < 0)
		{
			ERROR_MSG("error from read: %s\n", snd_strerror(rc));
			//sleep(5);
		}
		else if (rc != (int)frames)
		{
			ERROR_MSG("short read, read %d frames/n", rc);
			//sleep(5);
		}
		//fprintf(stdout, "录制了一次音频，size大小：%d,  frames大小：%d。\n", size, frames);


		char *temp_buffer = (char *)malloc(upload_buffer_size + size);
		memset(temp_buffer, 0, upload_buffer_size + size);
		memcpy(temp_buffer, once_upload_pcm_buffer, upload_buffer_size); //原先的拷贝过去
		memcpy(temp_buffer+upload_buffer_size, rec_pcm_buffer, size);   //再添加新的
		if (first)
		{
			first = 0;
			aud_stat = MSP_AUDIO_SAMPLE_FIRST;
		}
		else
		{
			free(once_upload_pcm_buffer);
			once_upload_pcm_buffer = NULL;
			aud_stat = MSP_AUDIO_SAMPLE_CONTINUE;
		}
		once_upload_pcm_buffer = temp_buffer;
		upload_buffer_size += size;
		
		if (upload_buffer_size >= len)
		{
			ret = QIVWAudioWrite(session_id, (const void*)once_upload_pcm_buffer, upload_buffer_size, aud_stat);	
			if (MSP_SUCCESS != ret)
			{
				ERROR_MSG("QIVWAudioWrite failed! error code:%d\n", ret);
				final_return = -1;
				goto iat_exit;  
			}
			DEBUG_MSG("Idle:%d\n",count++);
			upload_buffer_size = 0; //使重新开始录制音频		
		}		
	}
	
	errcode = QIVWAudioWrite(session_id, NULL, 0, MSP_AUDIO_SAMPLE_LAST);
	if (MSP_SUCCESS != errcode)
	{
		printf("\nQISRAudioWrite failed! error code:%d \n", errcode);
		final_return = -1;
		goto iat_exit;
	}
	
	final_return = 0;	

iat_exit:

	if (once_upload_pcm_buffer != NULL)
	{
		free(once_upload_pcm_buffer);
	}
	free(rec_pcm_buffer);	
	snd_pcm_drain(handle);
	snd_pcm_close(handle);
	QIVWSessionEnd(session_id, "end");
	return final_return;
}

/*
 * 功能：读取麦克风数据并识别出文字，当在录音识别时，开启指示灯，结束后关闭指示灯
 * 参数：rec_result：识别出的文字存放位置
 *       rec_result_size：存放文字空间大小
 * 返回值：成功返回0，失败返回-1
 * 说明：当在一定的时间（检测次数，默认为15），检测不到声音时（音量的阀值volume_threshold默认为6），则进行识别并退出！
 *       当检测到声音时（音量的阀值volume_threshold默认为6），之后如果连续的音量大小小于一定时间（检测次数，默认为3次），则进行识别并退出！
 *       如果需要调节音量阀值，请自己修改函数内部的数值
 */
static int speech_recognition(char *rec_result, int rec_result_size)
{
	/******************录制声音的各种参数部分**********************/	
	int rc;
	int size;
	snd_pcm_t* handle; //PCI设备句柄
	snd_pcm_hw_params_t* pcm_params;//硬件信息和PCM流配置
	int dir = 0;
	snd_pcm_uframes_t frames;
	int channels  = default_wav_hdr.channels;
	unsigned int frequency = default_wav_hdr.samples_per_sec;
	int bit       = default_wav_hdr.bits_per_sample;
	int datablock = default_wav_hdr.block_align;
	int final_return = -1;  //程序最终返回值，放到这里
	
	/* Open PCM device for recording (capture). */
	DEBUG_MSG("[PCM Setup] Open Capture\n");
	rc = snd_pcm_open(&handle, voice.usb_audio_addr, SND_PCM_STREAM_CAPTURE, 0);
	if (rc < 0)
	{
		ERROR_MSG("Unable to open pcm device: %s\n",  snd_strerror(rc));
		sleep(1);	 //可能出现频繁调用该函数，所以休眠一下
        return -1;
    }

	snd_pcm_hw_params_alloca(&pcm_params); //分配params结构体
	if(rc < 0)
	{
		ERROR_MSG("snd_pcm_hw_params_alloca error\n");
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		sleep(1); 
		return -1;
	}
        
	rc = snd_pcm_hw_params_any(handle, pcm_params);//初始化params
	if(rc<0)
	{
		ERROR_MSG("snd_pcm_hw_params_any error\n");
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		sleep(1); 
		return -1;
	}
	
	rc=snd_pcm_hw_params_set_access(handle, pcm_params, SND_PCM_ACCESS_RW_INTERLEAVED); //初始化访问权限
	if(rc<0)
	{
		ERROR_MSG("sed_pcm_hw_set_access error\n");
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		sleep(1);
		return -1;
	}
	
	//采样位数
	DEBUG_MSG("[PCM Setup] bit=%d\n",bit);
	switch(bit/8)
	{
		case 1:
			DEBUG_MSG("[PCM Setup] SND_PCM_FORMAT_U8\n");
			rc=snd_pcm_hw_params_set_format(handle, pcm_params, SND_PCM_FORMAT_U8);
			break ;
		case 2:
			DEBUG_MSG("[PCM Setup] SND_PCM_FORMAT_S16_LE\n");
			rc=snd_pcm_hw_params_set_format(handle, pcm_params, SND_PCM_FORMAT_S16_LE);
			break ;
		case 3:
			DEBUG_MSG("[PCM Setup] SND_PCM_FORMAT_S24_LE\n");
			rc=snd_pcm_hw_params_set_format(handle, pcm_params, SND_PCM_FORMAT_S24_LE);
			break ;
		default:
			rc = -1;
    }
	if (rc < 0)
	{
		ERROR_MSG("snd_pcm_hw_params_set_format error\n");
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		sleep(1);
		return -1;
	}
	
	DEBUG_MSG("[PCM Setup] channels=%d\n",channels);
	rc = snd_pcm_hw_params_set_channels(handle, pcm_params, channels); //设置声道,1表示单声>道，2表示立体声
	if(rc < 0)
	{
		ERROR_MSG("snd_pcm_hw_params_set_channels error\n");
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		sleep(1);
		return -1;
	}
	
	DEBUG_MSG("[PCM Setup] frequency=%d\n",frequency);
	rc = snd_pcm_hw_params_set_rate_near(handle, pcm_params, &frequency, &dir); //设置>频率
	if(rc < 0)
	{
		ERROR_MSG("snd_pcm_hw_params_set_rate_near error\n");
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		sleep(1);
		return -1;
	}

	rc = snd_pcm_hw_params(handle, pcm_params);   //这个函数有延时！大概1s左右，原因不知道！
	if(rc<0)
	{
		ERROR_MSG("snd_pcm_hw_params error\n");
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		sleep(1);
		return -1;
	}
	
	//下面的frames和size好像都没用了，因为参数传递进来了
	rc = snd_pcm_hw_params_get_period_size(pcm_params, &frames, &dir); /*获取周期长度*/
	if(rc<0)
	{
		ERROR_MSG("snd_pcm_hw_params_get_period_size error\n");
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		sleep(1);
		return -1;
	}
	size = frames * datablock; /*4 代表数据快长度*/

	INFO_MSG("[PCM Setup] done\n");
	/****************语音识别初始化部分*********************/
	const char* session_id  = NULL;
	unsigned int total_len = 0;
	int aud_stat = MSP_AUDIO_SAMPLE_CONTINUE; //音频状态
	int ep_stat = MSP_EP_LOOKING_FOR_SPEECH; //端点检测
	int rec_stat = MSP_REC_STATUS_SUCCESS;  //识别状态
	int errcode = MSP_SUCCESS;
	
	char *once_upload_pcm_buffer = NULL; //该音频缓冲区一旦满足len（下方）就上传科大讯飞
	unsigned int upload_buffer_size = 0;   //此值满足len就上传
	char *rec_pcm_buffer = (char *)malloc(size); //此时size大小应该为1024
	int first = 1;
	unsigned int len = 10 * FRAME_LEN; //每次写入200ms音频(16k，16bit)：1帧音频20ms，10帧=200ms。16k采样率的16位音频，一帧的大小为640Byte
	int after_voice_zero_num = 0;          //检测到声音之后，音量连续为无的次数
	int after_voice_counter_ongoing = 0;   //检测到声音之后的音量为无计数器
	int front_voice_zero_num = 0;          //检测到声音之前，音量连续为无的次数
	int front_voice_counter_ongoing = 1;   //检测到声音之前的音量为无计数器，默认开启
	int volume_threshold = 6;              //声音阀值，小于等于该阀值的声音将视为无声音
	
	const char* session_begin_params = "sub = iat, domain = iat, language = zh_ch, accent = mandarin, sample_rate = 16000,sch=1, nlp_version=3.0,result_type = plain, result_encoding = utf8";

	memset(rec_result, 0, rec_result_size);

	session_id = QISRSessionBegin(NULL, session_begin_params, &errcode); //听写不需要语法，第一个参数为NULL
	if (MSP_SUCCESS != errcode)
	{
		ERROR_MSG("QISRSessionBegin failed! error code:%d\n", errcode);
		final_return = -1;
		goto iat_exit;
	}

	while (voice.recongnition_switch == SWITCH_ON)
	{
		int ret = 0;
		//录制一次音频！大小为size(1024)
		memset(rec_pcm_buffer, 0, size);
		rc = snd_pcm_readi(handle, rec_pcm_buffer, frames);  //frames大小应该为512， size大小为1024
		if (rc == -EPIPE)
		{
			ERROR_MSG("Overrun Occurred\n");
			//sleep(5);
			snd_pcm_prepare(handle);
		}
		else if (rc < 0)
		{
			ERROR_MSG("Error from read: %s\n", snd_strerror(rc));
			//sleep(5);
		}
		else if (rc != (int)frames)
		{
			ERROR_MSG("Short read, Read %d frames/n", rc);
			//sleep(5);
		}
		//DEBUG_MSG("录制了一次音频，size大小：%d,  frames大小：%d。\n", size, frames);

		char *temp_buffer = (char *)malloc(upload_buffer_size + size);
		memset(temp_buffer, 0, upload_buffer_size + size);
		memcpy(temp_buffer, once_upload_pcm_buffer, upload_buffer_size); //原先的拷贝过去
		memcpy(temp_buffer+upload_buffer_size, rec_pcm_buffer, size);   //再添加新的
		if (first)
		{
			first = 0;
			aud_stat = MSP_AUDIO_SAMPLE_FIRST;
		}
		else
		{
			free(once_upload_pcm_buffer);
			once_upload_pcm_buffer = NULL;
			aud_stat = MSP_AUDIO_SAMPLE_CONTINUE;
		}
		once_upload_pcm_buffer = temp_buffer;
		upload_buffer_size += size;
		
		//如果当前录制的音频达到科大讯飞要求的大小，则上传科大讯飞
		if (upload_buffer_size >= len)
		{
			ret = QISRAudioWrite(session_id, (const void*)once_upload_pcm_buffer, upload_buffer_size, aud_stat, &ep_stat, &rec_stat);	
			if (MSP_SUCCESS != ret)
			{
				ERROR_MSG("QISRAudioWrite failed! error code:%d\n", ret);
				final_return = -1;
				goto iat_exit;  
			}
			
			if (MSP_REC_STATUS_SUCCESS == rec_stat) //已经有部分听写结果
			{
				const char *rslt = QISRGetResult(session_id, &rec_stat, 0, &errcode);
				if (MSP_SUCCESS != errcode)
				{
					ERROR_MSG("QISRGetResult failed! error code: %d\n", errcode);
					final_return = -1;
					goto iat_exit;  
				}
				if (NULL != rslt)
				{
					unsigned int rslt_len = strlen(rslt);
					total_len += rslt_len;
					if (total_len >= BUFFER_SIZE)
					{
						ERROR_MSG("No enough buffer for rec_result : %d\n", BUFFER_SIZE);
						final_return = -1;
						goto iat_exit;
					}
					strncat(rec_result, rslt, rslt_len);
					//DEBUG_MSG(stdout, "%s\n", rslt);
				}
			}
			
			if (MSP_EP_AFTER_SPEECH == ep_stat)   //检测到音频的结束端点！停止录音和识别！
			{
				INFO_MSG("检测到了音频结束端点！\n");
				break; 
			}
			
			//获取音量大小
			const char * para_name = "volume";
			char para_value[33] = {'\0'};
			unsigned int value_len = 33;
			ret = QISRGetParam(session_id, para_name, para_value, &value_len);
        	if( MSP_SUCCESS != ret )
			{
				ERROR_MSG( "QISRGetParam failed, error code is: %d\n", ret );
				final_return = -1;
				goto iat_exit;
			}
			int volume = 0;
			volume = atoi(para_value);
			DEBUG_MSG("Wakeup: volume %d, front count %d, after count %d\n", volume, front_voice_zero_num, after_voice_zero_num);
			
			if (volume > volume_threshold) //检测到声音了
			{
				if (!after_voice_counter_ongoing)   //如果没有开启检测到声音后的计数器开启，
				{
					after_voice_counter_ongoing = 1; //开启声音后计数器
					front_voice_counter_ongoing = 0; //关闭声音前计数器
				}
				after_voice_zero_num = 0;		 //每一次检测到有声音后都清零声音后计数器
			}
			//感觉上面的获取音量的那一块放到上面最好，，等下再改看看		
			if (volume <= volume_threshold && after_voice_counter_ongoing == 1)
			{	
				if (after_voice_zero_num >= 2)
				{
					after_voice_counter_ongoing = 0;
					after_voice_zero_num = 0;
					front_voice_counter_ongoing = 1;
					front_voice_zero_num = 0;
					break;		
				}
				else
				{
					after_voice_zero_num++;
				}
			}
		
			if (volume <= volume_threshold && front_voice_counter_ongoing == 1)
			{
				if (front_voice_zero_num >= 15)
				{
					after_voice_counter_ongoing = 0;
					after_voice_zero_num = 0;
					front_voice_counter_ongoing = 1;
					front_voice_zero_num = 0;
					break;			
				}
				else
				{
					front_voice_zero_num++;
				}
			}
			upload_buffer_size = 0; //使重新开始录制音频		
		}
		
	}
		
	errcode = QISRAudioWrite(session_id, NULL, 0, MSP_AUDIO_SAMPLE_LAST, &ep_stat, &rec_stat);
	if (MSP_SUCCESS != errcode)
	{
		ERROR_MSG("QISRAudioWrite failed! error code:%d \n", errcode);
		final_return = -1;
		goto iat_exit;
	}
	
	while (MSP_REC_STATUS_COMPLETE != rec_stat)
	{
		const char *rslt = QISRGetResult(session_id, &rec_stat, 0, &errcode);
		if (MSP_SUCCESS != errcode)
		{
			ERROR_MSG("QISRGetResult failed, error code: %d\n", errcode);
			final_return = -1;
			goto iat_exit;
		}
		
		if (NULL != rslt)
		{
			unsigned int rslt_len = strlen(rslt);
			total_len += rslt_len;
			if (total_len >= BUFFER_SIZE)
			{
				ERROR_MSG("No enough buffer for rec_result!\n");
				final_return = -1;
				goto iat_exit;
			}
			strncat(rec_result, rslt, rslt_len);
		}
		usleep(150*1000); //防止频繁占用CPU
	}
	
	final_return = 0;	

iat_exit:

	if (once_upload_pcm_buffer != NULL)
	{
		free(once_upload_pcm_buffer);
	}
	free(rec_pcm_buffer);	
	snd_pcm_drain(handle);
	snd_pcm_close(handle);
	QISRSessionEnd(session_id, "end");
	//close_voice_light(); //关闭指示灯
	return final_return;
}

/*
 * 功能：语音控制、语音聊天
 * 参数：无
 * 返回值：成功返回0，失败返回-1
 * 说明：1、从一次麦克风语音输入、语音听写、控制（聊天）都为正常的情况才视为为一次正常情况，返回0，任何一个环节出错返回-1
 *       2、必须在每一个环节（注释序号）之后添加判断是否打开了语音识别开关，如果检测到了关闭，则退出。
 *       3、添加了在每一个环节之后判断是否正在播放声音，如果正在播放声音那么关闭！
 *         （这个效果不大，因为当正在播放声音的时候可能正在录制声音，播放声音完后，录制声音才完毕！
 *          即可能在录音状态，播放警告音时发生该情况，未解决！)
 */
static int voice_chat_and_control(void)
{
	const char* output_text = NULL;
	
	if (voice.sound_box_ongoing_flag < 0)
	{
		usleep(100);
		return -1;  //当前正在播放声音，不允许录音
	}
	
	if (voice.recongnition_switch == SWITCH_OFF)
	{
		return -1;
	}
	
	switch(voice.state_machine)
	{
		case IDLE_STATE:
			DEBUG_MSG("IDLE_STATE\n");
			speech_awake();
			break;
			
		case AWAKE_STATE:
			DEBUG_MSG("AWAKE_STATE\n");
			memset(voice.voice_recongnition_text, 0, sizeof(voice.voice_recongnition_text));
			speech_recognition(voice.voice_recongnition_text, sizeof(voice.voice_recongnition_text));
			if (strlen(voice.voice_recongnition_text) == 0)
			{
				INFO_MSG("No Voice Question, try again!\n");
			}
			else
			{
				voice.state_machine = RESPONSE_STATE;
			}
			break;
			
		case RESPONSE_STATE:
			DEBUG_MSG("RESPONSE_STATE\n");
			DEBUG_MSG("Text to Voice：%s\n", voice.voice_recongnition_text);
			if (voice.recongnition_switch == SWITCH_OFF || voice.sound_box_ongoing_flag < 0)
			{
				break;
			}

			if (voice.recongnition_switch == SWITCH_OFF || voice.sound_box_ongoing_flag < 0)
			{
				break;
			}
			//Parser Jason
			output_text = ifly_get_contents(voice.voice_recongnition_text);
			INFO_MSG("Output_text:%s\n", output_text);
			if(strncmp(output_text,"Unknow error",12) == 0)
			{
				//語音無法順利回覆解答
				if (text_to_speech("抱歉 我不了解你的明白") < 0)
				{
					ERROR_MSG("Text to speech error\n");
					return -1;
				}
			}
			else
			{
				//4、语音输出回复的内容！
				if (text_to_speech(output_text) < 0)
				{
					ERROR_MSG("Text to speech error\n");
					return -1;
				}
			}
			INFO_MSG("Voice Control Finish\n");
			voice.state_machine = IDLE_STATE;
			break;
		default:
			ERROR_MSG("Voice control state machine error!!\n");
			break;
	}
	return 0;		
}


/*
 *功能：开启语音识别控制
 *返回值：成功返回0，失败返回-1
 *说明：这个函数只是打开语音中断开关（recongnition_switch），打开后在检测到声音后才进行录音，识别。
 */
int open_voice_recognition_chat_control()
{
	if (voice.voice_main_switch == SWITCH_OFF) //如果语音总开关没有打开，即语音初始化失败，禁止一切！
	{
		ERROR_MSG("voice错误：无法开启语音聊天控制！语音功能没有初始化成功，无法语音播放状态信息，请检查连接模式！\n");
		DEBUG_MSG("调试信息：voice.voice_main_switch:%d\n", voice.voice_main_switch);
		return 0;	
	}
	
	if (voice.recongnition_switch == SWITCH_ON)	      //如果语音识别控制开关已经打开，直接退出
	{
		ERROR_MSG("voice警告：语音聊天控制已经打开，无需重复打开此功能！\n");
		return 0;
	}

	voice.sound_box_ongoing_flag--; //不允许录音
	//输出语音提示“语音识别已经开启”
	system("aplay ./wav/sys_voice/opened_voice_recongnition.wav");
	voice.sound_box_ongoing_flag++;
	
	voice.state_machine = IDLE_STATE;
	voice.recongnition_switch = SWITCH_ON;
	INFO_MSG("语音识别控制已经开启\n");	

	while (voice.recongnition_switch == SWITCH_ON)
	{
		voice_chat_and_control();   //内部在初始化alas库参数的时候有延时，原因未知，所以不需要加延时了		
	}
	INFO_MSG("语音识别控制已经关闭\n");
	return 0;
}


/*
 * 功能：线程处理函数，在线程中关闭语音识别，降低延时
 * 参数：无
 * 返回值：无
 */
void* close_voice_recongnition_chat_control_th(void *arg)
{		
	if (voice.recongnition_switch == SWITCH_ON)
	{
		voice.recongnition_switch = SWITCH_OFF;
		//close_voice_light();
	
		//输出语音提示“语音识别已经关闭”
		voice.sound_box_ongoing_flag--;
		
		system("aplay ./wav/sys_voice/closed_voice_recongnition.wav");
		voice.sound_box_ongoing_flag++;
		return (void*)0;
	}

	return (void*)0;
}

/*
 * 在关闭信号中使用该函数（所有程序终结时调用！）
 */
void sys_close_voice_recongnition_chat_control()
{
	if (voice.voice_main_switch == SWITCH_ON)
	{
		voice.recongnition_switch = SWITCH_OFF;
		voice.voice_main_switch = SWITCH_OFF;
		//close_voice_light();
		MSPLogout();                                      //退出登录科大讯飞
		
		INFO_MSG("语音功能已经关闭！\n");
		return ;
	}

	return ;
}

/*
 *功能：关闭语音识别控制
 */
int close_voice_recongnition_chat_control()
{
	if (voice.voice_main_switch == SWITCH_OFF)   //语音没有初始化成功，直接退出！
	{
		ERROR_MSG("调试信息：无法关闭语音聊天控制！语音功能没有初始化成功，无法语音播放状态信息，请检查连接模式！\n");
		return 0;
	}

	if (voice.recongnition_switch == SWITCH_OFF)  //语音中断开关已经关闭，直接退出！
	{
		ERROR_MSG("调试信息：语音聊天控制已经关闭，无需重复关闭此功能！\n");
		return 0;
	}		
	
	/*
	 * 开启线程关闭语音识别
	 */
	
	//设置线程分离属性，以分离状态启动线程，在线程结束后会自动释放所占用的系统资源
	pthread_attr_t attr;
	pthread_attr_init(&attr);
	pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_DETACHED);

	pthread_t th; //线程标识符
	int err;
	if ((err = pthread_create(&th, &attr, close_voice_recongnition_chat_control_th, (void*)0)) != 0)
	{
		ERROR_MSG("servo_pulse_v_down pthread create error\n");
	}
	pthread_attr_destroy(&attr); //销毁线程属性结构体
		
	return 0;
}

