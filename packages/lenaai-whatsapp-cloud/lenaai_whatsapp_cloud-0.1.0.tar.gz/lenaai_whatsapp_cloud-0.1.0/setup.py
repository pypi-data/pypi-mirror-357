from setuptools import setup, find_packages

setup(
    name="lenaai-whatsapp-cloud",
    version="0.1.0",
    description="A library for WhatsApp Cloud and related messaging integrations.",
    author="LenaAI",
    author_email="dev@lenaai.net",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # Dependencies will be read from requirements.txt
    ],
    python_requires=">=3.9",
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 