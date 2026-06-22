from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'robot_vision'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='centron2026',
    maintainer_email='centron2026@todo.todo',
    description='Nodos para control de robot móvil con detección de pelota',
    license='TODO: License declaration',
    entry_points={
        'console_scripts': [
            'yolo_node = robot_vision.robot_vision_node:main',
            'robot_driver = robot_vision.robot_driver:main',
            'navegacion = robot_vision.navegacion:main',
        ],
    },
)
