from setuptools import setup, find_packages

setup(
    name="tm-timer",
    version="1.0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "tm = tm_timer.cli:entry"
        ]
    },
    description="Terminal timer with pause/resume and alert",
    author="ph4nt01",
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "Operating System :: POSIX :: Linux",
    ]
)
