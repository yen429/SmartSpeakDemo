add_library(ifly SHARED
    ifly.cpp)

include_directories("../include/")

target_include_directories(ifly PUBLIC
    "${ifly_SOURCE_DIR}/include")
message(STATUS "sc+${ifly_SOURCE_DIR}")

add_definitions(-D__STDC_FORMAT_MACROS)
set_property(DIRECTORY PROPERTY COMPILE_OPTIONS ${EXTRA_CXX_FLAGS})

if ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pthread")
endif()

# copy out the lib binary... need to leave the static lib around to pass gradle check
set(distribution_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../distribution)
#message(STATUS "sc+ @@@@@@@@@@ ${distribution_DIR}")
set_target_properties(ifly
                      PROPERTIES
                      LIBRARY_OUTPUT_DIRECTORY
                      ${distribution_DIR}/ifly/lib)

# create a list of files to copy
set( HEADER_FILES_DIR
   "${PROJECT_SOURCE_DIR}/include"
)

# do the copying
foreach( file_i ${HEADER_FILES_DIR})
    add_custom_command(
        TARGET ifly
    POST_BUILD
    COMMAND ${CMAKE_COMMAND}
    ARGS -E copy_directory ${file_i} "${distribution_DIR}/ifly/include"
)
endforeach( file_i )
