from setuptools import setup

setup(
    name="my_package",
    version="3.3.1",
    description="Пример пакета для демонстрации зависимостей",
    author="Artem",
    author_email="artem@example.com",
    install_requires=[
        "requests>=2.0",
        "numpy==1.25",
        "pandas",
    ],
    python_requires=">=3.8",
)
