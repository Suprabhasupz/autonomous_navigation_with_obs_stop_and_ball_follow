cmake_minimum_required(VERSION 3.8)
project(diffbot_description)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

# Install all resource folders
install(DIRECTORY
  launch
  urdf
  meshes
  worlds
  config
  rviz
  
  DESTINATION share/${PROJECT_NAME}
)

ament_package()