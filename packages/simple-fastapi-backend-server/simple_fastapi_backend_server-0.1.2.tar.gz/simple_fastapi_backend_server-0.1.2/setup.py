from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='simple_fastapi_backend_server',
    version='0.1.2',
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'uvicorn',
    ],
    entry_points={
        'console_scripts': [
            'simple_fastapi_backend_server = simple_fastapi_backend_server.main:start'
        ]
    },
    author='Ataur Rahman',
    description='A simple FastAPI wrapper package for quick testing of auth endpoints.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.7',
)
