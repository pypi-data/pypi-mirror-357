from setuptools import setup, find_packages

setup(
    name="shiva-si",
    version="1.0.0",
    author="Siddique Shiva",
    author_email="easwararaj05687@gmail.com",
    description="A model saving/loading format (.si) for AI/ML, similar to .pt or .npy",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/siddiquesh/shiva-si",
    packages=find_packages(),
    install_requires=[
        "torch>=1.12.0",
        "tensorflow==2.10.1",
        "onnx>=1.12.0",
        "psutil",
        "cython",
        "numpy<2.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",  
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    license="Proprietary"  
)
