
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-pyautogui-server",
    version="0.1.2",
    description="MCP server for pyautogui",
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
    install_requires=['fastmcp>=0.4.1', 'pillow>=11.1.0', 'pyautogui>=0.9.54'],
    keywords=["mseep"] + ['pyautogui', 'mcp', 'automation', 'gui'],
)
