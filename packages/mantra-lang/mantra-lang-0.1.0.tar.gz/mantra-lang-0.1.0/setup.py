from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mantra-lang",
    version="0.1.0",
    author="Mantra Team",
    author_email="team@mantra-lang.org",
    description="A Sanskrit-inspired programming language for concise, expressive code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mantra-lang/mantra",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Interpreters",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies for core functionality
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
        "gui": [
            "tkinter",  # For yantra GUI features
        ],
    },
    entry_points={
        "console_scripts": [
            "mantra=mantra.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "mantra": ["examples/*.man"],
    },
    keywords="programming-language sanskrit interpreter compiler",
)