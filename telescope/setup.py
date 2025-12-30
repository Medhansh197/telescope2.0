from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="telescope-weather-app",
    version="1.0.0",
    author="Telescope Weather Team",
    author_email="contact@telescopeweather.com",
    description="A comprehensive web application for monitoring weather conditions optimal for telescope viewing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/telescope-weather-app",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Astronomy",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Framework :: Flask",
        "Environment :: Web Environment",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "telescope-weather=app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["templates/*.html", "*.csv", "*.md", "*.txt"],
    },
    keywords="telescope weather astronomy stargazing conditions forecast",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/telescope-weather-app/issues",
        "Source": "https://github.com/yourusername/telescope-weather-app",
        "Documentation": "https://github.com/yourusername/telescope-weather-app/blob/main/README.md",
    },
)