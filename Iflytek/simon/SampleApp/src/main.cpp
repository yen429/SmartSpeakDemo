#include <stdio.h>
#include <stdlib.h>
#include <memory.h>
#include "ifly.h"

int json_parser(const char * const json)
{

    //printf(">>>> output is %s", output);
    ifly_get_contents(json);

    return 0;
}

int
main (void)
{
    FILE *fp;
    char *json_source;
    char op;

    op = std::getchar();

    //remove the rest of the line from input stream
    int temp;
    while ( (temp = std::getchar()) != '\n' && temp != EOF );

    printf("Please input a number. \n 1:weather\n2:joke\n3:flight\n4:train\n5:poetry\n6:story\n");
    switch(op){
        case '1':
            fp = fopen("/home/simonchang/Downloads/xx/Weather_Data.txt", "rb");
            break;
        case '2':
            fp = fopen("/home/simonchang/Downloads/xx/Joke_Data.txt", "rb");
            break;
        case '3':
            fp = fopen("/home/simonchang/Downloads/xx/Flight_Data.txt", "rb");
            break;
        case '4':
            fp = fopen("/home/simonchang/Downloads/xx/Train_Data.txt", "rb");
            break;
        case '5':
            fp = fopen("/home/simonchang/Downloads/xx/Poetry_Data.txt", "rb");
            break;
        case '6':
            fp = fopen("/home/simonchang/Downloads/xx/Story_Data.txt", "rb");
            break;
        case '7':
            fp = fopen("/home/simonchang/Downloads/xx/News_Data.txt", "rb");
            break;
        case '8':
            fp = fopen("/home/simonchang/Downloads/xx/CookBook_Data.txt", "rb");
            break;
        case '9':
            fp = fopen("/home/simonchang/Downloads/xx/DateTime_Data.txt", "rb");
            break;
        default:
            fp = fopen("/home/simonchang/Downloads/xx/Weather_Data.txt", "rb");
            break;
    }

    //fp = fopen("/home/simonchang/Downloads/xx/Joke_Data.txt", "rb");
    if (fp) {
        fseek(fp, 0, SEEK_END);
        long fsize = ftell(fp);
        fseek(fp, 0, SEEK_SET);  //same as rewind(f);

        json_source = (char *) malloc(fsize + 1);
        fread(json_source, fsize, 1, fp);
        fclose(fp);
        json_source[fsize] = 0;
    }

    printf ("Hello, world!\n");

    printf(">>>> %s", json_source);
    json_parser(json_source);
    free(json_source);
    return 0;
}






