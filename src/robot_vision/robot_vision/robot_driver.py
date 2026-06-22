#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from robot_vision.msg import SensorData, MotorCmd

import serial
import serial.tools.list_ports
import time

class RobotDriverNode(Node):
    def __init__(self):
        super().__init__('robot_driver')

        # Parámetros
        self.declare_parameter('port', '')  # Si está vacío, auto-detecta
        self.declare_parameter('baudrate', 9600)
        self.declare_parameter('timeout', 1.0)

        port = self.get_parameter('port').value
        baudrate = self.get_parameter('baudrate').value
        timeout = self.get_parameter('timeout').value

        # Auto-detección si no se especifica puerto
        if not port:
            port = self._find_port()
            if not port:
                self.get_logger().error('No se encontró puerto serial')
                raise RuntimeError('No se encontró puerto serial')
        self.get_logger().info(f'Conectado a {port}')

        # Abrir serial
        try:
            self.ser = serial.Serial(port, baudrate, timeout=timeout)
            time.sleep(2)  # Esperar a que Arduino reinicie
        except Exception as e:
            self.get_logger().error(f'Error al abrir serial: {e}')
            raise

        # Publicador de datos de sensores
        self.sensor_pub = self.create_publisher(SensorData, '/sensor_data', 10)

        # Suscriptor para comandos de motores
        self.cmd_sub = self.create_subscription(
            MotorCmd, '/motor_cmd', self.cmd_callback, 10
        )

        # Temporizador para leer el puerto serial (10 Hz)
        self.timer = self.create_timer(0.1, self.read_serial)

        self.get_logger().info('RobotDriverNode iniciado')

    def _find_port(self):
        for p in serial.tools.list_ports.comports():
            if 'ttyACM' in p.device or 'ttyUSB' in p.device:
                return p.device
        return None

    def read_serial(self):
        try:
            line = self.ser.readline().decode(errors='ignore').strip()
            if not line:
                return
            # Formato esperado: color1,color2,color3,distI,distD,distF,distB,enc1,enc2,enc3
            partes = line.split(',')
            if len(partes) != 10:
                return
            msg = SensorData()
            msg.color1 = int(partes[0])
            msg.color2 = int(partes[1])
            msg.color3 = int(partes[2])
            msg.dist_izq = float(partes[3])
            msg.dist_der = float(partes[4])
            msg.dist_front = float(partes[5])
            msg.dist_back = float(partes[6])
            msg.enc1 = int(partes[7])
            msg.enc2 = int(partes[8])
            msg.enc3 = int(partes[9])
            self.sensor_pub.publish(msg)
        except Exception as e:
            self.get_logger().warn(f'Error leyendo serial: {e}')

    def cmd_callback(self, msg):
        # Enviar comando M:v1,v2,v3\n al Arduino
        cmd = f"M:{msg.motor1},{msg.motor2},{msg.motor3}\n"
        try:
            self.ser.write(cmd.encode())
        except Exception as e:
            self.get_logger().warn(f'Error enviando comando: {e}')

    def destroy_node(self):
        self.ser.close()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = RobotDriverNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
