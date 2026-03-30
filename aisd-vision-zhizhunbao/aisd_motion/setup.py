from setuptools import find_packages, setup

package_name = 'aisd_motion'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='zhizhunbao',
    maintainer_email='402707192@qq.com',
    description='ROS 2 motion control package that converts hand gestures to robot motion commands',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'move = aisd_motion.move:main',
        ],
    },
)

