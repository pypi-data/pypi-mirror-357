from distutils.core import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
  name = 'youtube-zik',         # How you named your package folder (MyLib)
  long_description=long_description,
  long_description_content_type='text/markdown',
  include_package_data=True,
  packages = ['youtube-zik'],   # Chose the same as "name"
  version = '2.5.0',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'YT DDL GUI based on pytubefix',   # Give a short description about your library
  author = 'François Garbez',                   # Type in your name
  author_email = 'fawn06220@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/Fawn06220/Youtube-Zik',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/Fawn06220/Youtube-Zik/archive/refs/tags/v2.3.1.tar.gz',    # I explain this later on
  keywords = ['python', 'youtube', 'gui'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'wxpython',
          'moviepy',
          'pytubefix',
      ],
  classifiers=[
    'Development Status :: 5 - Production/Stable',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.12',
    'Programming Language :: Python :: 3.13'
  ],
)
