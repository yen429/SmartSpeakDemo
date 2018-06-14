#include <alsa/asoundlib.h>
#include <unistd.h>
#include "voice.h"
#include "pcm.h"
#include "debug.h"

int pcm_size = 0;
int pcm_frames = 0;

static wave_pcm_hdr default_wav_hdr = 
{
	{'R', 'I', 'F', 'F'},  // RIFF
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

snd_pcm_t* pcm_setup(snd_pcm_stream_t stream, char *dev_name)
{
	int rc;
	snd_pcm_t* handle;
	snd_pcm_hw_params_t* pcm_params;//硬件信息和PCM流配置
	int dir=0;
	snd_pcm_uframes_t frames;

	int channels  = default_wav_hdr.channels; // 1
	unsigned int frequency = default_wav_hdr.samples_per_sec; // 16000
	int bit       = default_wav_hdr.bits_per_sample; // 16
	int datablock = default_wav_hdr.block_align;
	
	rc = snd_pcm_open(&handle, dev_name, stream, 0);
	if(rc < 0)
	{
		ERROR_MSG("open PCM device error\n");
		return NULL;
	}

	snd_pcm_hw_params_alloca(&pcm_params); //分配params结构体
	if(rc < 0)
	{
		ERROR_MSG("snd_pcm_hw_params_alloca error\n");
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		return NULL;
	}
	
	rc = snd_pcm_hw_params_any(handle, pcm_params);//初始化params
	if(rc < 0)
	{
		ERROR_MSG("snd_pcm_hw_params_any error\n");
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		return NULL;
	}
	
	rc=snd_pcm_hw_params_set_access(handle, pcm_params, SND_PCM_ACCESS_RW_INTERLEAVED); //初始化访问权限
	if(rc < 0)
	{
		ERROR_MSG("sed_pcm_hw_set_access error\n");
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		return NULL;
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
		return NULL;
	}
	
	DEBUG_MSG("[PCM Setup] channels=%d\n", channels);
	rc=snd_pcm_hw_params_set_channels(handle, pcm_params, channels); //设置声道,1表示单声>道，2表示立体声
	if(rc < 0)
	{
		ERROR_MSG("snd_pcm_hw_params_set_channels error\n");
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		return NULL;
	}
	
	DEBUG_MSG("[PCM Setup] frequency=%d\n", frequency);
	rc=snd_pcm_hw_params_set_rate_near(handle, pcm_params, &frequency, &dir); //设置>频率
	if(rc < 0)
	{
		ERROR_MSG("snd_pcm_hw_params_set_rate_near error\n");
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		return NULL;
	}

	rc = snd_pcm_hw_params(handle, pcm_params);
	if(rc < 0)
	{
		ERROR_MSG("snd_pcm_hw_params error\n");
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		return NULL;
	}
	usleep(300*1000);
	//下面的frames和size好像都没用了，因为参数传递进来了
	rc=snd_pcm_hw_params_get_period_size(pcm_params, &frames, &dir); /*获取周期长度*/
	if(rc < 0)
	{
		ERROR_MSG("snd_pcm_hw_params_get_period_size error\n");
		snd_pcm_drain(handle);
		snd_pcm_close(handle);
		return NULL;
	}
	pcm_frames = frames;
	pcm_size = pcm_frames * datablock; /* 代表数据快长度, pcm_frames = 2048, datablock =2 */
	DEBUG_MSG("[PCM Setup] pcm_size=%d, pcm frames=%d, datablock=%d\n", pcm_size, pcm_frames, datablock);
	return handle;
}

void pcm_playback(snd_pcm_t* handle)
{

}

void pcm_capture(snd_pcm_t* handle)
{
	
	
}

void pcm_close(snd_pcm_t* handle)
{
	snd_pcm_drain(handle);
	snd_pcm_close(handle);
}