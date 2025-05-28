from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="dutch-anwb-hyde-chatbot",
    version="1.0.0",
    author="ANWB HyDE Chatbot Team",
    author_email="your.email@example.com",
    description="Dutch ANWB HyDE Chatbot - RAG system with Memory and HyDE for ANWB T&C International roadside assistance",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hnsmr/dutch-ANWB-hyde-chatbot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
    },
    entry_points={
        "console_scripts": [
            "anwb-chatbot=anwb_chatbot_app:main",
        ],
    },
    keywords="chatbot, RAG, HyDE, ANWB, Dutch, NLP, AI, streamlit, memory, international, roadside assistance",
    project_urls={
        "Bug Reports": "https://github.com/hnsmr/dutch-ANWB-hyde-chatbot/issues",
        "Source": "https://github.com/hnsmr/dutch-ANWB-hyde-chatbot",
        "Documentation": "https://github.com/hnsmr/dutch-ANWB-hyde-chatbot#readme",
    },
) 