#ifndef __PCM_H_
#define __PCM_H_
/* 语音识别后智能回复的产生的wav文件：wav音频头部格式 */
typedef struct _wave_pcm_hdr
{
	char      riff[4];           // = "RIFF"
	int	      size_8;            // = FileSize - 8
	char      wave[4];           // = "WAVE"
	char      fmt[4];            // = "fmt "
	int       fmt_size;		     // = 下一个结构体的大小 : 16
	short int format_tag;        // = PCM : 1
	short int channels;          // = 通道数 : 1
	int       samples_per_sec;   // = 采样率 : 8000 | 6000 | 11025 | 16000
	int       avg_bytes_per_sec; // = 每秒字节数 : samples_per_sec * bits_per_sample / 8
	short int block_align;       // = 每采样点字节数 : wBitsPerSample / 8
	short int bits_per_sample;   // = 量化比特数: 8 | 16
	char      data[4];           // = "data";
	int       data_size;         // = 纯数据长度 : FileSize - 44 
} wave_pcm_hdr;

snd_pcm_t*  pcm_setup(snd_pcm_stream_t stream, char *dev_name);
void pcm_playback(snd_pcm_t* handle);
void pcm_capture(snd_pcm_t* handle);
void pcm_close(snd_pcm_t* handle);

extern int pcm_size;
extern int pcm_frames;

#endif