from setuptools import setup
setup(name="espurna-nightly-builder",
      version="1.0",
      description="ESPurna nightly builder utility",
      author="Maxim Prokhorov",
      license="License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
      install_requires=[
          "requests"
      ],
      packages=["espurna_nightly_builder"],
      entry_points={
          "console_scripts": [
              "espurna_nightly = espurna_nightly_builder.__main__:main"
          ]
      }
)
