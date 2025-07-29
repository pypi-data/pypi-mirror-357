from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cue-audio",
    version="1.0.0",
    author="Alex Wales",
    author_email="alexwaiteuk@gmail.com",
    description="Simple, elegant spatial audio orchestration for immersive experiences",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alexwales/cue-audio",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: System :: Hardware",
        "Topic :: Home Automation",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pyaudio>=0.2.11",
        "paho-mqtt>=1.6.0", 
        "numpy>=1.21.0",
    ],
    keywords="audio spatial surround mqtt immersive sound automation",
    project_urls={
        "Bug Reports": "https://github.com/alexwales/cue-audio/issues",
        "Source": "https://github.com/alexwales/cue-audio/",
        "Documentation": "https://github.com/alexwales/cue-audio#readme",
    },
) 