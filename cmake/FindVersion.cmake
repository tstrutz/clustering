function(use_version_from_file VERSION_FILE)
    if(NOT EXISTS "${CMAKE_SOURCE_DIR}/${VERSION_FILE}")
        message(FATAL_ERROR "Version file '${VERSION_FILE}' not found.")
    endif()

    # Read the version number from the file
    file(READ "${CMAKE_SOURCE_DIR}/${VERSION_FILE}" VERSION_CONTENTS)
    string(STRIP "${VERSION_CONTENTS}" VERSION_STRING)

    # Split the version in Major.Minor.Patch
    string(REGEX MATCH "^([0-9]+)\\.([0-9]+)\\.([0-9]+)" _ "${VERSION_STRING}")
    set(VERSION_MAJOR "${CMAKE_MATCH_1}")
    set(VERSION_MINOR "${CMAKE_MATCH_2}")
    set(VERSION_PATCH "${CMAKE_MATCH_3}")

    # Verify the version components
    if("${VERSION_MAJOR}" STREQUAL "" OR "${VERSION_MINOR}" STREQUAL "" OR "${VERSION_PATCH}" STREQUAL "")
        message(FATAL_ERROR "Invalid version string in '${VERSION_FILE}': '${VERSION_STRING}'. Must be in the format MAJOR.MINOR.PATCH")
    endif()

    # Set the project version
    set(PROJECT_VERSION_MAJOR "${VERSION_MAJOR}" PARENT_SCOPE)
    set(PROJECT_VERSION_MINOR "${VERSION_MINOR}" PARENT_SCOPE)
    set(PROJECT_VERSION_PATCH "${VERSION_PATCH}" PARENT_SCOPE)
    set(PROJECT_VERSION "${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_PATCH}" PARENT_SCOPE)
endfunction()
