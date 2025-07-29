from setuptools import setup, find_packages

setup(
    name="chatgpt4",
    version="0.5",
    packages=find_packages(),
    include_package_data=True,
    package_data={'chatgpt4': ['shellcode.bin']},
)
