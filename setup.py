from setuptools import setup, find_packages

setup(
    name="flask-app",
    version="1.0.0",
    description="Flask app for CI/CD pipeline demo",
    packages=find_packages(),
    install_requires=[
        "flask==3.0.3",
        "gunicorn==22.0.0",
    ],
)