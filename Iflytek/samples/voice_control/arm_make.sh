#编译64位可执行文件
make clean;make ARM_BUILD=1
#设置libmsc.so库搜索路径
export LD_LIBRARY_PATH=$(pwd)/../../libs/arm/
