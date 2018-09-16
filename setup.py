from setuptools import setup
setup(name="espurna-dev-builder",
      version="1.0",
      description="https://github.com/xoseperez/espurna dev branch builder",
      author="Maxim Prokhorov",
      license="GPL-3",
      install_requires=[
          "requests"
      ],
      packages=["espurna_dev_builder"])
