from setuptools import find_packages, setup

package_name = 'aisd_hearing'

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
    description='ROS 2 hearing package for audio recording and speech recognition',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'recording_publisher = aisd_hearing.recording_publisher:main',
            'words_publisher = aisd_hearing.words_publisher:main',
            'ollama_publisher = aisd_hearing.ollama_publisher:main',
            'speak_client = aisd_hearing.speak_client:main',
        ],
    },
)

