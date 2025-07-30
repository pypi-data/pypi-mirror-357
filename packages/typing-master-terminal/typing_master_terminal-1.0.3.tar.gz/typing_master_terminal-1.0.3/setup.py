from setuptools import setup, find_packages

try:
    with open("requirements.txt") as f:
        requirements = f.read().splitlines()
except FileNotFoundError:
    requirements = []


setup(
    name="typing_master_terminal",
    version="1.0.3",
    description="A terminal-based typing game with animations and score tracking",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Aditya",
    author_email="spliots09@gmail.com",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "typing-master=typing_test.main:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
