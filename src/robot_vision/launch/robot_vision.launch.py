#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([

        # Nodo de detección de pelota (cámara + YOLO)
        Node(
            package='robot_vision',
            executable='robot_vision_node.py',   # nombre del script (con extensión .py)
            name='yolo_node',
            output='screen',
            # Si quieres pasar parámetros al nodo, se añaden aquí
            # parameters=[{'param': 'value'}]
        ),

        # Nodo driver serial (comunicación con Arduino)
        Node(
            package='robot_vision',
            executable='robot_driver.py',        # script instalado
            name='robot_driver',
            output='screen',
            parameters=[{
                'port': '/dev/ttyACM0',          # Puerto serial del Arduino
                'baudrate': 9600,
                'timeout': 1.0,
            }]
        ),

        # Nodo de navegación (lógica de control)
        Node(
            package='robot_vision',
            executable='navegacion.py',          # script instalado
            name='navegacion',
            output='screen',
            parameters=[{
                'modo_auto': True,               # True = automático, False = manual
                'velocidad_base': 150,
                'tolerancia_centro': 80,
                'area_min': 25000,
            }]
        ),
    ])
