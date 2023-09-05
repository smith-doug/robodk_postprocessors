from setuptools import find_packages, setup

setup(
    name='robodk_postprocessors',
    version='0.0.1',
    author='RoboDK',
    license='Apache-2.0',
    packages=find_packages(),
    url='https://robodk.com/post-processors',
    install_requires=['dataclass_wizard', 'numpy']
)
