from setuptools import setup, find_packages

setup(
    name="win32-sysgrow",
    version="1.0.1",
    author="AleirJDawn",
    author_email="",
    description="Python toolkit for automating the installation and configuration of various useful software and system settings on Windows",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),   
    python_requires='>=3.6', 
    include_package_data=True,
    install_requires=[
        'requests',
        'tqdm',
        'rarfile',
        'pywin32',
        'pycryptodome',

    ],
    package_data={
        'win32_sysgrow': ['*.exe', '*.dll', '*.bat', '*.cmd'],
    },
    entry_points={     
        'console_scripts': [
            'sysgrow=win32_sysgrow.main:main', 
        ],
    },
    classifiers=[      
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
