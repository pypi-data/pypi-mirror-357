from setuptools import setup, find_packages

setup(
    name="bitmark",
    version="1.0.1",
    author="AleirJDawn",
    author_email="",
    description="bitmark is a simple yet powerful utility to manage and parse bitflags represented as hexadecimal values, with support for user-defined flag sets stored in YAML files.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),   
    python_requires='>=3.6', 
    include_package_data=True,
    install_requires=[
        'pyyaml'
    ],
    entry_points={     
        'console_scripts': [
            'bitmark=bitmark.main:main', 
        ],
    },
    classifiers=[      
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
