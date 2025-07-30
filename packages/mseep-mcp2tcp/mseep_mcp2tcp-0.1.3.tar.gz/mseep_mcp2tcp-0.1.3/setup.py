
from setuptools import setup, find_packages

setup(
    name="mseep-mcp2tcp",
    version="0.1.3",
    description="MCP TCP Service for PWM Control",
    long_description="Package managed by MseeP.ai",
    long_description_content_type="text/plain",
    author="mseep",
    author_email="support@skydeck.ai",
    maintainer="mseep",
    maintainer_email="support@skydeck.ai",
    url="",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=['mcp>=1.1.2', 'pyyaml>=6.0.1', 'httpx>=0.28.1'],
    keywords=["mseep"] + ['mcp', 'tcp', 'pwm', 'ai', 'llm'],
)
