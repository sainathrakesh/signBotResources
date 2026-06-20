from setuptools import setup
import os
from glob import glob

package_name = 'sign_bot_publisher'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        # Required for ament_index_python to locate the package
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        # Install the package-level files
        ('share/' + package_name, ['package.xml']),
        # Install the config YAML file to share/
        (os.path.join('share', package_name, 'config'),
            glob(os.path.join(package_name, 'config', '*.yaml'))),
    ],
    install_requires=[
        'setuptools',
        'pyyaml',
        'ament_index_python',
    ],
    zip_safe=True,
    maintainer='pepper',
    maintainer_email='shendge.vishal.vilas@gmail.com',
    description='Joint state publisher for sign bot using YAML-defined poses',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'sign_joint_publisher = sign_bot_publisher.sign_joint_publisher:main'
        ],
    },
)
