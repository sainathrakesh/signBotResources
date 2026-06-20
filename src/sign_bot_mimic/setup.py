from setuptools import find_packages, setup

package_name = 'sign_bot_mimic'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='pepper',
    maintainer_email='shendge.vishal.vilas@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        'holistic_data_collector = sign_bot_recognition.holistic_data_collector:main',
        ],
    },
)
