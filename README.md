# ROS2 Workspace - Robot Vision

Sistema de control para robot móvil basado en ROS2 (Jazzy). Incluye nodos para comunicación con Arduino, detección de pelota con YOLO y navegación autónoma con evasión de línea blanca.

## Características

- Nodo driver serial (`robot_driver`) que se comunica con un Arduino para leer sensores (color, distancia, encoders) y enviar comandos de motores.
- Nodo de detección de pelota (`yolo_node`) que usa una cámara Raspberry Pi (IMX219 NoIR) con YOLOv8 para detectar una pelota.
- Nodo de navegación (`navegacion`) que implementa:
  - Evasión prioritaria de línea blanca usando sensores de color.
  - Seguimiento de la pelota en modo automático.
  - Modo manual (solo visualización de la cámara).
- Mensajes personalizados:
  - `SensorData`: colores, distancias, encoders.
  - `MotorCmd`: velocidades para tres motores.
  - `BallDetection`: centro, área y confianza de la pelota.

## Requisitos

- ROS2 Jazzy (o Humble) instalado.
- Python 3.13 (o compatible).
- Dependencias Python:
  - `pyserial`
  - `ultralytics`
  - `opencv-python`
  - `picamera2` (para Raspberry Pi)
- Arduino conectado vía USB (puerto `/dev/ttyACM0` o `/dev/ttyUSB0`).
- Cámara Raspberry Pi configurada y funcionando.

## Instalación

Clona este repositorio en tu workspace de ROS2:

```bash
cd ~/ros2_ws/src
git clone https://github.com/AlexanderChulin/ros2_ws.git robot_vision
cd ~/ros2_ws

Instala las dependencias Python:

pip3 install pyserial ultralytics opencv-python picamera2

Compila el paquete:

colcon build --packages-select robot_vision
source install/setup.bash

Lanzar todos los nodos con el launch file

ros2 launch robot_vision robot_vision.launch.py

Ejecutar nodos individualmente

# Driver serial (con parámetro de puerto)
ros2 run robot_vision robot_driver.py --ros-args -p port:=/dev/ttyACM0

# Navegación
ros2 run robot_vision navegacion.py

# Detección de pelota
ros2 run robot_vision robot_vision_node.py

Tópicos disponibles

    /sensor_data (robot_vision/msg/SensorData) – datos de sensores del Arduino.

    /motor_cmd (robot_vision/msg/MotorCmd) – comandos de velocidad para los motores.

    /ball (robot_vision/msg/BallDetection) – detección de la pelota.

Visualizar datos en tiempo real

ros2 topic echo /sensor_data
ros2 topic echo /ball
ros2 topic echo /motor_cmd

Parámetros configurables

En el launch file se pueden ajustar:

    port: puerto serial (ej. /dev/ttyACM0).

    modo_auto: True para modo automático, False para manual.

    velocidad_base: velocidad de los motores (0-255).

    tolerancia_centro: margen de error para centrar la pelota.

    area_min: área mínima de la pelota para considerarla cercana.

Estructura del paquete

robot_vision/
├── CMakeLists.txt
├── package.xml
├── setup.py
├── launch/
│   └── robot_vision.launch.py
├── msg/
│   ├── SensorData.msg
│   ├── MotorCmd.msg
│   └── BallDetection.msg
├── robot_vision/
│   ├── __init__.py
│   ├── robot_driver.py
│   ├── navegacion.py
│   └── robot_vision_node.py
└── models/
    └── pelota_best.pt
