# Install rules and package config. Generates clustering-config.cmake and
# clustering-config-version.cmake (SameMajorVersion compat) so consumers can
# call `find_package(citor X.Y REQUIRED)`.

include(GNUInstallDirs)
include(CMakePackageConfigHelpers)

install(DIRECTORY include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
install(TARGETS clustering EXPORT clusteringTargets)
install(
    EXPORT clusteringTargets
    FILE clusteringTargets.cmake
    NAMESPACE citor::
    DESTINATION cmake/clustering
)

configure_package_config_file(
    ${PROJECT_SOURCE_DIR}/cmake/clusteringConfig.cmake.in
    "${CMAKE_CURRENT_BINARY_DIR}/clustering-config.cmake"
    INSTALL_DESTINATION cmake/clustering
)
write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/clustering-config-version.cmake"
    VERSION ${${PROJECT_NAME}_VERSION}
    COMPATIBILITY SameMajorVersion
)
install(
    FILES
        "${CMAKE_CURRENT_BINARY_DIR}/clustering-config.cmake"
        "${CMAKE_CURRENT_BINARY_DIR}/clustering-config-version.cmake"
    DESTINATION cmake/clustering
)
