from distutils.core import setup

# Recover version from VERSION file
with open('VERSION', 'r') as version_file:
    VERSION = version_file.readline()

setup(name='Markup2Beamer',
      version=VERSION,
      description='Markup to Beamer presentation',
      author='Benjamin Audren',
      author_email='benj_audren@yahoo.fr',
      package_dir={'': 'source'},
      scripts=['source/markup2beamer'],
      packages=[''],
      )
