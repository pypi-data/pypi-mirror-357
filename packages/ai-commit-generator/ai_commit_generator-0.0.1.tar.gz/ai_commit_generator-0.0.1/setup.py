from setuptools import setup, find_packages

# Read README for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

setup(
    name="ai_commit_generator",
    version="0.0.1",
    author="Azat Antonyan",
    author_email="azat.antonyan65@gmail.com",
    description="AI-powered Git commit message generator using various LLM providers",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Zt0/ai_commit_generator",
    project_urls={
        "Bug Tracker": "https://github.com/Zt0/ai_commit_generator/issues",
        "Documentation": "https://github.com/Zt0/ai_commit_generator#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pathspec>=0.12.1",         # used for file pattern matching (diff filtering?)
        "cohere>=5.15.0",           # required if you're using Cohere API
        "openai>=1.86.0",           # required for OpenAI integration
        "python-dotenv>=1.1.0",     # for environment variable loading
        "pre-commit>=4.2.0",        # if you want to run pre-commit hooks programmatically or recommend it
        "click>=8.2.1",             # CLI interface
    ],
    extras_require={
        "cohere": ["cohere>=5.15.0"],
        "openai": ["openai>=1.0.0"],
        "anthropic": ["anthropic>=0.3.0"],
    },
    entry_points={
        "console_scripts": [
            "ai_commit_generator=ai_commit_generator.cli:main",
        ],
    },
    include_package_data=True,
    keywords="git commit ai llm automation development tools",
)
