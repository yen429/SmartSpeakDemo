#include <fcntl.h>
#include <stdio.h>
#include <sys/stat.h>
#include <unistd.h>
#include <string.h>

#define MAX_BUF 40960

int main()
{
    int fd;
    char * myfifo = "voice_control_fifo";
    char buf[MAX_BUF]={0};

    /* open, read, and display the message from the FIFO */
    fd = open(myfifo, O_RDONLY);
	if(fd<0)
	{
		printf("Open %s error\n", myfifo);
		return 1;
	}
	while(1)
	{
		memset(buf, 0, MAX_BUF);
		read(fd, buf, MAX_BUF);
		printf("%s", buf);
	}
	close(fd);
    return 0;
}