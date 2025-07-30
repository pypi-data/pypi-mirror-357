from setuptools import setup, find_packages

setup(
    name="RvLProMaster",
    version="0.1.3",
    packages=find_packages(),
    install_requires=[
        "aiohttp[speedups]",
        "asyncio",
        "python-dotenv",
        "telegraph",
        "openai",
        "google-genai",
        "markdown",
        "yt-dlp",
        "Pillow"
    ],
    author="YudhoPatrianto",
    author_email="kydh01123@gmail.com",
    description="The Telegram Bot API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/YudhoPRJKT-Teams/RvLProMaster",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.12',
)
