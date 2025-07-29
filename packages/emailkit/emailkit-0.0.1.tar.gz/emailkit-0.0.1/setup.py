from setuptools import setup

setup(
    name="emailkit",
    version="0.0.1",
    description="This is python email package",
    # Correctly points to the single module file within the 'src' directory
    py_modules=["emailkit"], # No .py extension here, setuptools adds it
    package_dir={'': 'src'},
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    extras_require={
        "dev":[
            "pytest>=3.7",
        ]
    }
)