cmake_minimum_required(VERSION 3.14)
project(svdep VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Set visibility for shared library
set(CMAKE_CXX_VISIBILITY_PRESET hidden)
set(CMAKE_VISIBILITY_INLINES_HIDDEN YES)

# Source files
set(SVDEP_SOURCES
    src/svdep.cpp
    src/SVDepContext.cpp
    src/SVPreprocessor.cpp
    src/FileCollection.cpp
)

# Create shared library
add_library(svdep SHARED ${SVDEP_SOURCES})

target_include_directories(svdep
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src
)

# Set library version
set_target_properties(svdep PROPERTIES
    VERSION ${PROJECT_VERSION}
    SOVERSION 1
)

# Platform-specific settings
if(WIN32)
    target_compile_definitions(svdep PRIVATE _CRT_SECURE_NO_WARNINGS)
endif()

# Installation rules
include(GNUInstallDirs)

install(TARGETS svdep
    EXPORT svdep-targets
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)

install(DIRECTORY include/
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

install(EXPORT svdep-targets
    FILE svdep-targets.cmake
    NAMESPACE svdep::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/svdep
)

# Create config file
include(CMakePackageConfigHelpers)
write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/svdep-config-version.cmake"
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)

configure_file(cmake/svdep-config.cmake.in
    "${CMAKE_CURRENT_BINARY_DIR}/svdep-config.cmake"
    @ONLY
)

install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/svdep-config.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/svdep-config-version.cmake"
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/svdep
)

# Option to build tests
option(SVDEP_BUILD_TESTS "Build tests" OFF)
if(SVDEP_BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()
