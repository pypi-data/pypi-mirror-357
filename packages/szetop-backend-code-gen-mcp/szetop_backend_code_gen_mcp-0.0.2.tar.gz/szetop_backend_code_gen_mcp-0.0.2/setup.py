from setuptools import setup, find_packages

setup(
    name="szetop-backend-gen-mcp",
    version="0.0.3",
    description="易图后端代码生成MCP服务",
    author="szetop",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "mcp>=1.2.0",
        "anthropic>=0.8.0",
        "openai>=1.0.0",
        "python-dotenv>=1.0.0",
        "Pillow>=10.0.0",
        "numpy>=1.26.0",
        "pandas>=2.1.0",
        "pytesseract>=0.3.13",
        "javalang>=0.13.0",
        "requests>=2.32.4",
        "cryptography>=45.0.4",
        "json5>=0.12.0"
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.23.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
            "ruff>=0.1.0",
        ]
    },
)
