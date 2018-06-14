#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <stdio.h>
#include <unistd.h>
#include "debug.h"

int fifo_init(const char *fifo_file)
{
	int fd;
	/* create the FIFO (named pipe) */
    mkfifo(fifo_file, 0666);
	
	/* open, read, and display the message from the FIFO */
    fd = open(fifo_file, O_WRONLY);
	
	return fd;
}

int fifo_write(int fd ,const char *message, int message_size)
{
	int rc;
	rc = write(fd, message, message_size);
	if(rc < 0)
		INFO_MSG("write error\n");
	else
		INFO_MSG("write success\n");
	return rc;
}

void fifo_close(int fd)
{
	close(fd);
}