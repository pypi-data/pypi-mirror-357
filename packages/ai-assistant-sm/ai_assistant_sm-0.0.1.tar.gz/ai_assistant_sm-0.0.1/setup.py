from setuptools import setup, find_packages

setup(
    name="ai_assistant_sm",
    version="0.0.1",
    author="Arun CS",
    author_email="aruncs31s@proton.com",
    description="Sub Module for AI Assistant Project",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(where="src"),  
    package_dir={"": "src"}, 
    include_package_data=True,
    install_requires=[
        "requests",
        "SpeechRecognition",
    ],
   
)