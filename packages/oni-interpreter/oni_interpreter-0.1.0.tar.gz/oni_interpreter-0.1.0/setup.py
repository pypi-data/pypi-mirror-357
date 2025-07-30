from setuptools import setup

setup(
    name="oni-interpreter",
    version="0.1.0",
    py_modules=["oni_interpreter"],
    entry_points={
        "console_scripts": [
            "oni=oni_interpreter:main"
        ]
    },
    author="Arthur Fillipy",
    author_email="arthurfillipy20@gmail.com",
    description="Interpretador da linguagem Oni/Uni",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
