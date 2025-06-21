from setuptools import setup, find_packages

setup(
    name="ghost-bot",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'python-telegram-bot==13.7',
        'requests>=2.31.0',
        'python-decouple>=3.8',
        'aiosqlite>=0.19.0',
        'pytz>=2023.3',
        'python-dateutil>=2.8.2',
        'urllib3>=1.26.0,<2.0.0',
        'six>=1.16.0',
        'Pillow>=10.0.0',
    ],
    python_requires='>=3.8',
    include_package_data=True,
)
