from setuptools import setup
from setuptools.command.install import install

class PostInstallCommand(install):
    def run(self):
        print("hello world from https://hackerone.com/thruster")
        install.run(self)

setup(
    name="jd-mlops",
    version="0.1",
    cmdclass={
        'install': PostInstallCommand,
    },
    author="Your Name",
    author_email="you@example.com",
    description="Just prints hello from thruster",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.6',
)