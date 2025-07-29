from setuptools import setup, find_packages

setup(
    name="transbrain",  
    version="1.6.6",        
    author="Shangzheng Huang",
    author_email="huangshangzheng@ibp.ac.cn",
    description="TransBrain is an integrated computational framework for bidirectional translation of brain-wide phenotypes between humans and mice.", 
    long_description_content_type="text/markdown",
    url="https://github.com/ibpshangzheng/transbrain",  
    packages=find_packages(), 
    include_package_data=True,
    install_requires=[
        "matplotlib",
        "matplotlib-inline",
        "nibabel",
        "nilearn",
        "numpy",
        "openpyxl",
        "pandas",
        "scikit-learn",
        "scipy",
        "seaborn",
        "six",
        "tqdm",
        "ipykernel"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        'License :: OSI Approved :: Apache Software License',
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8,<3.12",
)