set(SOURCES_DISP
    view.cc
    view_prop.cc
    glapp.cc
    fiber_disp.cc
    line_disp.cc
    point_disp.cc
    grid_display.cc
    display_prop.cc
    display.cc
    display1.cc
    display2.cc
    display3.cc
)

#include_directories("../gym")
#include_directories("../gym/deps")
#set(SOURCES_GYM
#    save_image.cc
#    gle.cc
#)
#list(TRANSFORM SOURCES_GYM PREPEND "${PROJECT_SOURCE_DIR}/../src/gym/")

#set(SOURCES_GYM_DEPS
#    spng.c
#    miniz.c
#)
#list(TRANSFORM SOURCES_GYM_DEPS PREPEND "${PROJECT_SOURCE_DIR}/../src/gym/deps/")
list(TRANSFORM SOURCES_DISP PREPEND "${PROJECT_SOURCE_DIR}/src/disp/")


set(DISP_INCLUDES math base sim sim/organizers gym gym/deps)
list(TRANSFORM DISP_INCLUDES PREPEND "${PROJECT_SOURCE_DIR}/src/")

add_library(${DISP_LIBRARY} STATIC ${SOURCES_DISP})

target_compile_definitions(${DISP_LIBRARY} PRIVATE -DDISPLAY)
target_include_directories(${DISP_LIBRARY} PUBLIC "${DISP_INCLUDES}" )
