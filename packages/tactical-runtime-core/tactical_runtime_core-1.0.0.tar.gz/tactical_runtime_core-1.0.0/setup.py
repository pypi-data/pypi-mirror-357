from setuptools import setup, find_packages

setup(
    name="tactical_runtime_core",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'tactical-runtime=tactical_runtime_core.main:main',
        ],
    },
    author="S.R. Bryant",
    author_email="",
    description="Tactical Runtime Core CLI SDK",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/tactical-runtime-core",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
