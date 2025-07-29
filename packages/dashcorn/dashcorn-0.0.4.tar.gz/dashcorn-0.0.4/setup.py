#!/usr/bin/env python

import setuptools

setuptools.setup(
  name = 'dashcorn',
  version = '0.0.4',
  description = 'A dashboard for FastAPI/Uvicorn',
  author = 'acegik',
  license = 'GPL-3.0',
  license_files = 'LICENSE',
  url = 'https://github.com/dashcorn/dashcorn',
  download_url = 'https://github.com/dashcorn/dashcorn/downloads',
  keywords = ['tools'],
  classifiers = [],
  python_requires=">=3.9",
  package_dir = {'':'src'},
  packages = setuptools.find_packages('src'),
)
