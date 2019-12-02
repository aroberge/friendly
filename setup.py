# pylint: skip-file
from setuptools import setup, find_packages
from friendly_traceback import version

version_ = version.__version__

with open("README.md", encoding="utf8") as f:
    README = f.read()

setup(
    name="friendly-traceback",
    version=version_,
    description="Friendlier tracebacks in any language.",
    long_description=README,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 1 - Planning",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Intended Audience :: Education",
        "Topic :: Education",
    ],
    url="https://github.com/aroberge/friendly-traceback",
    author="André Roberge",
    author_email="Andre.Roberge@gmail.com",
    packages=find_packages(exclude=["dist", "build", "tools", "tests", "demos"]),
    package_data={"gettext": ["friendly_traceback/locales/*"]},
    include_package_data=True,
    zip_safe=False,
)
