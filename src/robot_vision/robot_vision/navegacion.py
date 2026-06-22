#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from robot_vision.msg import SensorData, MotorCmd, BallDetection

import time

class NavigationNode(Node):
    def __init__(self):
        super().__init__('navegacion')

        # Parámetros
        self.declare_parameter('modo_auto', True)
        self.declare_parameter('velocidad_base', 150)
        self.declare_parameter('tolerancia_centro', 80)
        self.declare_parameter('area_min', 25000)

        self.modo_auto = self.get_parameter('modo_auto').value
        self.vel_base = self.get_parameter('velocidad_base').value
        self.tolerancia = self.get_parameter('tolerancia_centro').value
        self.area_min = self.get_parameter('area_min').value

        # Publicador de comandos de motores
        self.cmd_pub = self.create_publisher(MotorCmd, '/motor_cmd', 10)

        # Suscriptores
        self.sensor_sub = self.create_subscription(
            SensorData, '/sensor_data', self.sensor_callback, 10
        )
        self.ball_sub = self.create_subscription(
            BallDetection, '/ball', self.ball_callback, 10
        )

        # Variables de estado
        self.ultimo_sensor = None
        self.ultima_pelota = None
        self.ultimo_evado = 0.0
        self.tiempo_evasion = 0.35

        # Temporizador para lógica de control (10 Hz)
        self.timer = self.create_timer(0.1, self.control_loop)

        self.get_logger().info('NavigationNode iniciado')

    def sensor_callback(self, msg):
        self.ultimo_sensor = msg

    def ball_callback(self, msg):
        self.ultima_pelota = msg

    def control_loop(self):
        if self.ultimo_sensor is None:
            return

        # 1) Evasión de línea blanca (prioritaria)
        if self._evadir_linea_blanca():
            return

        # 2) Si modo automático, seguir pelota
        if self.modo_auto:
            self._seguir_pelota()
        else:
            # Modo manual: no moverse (el usuario controla por otro medio)
            self._enviar_comando(0, 0, 0)

    def _evadir_linea_blanca(self):
        sensor = self.ultimo_sensor
        blancos = []
        if sensor.color1 == 1: blancos.append(1)  # S1
        if sensor.color2 == 1: blancos.append(2)  # S2
        if sensor.color3 == 1: blancos.append(3)  # S3

        if not blancos:
            return False

        # Mapeo de sensores a ángulos y direcciones de evasión
        angulos = {1: 90, 2: 210, 3: 330}
        direcciones = {270: 'atras', 30: 'derecha', 150: 'izquierda'}

        if len(blancos) == 1:
            ang = angulos[blancos[0]]
            ang_op = (ang + 180) % 360
            dir_ev = direcciones.get(ang_op, 'atras')
        else:
            dir_ev = 'atras'

        ahora = time.time()
        if ahora - self.ultimo_evado < self.tiempo_evasion:
            return True

        self.ultimo_evado = ahora

        # Aplicar movimiento de evasión
        velocidades = {
            'atras': (-self.vel_base, -self.vel_base, -self.vel_base),
            'izquierda': (self.vel_base, -self.vel_base, self.vel_base),
            'derecha': (self.vel_base, -self.vel_base, -self.vel_base),
        }
        v1, v2, v3 = velocidades.get(dir_ev, (0, 0, 0))
        self._enviar_comando(v1, v2, v3)
        return True

    def _seguir_pelota(self):
        if self.ultima_pelota is None:
            # Si no hay pelota, girar para buscarla
            self._enviar_comando(self.vel_base, -self.vel_base, self.vel_base)
            return

        cx = self.ultima_pelota.cx
        area = self.ultima_pelota.area
        centro_imagen = 320  # Asumiendo ancho 640

        # Decidir movimiento
        if cx < centro_imagen - self.tolerancia:
            self._enviar_comando(self.vel_base, -self.vel_base, self.vel_base)  # izquierda
        elif cx > centro_imagen + self.tolerancia:
            self._enviar_comando(self.vel_base, -self.vel_base, -self.vel_base)  # derecha
        else:
            if area < self.area_min:
                self._enviar_comando(self.vel_base, self.vel_base, self.vel_base)  # adelante
            else:
                self._enviar_comando(0, 0, 0)  # detener

    def _enviar_comando(self, v1, v2, v3):
        cmd = MotorCmd()
        cmd.motor1 = int(v1)
        cmd.motor2 = int(v2)
        cmd.motor3 = int(v3)
        self.cmd_pub.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = NavigationNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
