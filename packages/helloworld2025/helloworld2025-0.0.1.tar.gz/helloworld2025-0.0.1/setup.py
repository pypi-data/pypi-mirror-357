from setuptools import setup 
setup(
    name="helloworld2025",
    version="0.0.1",
    description="This is a hello world package",
    py_modules=["hello_world"],
    package_dir={'':'src'},
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    extras_require={
        "dev":[
            "pytest>=3.7",
        ]
    })