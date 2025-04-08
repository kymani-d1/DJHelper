from setuptools import setup, find_packages

setup(
    name="mixxx-ai-copilot",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="An AI copilot extension for Mixxx DJ software that learns and replicates a user's DJ style",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mixxx-ai-copilot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio :: Mixers",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests",
        "sqlalchemy",
        "numpy",
        "pandas",
        "scikit-learn",
        "pyqt5",
        "soundcloud-api",
    ],
    entry_points={
        "console_scripts": [
            "mixxx-ai-copilot=src.ui.main_window:main",
        ],
    },
)