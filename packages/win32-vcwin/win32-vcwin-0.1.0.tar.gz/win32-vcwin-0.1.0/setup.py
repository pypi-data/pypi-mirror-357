from setuptools import setup, find_packages

setup(
    name="win32-vcwin",
    version="0.1.0",
    author="AleirJDawn",
    author_email="",
    description="win32-vcwin is a command-line tool for Windows developers to inspect, install, uninstall, and manage components such as Visual C++ Tools, Windows SDK, WDK, and DirectX SDK.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),   
    python_requires='>=3.6', 
    include_package_data=True,
    package_data={
        'win32_vcwin': ['*.exe'],
    },
    entry_points={     
        'console_scripts': [
            'vcwin=win32_vcwin.main:main', 
        ],
    },
    classifiers=[      
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
