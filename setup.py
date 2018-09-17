from setuptools import setup
setup(name="espurna-dev-builder",
      version="1.0",
      description="ESPurna dev branch builder utility",
      author="Maxim Prokhorov",
      license="License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
      install_requires=[
          "requests"
      ],
      packages=["espurna_dev_builder"])
