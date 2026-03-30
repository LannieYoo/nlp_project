from setuptools import find_packages, setup

package_name = 'aisd_vision'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='zhizhunbao',
    maintainer_email='402707192@qq.com',
    description='ROS 2 vision package for hand gesture recognition using MediaPipe',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'image_publisher = aisd_vision.image_publisher:main',
            'hands = aisd_vision.hands:main',
        ],
    },
)

