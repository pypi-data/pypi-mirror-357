from setuptools import setup, find_packages

setup(
    name='fastapi_grpc_bridge',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'grpcio',
        'grpcio-tools',
        'pydantic',
        'protobuf',
        'uvicorn'
    ],
    entry_points={
        'console_scripts': [
            'fastapi-grpc=fastapi_grpc_bridge.grpc_server:main',
        ],
    },
)
