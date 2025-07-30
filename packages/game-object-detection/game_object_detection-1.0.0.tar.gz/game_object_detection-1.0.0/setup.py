from setuptools import setup, find_packages

setup(
    name="game-object-detection",
    version="1.0.0",
    author="Alex",
    author_email="thettboy11@gmail.com",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "torch>=1.9.0",
        "ultralytics>=8.0.0",
        "opencv-python>=4.5.0",
        "numpy>=1.21.0",
        "Pillow>=8.0.0",
        "scikit-learn>=1.0.0",
        "PyYAML>=6.0",
    ],
)