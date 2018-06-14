#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <memory.h>
#include "ifly.h"

using namespace rapidjson;
using namespace std;

#define MY_FREE(x) {free(x); x=NULL;}

/** This table shall be same as enum IFLY_SERVICE_ID.
 */
typedef struct ifly_services {
    const char *name;
    IFLY_SERVICE_ID id;
} ifly_services;

typedef struct ifly_result_data {
    int type;
    const char *key;
    const char *prefix;
    char *result;
} ifly_result_data;


static ifly_services g_ifly_services[] = {
    {"musicX",       SERVICE_MUSICX},
    {"weather",      SERVICE_WEATHER},
    {"pm25",         SERVICE_PM25},
    {"flight",       SERVICE_FLIGHT},
    {"train",        SERVICE_TRAIN},
    {"telephone",    SERVICE_TELEPHONE},
    {"numberMaster", SERVICE_NUMBER_MASTER},
    {"poetry",       SERVICE_POETRY},
    {"story",        SERVICE_STORY},
    {"joke",         SERVICE_JOKE},
    {"radio",        SERVICE_RADIO},
    {"news",         SERVICE_NEWS},
    {"cookbook",     SERVICE_COOKBOOK},
    {"chat",         SERVICE_CHAT},
    {"calc",         SERVICE_CALC},
    {"datetime",     SERVICE_DATETIME},
    {"yhjg",         SERVICE_YHJG},
    {"tcyl",         SERVICE_TCYL},
    {"dataTransfer", SERVICE_DATA_TRANSFER},
    {"llb",          SERVICE_LLB},
    {"zdcx",         SERVICE_ZDCX},
    {"mycx",         SERVICE_MYCX},
    {"telephoneFee", SERVICE_TELEPHONE_FEE},
    {"tccx",         SERVICE_TCCX},
    {"dzfp",         SERVICE_DZFP},
    {"robotAction",  SERVICE_ROBOT_ACTION},
    {"cmd",          SERVICE_CMD},
    {"dishOrder",    SERVICE_DISH_ORDER},
    {"movie",        SERVICE_MOVIE},
    {"live",         SERVICE_LIVE},
    {"openQA",       SERVICE_OPEN_QA},
    {"AIUI.cyclopedia", SERVICE_AIUI_CYCLOPEDI},
};

#define NUM_OF_SERVICES (sizeof (g_ifly_services) / sizeof (ifly_services))

// enum for first level keys
typedef enum {
    KEY_RC = 0,
    KEY_ERROR,
    KEY_TEXT,
    KEY_SERVICE,
    KEY_OPERATION,
    KEY_DATA,
    KEY_ANSWER,
} ENUM_RESPONSE_KEYS_ID;

#ifdef USE_CJSON
// first level keys
char * response_keys[] = {
    "rc",
    "error",
    "text",
    "service",
    "operation",
    "data",
    "answer",
};
#define NUM_OF_RESPONSE_KEYS (sizeof(response_keys) / sizeof(const char *));
#endif //USE_CJSON

static ifly_data *g_list_root = NULL;
static char *g_output_data = NULL;

//#ifdef USE_CJSON
//#endif //USE_CJSON
#ifdef USE_RAPIDJSON
static char *g_json_source = NULL;
static Document document;
static std::ostringstream g_oss;
std::string g_var;
#endif //USE_RAPIDJSON


bool mystrcat(char *addition)
{
    if (g_output_data == NULL) {
        g_output_data = (char *) realloc(g_output_data, strlen(addition) + sizeof(char));
    } else {
        g_output_data = (char *) realloc(g_output_data, strlen(g_output_data) + strlen(addition) + sizeof(char));
    }
    if (!g_output_data) {
        printf("[%s] pointer is null.", __FUNCTION__);
        return false;
    }
    strcat(g_output_data, addition);
    return true;
}

char *ifly_concat_strings(char *str, ...) {
    va_list arguments;
    //unsigned int size = 0;
    //int i = 0;
    char *concat_str = NULL;
#if 0
    /* Initializing arguments to store all values after num */
    va_start (arguments, str);
    /* Sum all the inputs; we still rely on the function caller to tell us how
     * many there are */
    while (str) {
        int x = strlen(str);
        printf("[%s] strlen=%d, %s", __FUNCTION__, x, str);
        size += x;

        str = va_arg(arguments, int);
    }
    va_end (arguments);                  // Cleans up the list
#endif
    concat_str = (char *) malloc(sizeof(char)*1024*1024*100);
    va_start (arguments, str);

    vsprintf(concat_str, str, arguments);
    /*
    while (str) {
        strcat(concat_str, str);
        printf("[%s] concat_str=%s", __FUNCTION__, concat_str);

        str = va_arg(arguments, int);
    }*/

    va_end (arguments);                  // Cleans up the list

    printf("[%s] concat_str=%s", __FUNCTION__, concat_str);

    return concat_str;
}

#ifdef USE_RAPIDJSON
/** This API is intend to check the response code which is returned by
 * ifly server.
 *
 * @retval true valid
 * @retval false invalid
 */
bool ifly_is_valid_response(void) {
    bool ret = false;
/*
    g_json_source = (char*) malloc(strlen(json)+1);
    strcpy(g_json_source, json);
    if (document.ParseInsitu(g_json_source).HasParseError()) {
        printf("[%s] document parsing error!", __FUNCTION__);
        goto error;
    }
    */
    //get 'rc' field
    if (document.IsObject() == true) {
        ret = (document["rc"].GetInt() == 0)?true:false;
    } else if (document.IsArray() == true) {
        unsigned int i = 0;
        for (i = 0; i < document.Size(); i++) { //TODO: document,Size() should 1 always.
           ret = (document[i]["rc"].GetInt() == 0)?true:false;
           break;
        }
    }

//error:
//    MY_FREE(g_json_source)
    return ret;
}

/** This API is intend to retrieve error information from response
 * message.
 *
 * @return char* error string pointer.
 */
char *ifly_get_error_information(void) {
    //get 'error' field

    if (document.IsObject() == true) {
        Value::ConstMemberIterator itr = document.FindMember("error");
        if (itr != document.MemberEnd()) {
            return (char *) document["error"]["message"].GetString();
        }
    } else if (document.IsArray() == true) {
        unsigned int i = 0;
        for (i = 0; i < document.Size(); i++) { //TODO: document,Size() should 1 always.
            Value::ConstMemberIterator itr = document[i].FindMember("error");
            if (itr != document.MemberEnd()) {
                return (char *) document[i]["error"]["message"].GetString();
            }
        }
    }
    return NULL;
}

/** This API is intend to retrieve original request from response
 * message.
 *
 * @return char* requested text.
 */
char *ifly_get_requested_text(void) {
    //get 'text' field
    if (document.IsObject() == true) {
        return (char *) document["text"].GetString();
    } else if (document.IsArray() == true) {
        for (SizeType i = 0; i < document.Size(); i++) { //TODO: document,Size() should 1 always.
           return (char *) document[i]["text"].GetString();
        }
    }
    return NULL;
}

IFLY_SERVICE_ID ifly_get_service_id(void) {
    unsigned int i = 0;
    char *name = ifly_get_service_name();

    for (i=0; i<NUM_OF_SERVICES; i++) {
        if (!strcmp(name, g_ifly_services[i].name)) {
            printf("[%s] service name %s is found!\n", __FUNCTION__, name);
            return g_ifly_services[i].id;
        }
    }
    return SERVICE_UNKNOWN; //error case.
}

/** This API is intend to retrieve service id from response
 * message. Check ifly spec. for more details.
 *
 * @param msg the response message in JSON format.
 * @return char* service id.
 */
char *ifly_get_service_name(void) {
    //get 'service' field
    if (document.IsObject() == true) {
        Value::ConstMemberIterator itr = document.FindMember("service");
        if (itr != document.MemberEnd()) {
            return (char *) document["service"].GetString();
        }
    } else if (document.IsArray() == true) {
        for (SizeType i = 0; i < document.Size(); i++) { //TODO: document,Size() should 1 always.
            Value::ConstMemberIterator itr = document.FindMember("service");
            if (itr != document.MemberEnd()) {
                return (char *) document[i]["service"].GetString();
            }
        }
    }
    return NULL;
}

/** This API is intend to retrieve answered text from response
 * message.
 *
 * @param msg the response message in JSON format.
 * @return char* answered text.
 */
char *ifly_get_answered_text(void) {
    //get '/answer/text' field
    if (document.IsObject() == true) {
        Value::ConstMemberIterator itr = document.FindMember("answer");
        if (itr != document.MemberEnd()) {
            return (char *) document["answer"]["text"].GetString();
        }
    } else if (document.IsArray() == true) {
        for (SizeType i = 0; i < document.Size(); i++) { //TODO: document,Size() should 1 always.
            Value::ConstMemberIterator itr = document.FindMember("answer");
            if (itr != document.MemberEnd()) {
                return (char *) document[i]["answer"]["text"].GetString();
            }
        }
    }
    return NULL;
}

void handle_joke(SizeType i, SizeType j) {
    std::ostringstream oss;
    std::string var;

    ifly_result_data map[] = {
        //{kStringType, "title", NULL, NULL},
        {kStringType, "content", NULL, NULL},
    };

    SizeType map_size = sizeof(map) / sizeof(ifly_result_data);

    for (SizeType k=0; k<map_size; k++) {
        if (i != 0xffffffff)
            oss << "/" << i << "/data/result/" << j << "/" << map[k].key;
        else
            oss << "/data/result/" << j << "/" << map[k].key;
        var = oss.str();
        if (Value* tmp = Pointer(var.c_str()).Get(document)) {
            cout << "[" << j << "]" << ((map[k].prefix != NULL)?map[k].prefix:"") << tmp->GetString() << "\n";
            g_oss << ((map[k].prefix != NULL)?map[k].prefix:"") << tmp->GetString() << " ";
        }
        oss.str("");
        var.clear();
    }
}

void handle_poetry(SizeType i, SizeType j) {
    std::ostringstream oss;
    std::string var;

    ifly_result_data map[] = {
        {kStringType, "title", NULL, NULL},
        {kStringType, "content", NULL, NULL},
    };

    SizeType map_size = sizeof(map) / sizeof(ifly_result_data);

    for (SizeType k=0; k<map_size; k++) {
        if (i != 0xffffffff)
            oss << "/" << i << "/data/result/" << j << "/" << map[k].key;
        else
            oss << "/data/result/" << j << "/" << map[k].key;
        var = oss.str();
        if (Value* tmp = Pointer(var.c_str()).Get(document)) {
            cout << "[" << j << "]" << ((map[k].prefix != NULL)?map[k].prefix:"") << tmp->GetString() << "\n";
            g_oss << ((map[k].prefix != NULL)?map[k].prefix:"") << tmp->GetString() << " ";
        }
        oss.str("");
        var.clear();
    }
}

void handle_story(SizeType i, SizeType j) {
    std::ostringstream oss;
    std::string var;

    ifly_result_data map[] = {
        {kStringType, "name", NULL, NULL},
        {kStringType, "playUrl", "內容連結   ", NULL},
    };

    SizeType map_size = sizeof(map) / sizeof(ifly_result_data);

    for (SizeType k=0; k<map_size; k++) {
        if (i != 0xffffffff)
            oss << "/" << i << "/data/result/" << j << "/" << map[k].key;
        else
            oss << "/data/result/" << j << "/" << map[k].key;
        var = oss.str();
        if (Value* tmp = Pointer(var.c_str()).Get(document)) {
            cout << "[" << j << "]" << ((map[k].prefix != NULL)?map[k].prefix:"") << tmp->GetString() << "\n";
            g_oss << ((map[k].prefix != NULL)?map[k].prefix:"") << tmp->GetString() << "  ";
        }
        oss.str("");
        var.clear();
    }
}

void handle_news(SizeType i, SizeType j) {
    std::ostringstream oss;
    std::string var;

    ifly_result_data map[] = {
        {kStringType, "title", "標題   ", NULL},
        {kStringType, "category", "分類   ", NULL},
        {kStringType, "publishDateTime", "發布時間   ", NULL},
        {kStringType, "url", "內容連結   ", NULL},
    };

    SizeType map_size = sizeof(map) / sizeof(ifly_result_data);

    for (SizeType k=0; k<map_size; k++) {
        if (i != 0xffffffff)
            oss << "/" << i << "/data/result/" << j << "/" << map[k].key;
        else
            oss << "/data/result/" << j << "/" << map[k].key;
        var = oss.str();
        if (Value* tmp = Pointer(var.c_str()).Get(document)) {
            cout << "[" << j << "]" << ((map[k].prefix != NULL)?map[k].prefix:"") << tmp->GetString() << "\n";
            g_oss << ((map[k].prefix != NULL)?map[k].prefix:"") << tmp->GetString() << " ";
        }
        oss.str("");
        var.clear();
    }
}

void handle_cookbook(SizeType i, SizeType j) {
    std::ostringstream oss;
    std::string var;

    ifly_result_data map[] = {
        {kStringType, "title", "菜名   ", NULL},
        //{kStringType, "tag", "標籤   ", NULL},
        {kStringType, "ingredient", "主要食材   ", NULL},
        {kStringType, "accessory", "輔助食材   ", NULL},
        {kStringType, "steps", "步驟   ", NULL},
    };

    SizeType map_size = sizeof(map) / sizeof(ifly_result_data);

    for (SizeType k=0; k<map_size; k++) {
        if (i != 0xffffffff)
            oss << "/" << i << "/data/result/" << j << "/" << map[k].key;
        else
            oss << "/data/result/" << j << "/" << map[k].key;
        var = oss.str();
        if (Value* tmp = Pointer(var.c_str()).Get(document)) {
            cout << "[" << j << "]" << ((map[k].prefix != NULL)?map[k].prefix:"") << tmp->GetString() << "\n";
            g_oss << ((map[k].prefix != NULL)?map[k].prefix:"") << tmp->GetString() << " ";
        }
        oss.str("");
        var.clear();
    }
}

void handle_weather(SizeType j) {
    std::ostringstream oss;
    std::string var;

    ifly_result_data map[] = {
        //{"airQuality", NULL},
        {kStringType, "city", NULL, NULL},
        {kStringType, "date", "日期   ", NULL},
        {kStringType, "humidity", "濕度   ", NULL},
        //{"lastUpdateTime", "更新時間   ", NULL},
        {kStringType, "pm25", "PM2.5指數   ", NULL},
        {kStringType, "tempRange", "溫度   ", NULL},
        {kStringType, "weather", "天氣狀況   ", NULL},
        {kStringType, "wind", "風狀況   ", NULL},
    };

    SizeType map_size = sizeof(map) / sizeof(ifly_result_data);

    for (SizeType k=0; k<map_size; k++) {
        oss << "/data/result/" << j << "/" << map[k].key;
        var = oss.str();
        if (Value* tmp = Pointer(var.c_str()).Get(document)) {
            cout << "[" << j << "]" << ((map[k].prefix != NULL)?map[k].prefix:"") << tmp->GetString() << "\n";
            g_oss << ((map[k].prefix != NULL)?map[k].prefix:"") << tmp->GetString() << " ";
        }
        oss.str("");
        var.clear();
    }
}

void handle_pm25(SizeType i, SizeType j) {
    std::ostringstream oss;
    std::string var;

    ifly_result_data map[] = {
        {kStringType, "positionName", "監測點名稱   ", NULL},
        {kStringType, "pm25", "顆粒物(粒徑小於等於2.5)   ", NULL}, //int
        {kStringType, "pm10", "顆粒物(粒徑小於等於10)   ", NULL},
        {kStringType, "piblishDateTime", "發布日期   ", NULL},
        {kStringType, "area", "地區   ", NULL},
        {kStringType, "aqi", "空氣質量指數(AQI)   ", NULL}, //int
        {kStringType, "quality", "污染程度   ", NULL},
        {kStringType, "subArea", "下級地區   ", NULL},
    };

    SizeType map_size = sizeof(map) / sizeof(ifly_result_data);

    for (SizeType k=0; k<map_size; k++) {
        if (i != 0xffffffff)
            oss << "/" << i << "/data/result/" << j << "/" << map[k].key;
        else
            oss << "/data/result/" << j << "/" << map[k].key;
        var = oss.str();
        if (Value* tmp = Pointer(var.c_str()).Get(document)) {
            cout << "[" << j << "]" << ((map[k].prefix != NULL)?map[k].prefix:"") << tmp->GetString() << "\n";
            g_oss << ((map[k].prefix != NULL)?map[k].prefix:"") << tmp->GetString() << " ";
        }
        oss.str("");
        var.clear();
    }
}

void handle_flight(SizeType i, SizeType j) {
    std::ostringstream oss;
    std::string var;

    ifly_result_data map[] = {
        {kStringType, "departCity", "出發城市   ", NULL},
        {kStringType, "arriveCity", "到達城市   ", NULL}, //int
        {kStringType, "dPort", "出發機場   ", NULL},
        {kStringType, "aPort", "到達機場   ", NULL},
        {kStringType, "airline", "航空公司   ", NULL},
        {kStringType, "takeOffTime", "起飛時間   ", NULL}, //int
        {kStringType, "arriveTime", "到達時間   ", NULL},
        {kStringType, "flight", "航班號   ", NULL},
        //{"rate", "航班扣率   ", NULL},
        {kStringType, "price", "航班票價   ", NULL},
        {kStringType, "standardPrice", "標準價   ", NULL},
        {kStringType, "cabinInfo", "艙位信息   ", NULL},
        {kStringType, "quantity", "剩餘票量   ", NULL},
    };

    SizeType map_size = sizeof(map) / sizeof(ifly_result_data);

    for (SizeType k=0; k<map_size; k++) {
        if (i != 0xffffffff)
            oss << "/" << i << "/data/result/" << j << "/" << map[k].key;
        else
            oss << "/data/result/" << j << "/" << map[k].key;
        var = oss.str();
        if (Value* tmp = Pointer(var.c_str()).Get(document)) {
            cout << "[" << j << "]" << ((map[k].prefix != NULL)?map[k].prefix:"") << tmp->GetString() << "\n";
            g_oss << ((map[k].prefix != NULL)?map[k].prefix:"") << tmp->GetString() << " ";
        }
        oss.str("");
        var.clear();
    }
}

void handle_train(SizeType i, SizeType j) {
    std::ostringstream oss;
    std::string var;

    ifly_result_data map[] = {
        {kStringType,   "trainNo",          "車次   ",              NULL},
        {kStringType,   "trainType",        "火車類型   ",          NULL}, //int
        {kStringType,   "originStation",    "起始站   ",            NULL},
        {kStringType,   "terminalStation",  "終點站   ",            NULL},
        {kStringType,   "startTime",        "始發時間   ",          NULL},
        {kStringType,   "arriveTime",       "終點站時間   ",        NULL},
        {kStringType,   "runTime",          "全程運行時間   ",      NULL},
        {kArrayType,    "price",            "全程票價   ",          NULL},
    };

    ifly_result_data price[] = {
        {kStringType,   "name",             "票價類別   ",          NULL},
        {kStringType,   "value",            "票價   ",              NULL},
    };

    SizeType map_size = sizeof(map) / sizeof(ifly_result_data);
    SizeType price_size = sizeof(price) / sizeof(ifly_result_data);

    SizeType p_size = (i!=0xffffffff)?document[i]["data"]["result"][j]["price"].Size():document["data"]["result"][j]["price"].Size();

    for (SizeType k=0; k<map_size; k++) {

        switch (map[k].type) {
            case kStringType:
                if (i != 0xffffffff) {
                    oss << "/" << i << "/data/result/" << j << "/" << map[k].key;
                } else {
                    oss << "/data/result/" << j << "/" << map[k].key;
                }
                var = oss.str();
                if (Value* tmp = Pointer(var.c_str()).Get(document)) {
                    cout << "[" << j << "]" << ((map[k].prefix != NULL)?map[k].prefix:"") << tmp->GetString() << "\n";
                    g_oss << ((map[k].prefix != NULL)?map[k].prefix:"") << tmp->GetString() << " ";
                }
                oss.str("");
                var.clear();
                break;
            case kArrayType:
                for (SizeType p=0; p<p_size; p++) {
                    for (SizeType pd=0; pd<price_size; pd++) {
                        if (i != 0xffffffff) {
                            oss << "/" << i << "/data/result/" << j << "/" << map[k].key << "/" << p << "/" << price[pd].key;
                        } else {
                            oss << "/data/result/" << j << "/" << map[k].key << "/" << p << "/" << price[pd].key;
                        }
                        var = oss.str();
                        if (Value* tmp = Pointer(var.c_str()).Get(document)) {
                            cout << "[" << j << "]" << ((price[pd].prefix != NULL)?price[pd].prefix:"") << tmp->GetString() << "\n";
                            g_oss << ((price[pd].prefix != NULL)?price[pd].prefix:"") << tmp->GetString() << " ";
                        }
                        oss.str("");
                        var.clear();
                    }
                }
                break;
        }
    }
}

void handle_data(IFLY_SERVICE_ID id, SizeType i, SizeType j) {
    switch (id) {
        case SERVICE_UNKNOWN:
            break;
        case SERVICE_MUSICX:
            break;
        case SERVICE_WEATHER:
            handle_weather(j);
            break;
        case SERVICE_PM25:
            handle_pm25(i, j);
            break;
        case SERVICE_FLIGHT:
            handle_flight(i, j);
            break;
        case SERVICE_TRAIN:
            handle_train(i, j);
            break;
        case SERVICE_TELEPHONE:
        case SERVICE_NUMBER_MASTER:
            break;
        case SERVICE_POETRY:
            handle_poetry(i, j);
            break;
        case SERVICE_STORY:
            handle_story(i, j);
            break;
        case SERVICE_JOKE:
            handle_joke(i, j);
            break;
        case SERVICE_RADIO:
        case SERVICE_NEWS:
            handle_news(i, j);
            break;
        case SERVICE_COOKBOOK:
            handle_cookbook(i, j);
            break;
        case SERVICE_CHAT:
        case SERVICE_CALC:
        case SERVICE_DATETIME:
        case SERVICE_YHJG:
        case SERVICE_TCYL:
        case SERVICE_DATA_TRANSFER:
        case SERVICE_LLB:
        case SERVICE_ZDCX:
        case SERVICE_MYCX:
        case SERVICE_TELEPHONE_FEE:
        case SERVICE_TCCX:
        case SERVICE_DZFP:
        case SERVICE_ROBOT_ACTION:
        case SERVICE_CMD:
            break;
        case SERVICE_DISH_ORDER:
            break;
        case SERVICE_MOVIE:
        case SERVICE_LIVE:
        case SERVICE_OPEN_QA:
        case SERVICE_AIUI_CYCLOPEDI:
            break;
    }
}
// type: joke,weather, etc.
// result: result array pointer.
void ifly_get_content(void) {
    //get '/data/result' field
    IFLY_SERVICE_ID id;
    id = ifly_get_service_id();

    Value::ConstMemberIterator itr = document.FindMember("data");
    if (itr != document.MemberEnd()) {
        if ((id != SERVICE_FLIGHT) &&
                (id != SERVICE_WEATHER) &&
                (id != SERVICE_PM25) &&
                (id != SERVICE_TRAIN) &&
                (id != SERVICE_AIUI_CYCLOPEDI) &&
                (id != SERVICE_JOKE) &&
                (id != SERVICE_COOKBOOK)
                ) {
            printf("[%s] %s\n", __FUNCTION__, "find data field! ##");

            if (document.IsObject() == true) {
                cout << "document is object." << endl;
                for (SizeType j = 0 ; j < document["data"]["result"].Size(); j++) {
                    handle_data(id, 0xffffffff, j);
                    break; //only use item 1.
                }
            } else if (document.IsArray() == true) {
                cout << "document is array." << endl;
                for (SizeType i = 0; i < document.Size(); i++) { //TODO: document,Size() should 1 always.
                    for (SizeType j = 0 ; j < document[i]["data"]["result"].Size(); j++) {
                        handle_data(id, i, j);
                        break; //only use item 1.
                    }
                }
            }
        }
    } else {
        printf("[%s] %s\n", __FUNCTION__, "no data field! ##");
    }
}

bool ifly_parser_start(const char *json) {
    g_json_source = (char*) malloc(strlen(json)+1);
    strcpy(g_json_source, json);
    if (document.ParseInsitu(g_json_source).HasParseError()) {
        printf("[%s] document parsing error!\n==>%s\n$$$>%s", __FUNCTION__, json, g_json_source);
        return false;
    }

    g_oss.str("");
	g_oss.clear();
    return true;
}

void ifly_parser_end(void) {
    MY_FREE(g_json_source)
}

//for test only
const char *ifly_get_contents(const char *json) {
    /*
    Document document;

    g_json_source = (char*) malloc(strlen(json)+1);
    strcpy(g_json_source, json);
    if (document.ParseInsitu(g_json_source).HasParseError()) {
        printf("[%s] document parsing error!", __FUNCTION__);
        return;
    }
    */
    //init
    ifly_parser_start(json);

    //rc
    printf("[%s] valid? %s\n", __FUNCTION__, (ifly_is_valid_response())?"true":"false");
    if (ifly_is_valid_response() == true) {

        //service
        char *service_id = ifly_get_service_name();
        printf("[%s] service is %s\n", __FUNCTION__, (service_id)?service_id:"NULL");
        //text
        char *text = ifly_get_requested_text();
        printf("[%s] text is %s\n", __FUNCTION__, (text)?text:"NULL");
        //answer
        char *answer = ifly_get_answered_text();
        printf("[%s] answer is %s\n", __FUNCTION__, (answer)?answer:"NULL");
        g_oss << answer << " ";

        //data->result
        ifly_get_content();

    } else {
        char *error = ifly_get_error_information();
        printf("[%s] error is %s\n", __FUNCTION__, (error)?error:"Unknow error.");
        g_oss << ((error)?error:"Unknow error.") << " ";
    }

    const std::string red("\033[0;31m");
    const std::string green("\033[1;32m");
    const std::string yellow("\033[1;33m");
    const std::string cyan("\033[0;36m");
    const std::string magenta("\033[0;35m");
    const std::string reset("\033[0m");

    //std::string var;
    g_var = g_oss.str();
    cout << red << endl << "Output result:" << endl << g_var.c_str() << reset << endl;

    //release memory resource.
    ifly_parser_end();

    return g_var.c_str();
}
#endif //USE_RAPIDJSON


void ifly_list_free(void) {
    ifly_data *tmp;

    while (g_list_root != NULL)
    {
        tmp = g_list_root;
        g_list_root = g_list_root->next;
        //printf("\n[%s] free %s %s\n", __FUNCTION__, tmp->title, tmp->content);
        free(tmp);
    }
}

void ifly_list_insert(char *title, char *content) {

    ifly_data *current;

    if (g_list_root == NULL) {
        //printf("[%s] #1 title:%s content:%s\n", __FUNCTION__, title, content);
        g_list_root = (ifly_data *)malloc(sizeof(*g_list_root));
        g_list_root->next = NULL;
        g_list_root->prev = NULL;
        g_list_root->title = title;
        g_list_root->content = content;
    } else {
        //printf("[%s] #2 title:%s content:%s\n", __FUNCTION__, title, content);
        current = g_list_root;
        // current is pointing to first element
        // we iterate until we find the end
        while(current->next != NULL) {
            current = current->next;
        }
        // create a new ifly_data and insert the item
        current->next = (ifly_data *)malloc(sizeof(ifly_data));
        (current->next)->prev = current;
        current = current->next;
        current->title = title;
        current->content = content;
        current->next = NULL;
    }
}

void ifly_list_delete(ifly_data *current, char *title, char *content){

    // Iterate until we find a pointer next to the one we need to delete
    while (current->next != NULL &&
            !strcmp((current->next)->title, title) &&
            !strcmp((current->next)->content, content)) {
        current = current->next;
    }

    // Item is not found
    if(current->next == NULL) {
        printf("\nElement with title:%s \n", title);
        printf("        with content:%s is not present in the list\n", content);
        return;
    }

    // The element is found in the node next to the one that current points to
    // We removed the node which is next to the pointer (which is also temp)
    ifly_data *tmp = current->next;
    // In special case that we are deleting last node
    if(tmp->next == NULL) {
        current->next = NULL;
    } else {
        current->next = tmp->next;
        (current->next)->prev = tmp->prev;
    }
    tmp->prev = current;

    // We got rid of the node, now time to dellocate the memory
    free(tmp);

    return;
}
void ifly_list_print(ifly_data *current) {
    while(current != NULL) {
        printf("\n[%s] title:%s\n", __FUNCTION__, current->title);
        printf("[%s] content:%s\n", __FUNCTION__, current->content);
        current = current->next;
    }

    //TODO serialize all node into one buffer.
}

bool ifly_list_find(ifly_data *current, char *title, char *content) {
    // First pointer is head aka dummy node with no data
    // so we go to next one
    current = current->next;

    // Iterate through the linked list
    while(current != NULL) {
        if (!strcmp(current->title, title) &&
            !strcmp(current->content, content)) {
            return true;
        }
        current = current->next;
    }
    return false;
}

