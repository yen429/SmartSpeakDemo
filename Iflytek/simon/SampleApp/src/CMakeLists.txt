add_executable(SampleApp main.cpp)

target_include_directories(SampleApp PUBLIC
    "${ifly_SOURCE_DIR}/include")

target_link_libraries(SampleApp
    ifly)
