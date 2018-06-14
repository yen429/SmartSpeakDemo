#include <stdio.h>
#include <stdlib.h>
#include <memory.h>
#include "ifly.h"

int
main (void)
{
    FILE *fp;
    char *json_source;

    fp = fopen("/home/simonchang/Downloads/xx/Weather_Data.txt", "rb");
    //fp = fopen("/home/simonchang/Downloads/xx/Joke_Data.txt", "rb");
    if (fp) {
        fseek(fp, 0, SEEK_END);
        long fsize = ftell(fp);
        fseek(fp, 0, SEEK_SET);  //same as rewind(f);

        json_source = malloc(fsize + 1);
        fread(json_source, fsize, 1, fp);
        fclose(fp);
        json_source[fsize] = 0;
    }

    printf ("Hello, world!\n");

    //printf(">>>> %s", json_source);
    json_parser(json_source);
    free(json_source);
    return 0;
}



/* return 1 if the monitor supports full hd, 0 otherwise */
int json_parser(const char * const json)
{

    //printf(">>>> output is %s", output);
    ifly_get_contents(json);

    return 0;
}


