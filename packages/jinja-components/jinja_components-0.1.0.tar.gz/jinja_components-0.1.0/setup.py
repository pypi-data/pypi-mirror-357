from setuptools import setup, find_packages

setup(
    name="jinja-components",
    version="0.1.0",
    author="Tamer Hamad Faour",
    author_email="info@denkengewinnen.com",
    description="Reusable Jinja2 HTML components and macros for Flask, Django, and Jinja projects.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/TamerOnLine/jinja-ui",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Jinja2>=3.0",
        "polib",
        "googletrans==4.0.0-rc1",
        "Babel"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Flask",
        "Framework :: Django"
    ],
    python_requires=">=3.7",
)
