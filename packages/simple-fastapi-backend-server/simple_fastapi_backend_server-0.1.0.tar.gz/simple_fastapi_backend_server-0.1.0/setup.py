from setuptools import setup, find_packages

setup(
    name='simple-fastapi-backend-server',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'uvicorn',
    ],
    entry_points={
        'console_scripts': [
            'simple-fastapi-backend-server = simple_fastapi_backend_server.main:start'
        ]
    },
    author='Ataur Rahman',
    description='A simple FastAPI wrapper package',
    python_requires='>=3.7',
)
