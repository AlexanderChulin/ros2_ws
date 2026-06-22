#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ============================================================
# Nodo ROS2 - Detección de Pelota
# Raspberry Pi 4 + IMX219 NoIR + YOLOv8 Entrenado
# Publica en el tópico /ball con el mensaje BallDetection
# ============================================================

import rclpy
from rclpy.node import Node
from robot_vision.msg import BallDetection

from ultralytics import YOLO
from picamera2 import Picamera2
import cv2
import numpy as np

# ============================================================
# CONFIGURACIÓN
# ============================================================

MODEL_PATH = "/home/centron2026/ros2_ws/src/robot_vision/models/pelota_best.pt"

CONF_THRESHOLD = 0.25

CAM_WIDTH = 640
CAM_HEIGHT = 480

AREA_MIN = 150
AREA_MAX = 120000

ASPECT_RATIO_MIN = 0.5
ASPECT_RATIO_MAX = 1.5

# ============================================================
# CLAHE
# ============================================================

clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))

def mejorar_contraste(frame):
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l = clahe.apply(l)
    lab = cv2.merge((l, a, b))
    frame_clahe = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    gray = cv2.cvtColor(frame_clahe, cv2.COLOR_BGR2GRAY)
    gray_eq = cv2.equalizeHist(gray)
    frame_eq = cv2.cvtColor(gray_eq, cv2.COLOR_GRAY2BGR)
    return cv2.addWeighted(frame_clahe, 0.7, frame_eq, 0.3, 0)

# ============================================================
# NODO
# ============================================================

class BallDetectorNode(Node):
    def __init__(self):
        super().__init__('ball_detector_node')

        # Publicador del mensaje BallDetection
        self.publisher = self.create_publisher(BallDetection, 'ball', 10)

        self.get_logger().info("Cargando modelo...")
        self.model = YOLO(MODEL_PATH)

        self.get_logger().info("Inicializando cámara...")
        self.picam2 = Picamera2()
        config = self.picam2.create_preview_configuration(
            main={"size": (CAM_WIDTH, CAM_HEIGHT), "format": "RGB888"}
        )
        self.picam2.configure(config)
        self.picam2.start()

        # Ajustes de color
        try:
            self.picam2.set_controls({
                "AwbEnable": False,
                "ColourGains": (1.6, 1.2)
            })
        except Exception as e:
            self.get_logger().warn(f"No se pudieron aplicar controles: {e}")

        # Temporizador a 5 FPS (0.2 s)
        self.timer = self.create_timer(0.2, self.loop)
        self.get_logger().info("Nodo iniciado correctamente")

    # ==========================================================
    # LOOP PRINCIPAL
    # ==========================================================

    def loop(self):
        try:
            frame = self.picam2.capture_array()
        except Exception as e:
            self.get_logger().warn(f"Error capturando imagen: {e}")
            return

        if frame is None:
            return

        # Convertir RGB a BGR para OpenCV
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame_mejorado = mejorar_contraste(frame)

        # Inferencia YOLO
        results = self.model(
            frame_mejorado,
            imgsz=640,
            conf=CONF_THRESHOLD,
            verbose=False
        )

        mejor_conf = 0.0
        mejor_box = None
        area = 0.0

        for r in results:
            if r.boxes is None:
                continue
            for box in r.boxes:
                cls = int(box.cls[0])
                label = self.model.names[cls]
                if label != "pelota":
                    continue
                conf = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                ancho = x2 - x1
                alto = y2 - y1
                area_actual = ancho * alto
                aspect = ancho / alto if alto > 0 else 0

                # Filtros de área y aspecto
                if area_actual < AREA_MIN or area_actual > AREA_MAX:
                    continue
                if aspect < ASPECT_RATIO_MIN or aspect > ASPECT_RATIO_MAX:
                    continue

                if conf > mejor_conf:
                    mejor_conf = conf
                    mejor_box = (x1, y1, x2, y2)
                    area = area_actual

        # Publicar si se detectó pelota
        if mejor_box is not None:
            x1, y1, x2, y2 = mejor_box
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            msg = BallDetection()
            msg.cx = float(cx)
            msg.cy = float(cy)
            msg.area = float(area)
            msg.confidence = float(mejor_conf)

            self.publisher.publish(msg)
            self.get_logger().info(
                f"Pelota: cx={cx}, cy={cy}, area={area}, conf={mejor_conf:.2f}"
            )

    # ==========================================================
    # LIMPIEZA
    # ==========================================================

    def destroy_node(self):
        try:
            self.picam2.stop()
        except:
            pass
        super().destroy_node()

# ============================================================
# MAIN
# ============================================================

def main(args=None):
    rclpy.init(args=args)
    node = BallDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
