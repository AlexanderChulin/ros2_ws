cmake_minimum_required(VERSION 3.8)
project(robot_vision)

# Dependencias mínimas
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# Mensajes
set(msg_files
  "msg/SensorData.msg"
  "msg/MotorCmd.msg"
  "msg/BallDetection.msg"
)

# Generar interfaces
rosidl_generate_interfaces(${PROJECT_NAME}
  ${msg_files}
)

# Instalar scripts como ejecutables (se instalan en lib/robot_vision/)
install(PROGRAMS
  robot_vision/robot_driver.py
  robot_vision/navegacion.py
  robot_vision/robot_vision_node.py
  DESTINATION lib/${PROJECT_NAME}
)

# Instalar archivo launch
install(FILES
  launch/robot_vision.launch.py
  DESTINATION share/${PROJECT_NAME}/launch
)

# Opcional: copiar mensajes generados (por si no se copian solos)
install(DIRECTORY
  ${CMAKE_CURRENT_BINARY_DIR}/rosidl_generator_py/${PROJECT_NAME}/
  DESTINATION lib/python3.13/site-packages/${PROJECT_NAME}
  PATTERN "*.pyc" EXCLUDE
)

# Exportar dependencias
ament_export_dependencies(rosidl_default_runtime)

# Empaquetar
ament_package()
