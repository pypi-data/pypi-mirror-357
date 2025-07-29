from setuptools import setup,find_packages

from pathlib import Path
this_directory = Path(__file__).parent
long_description = Path("README.md").read_text(encoding="utf-8").replace("<pre>", "# Maudio - Minimal Morse code audio encoder\n").split("</pre>")[-1].lstrip()

giturl="https://github.com/Mohd-Sinan/maudio"

setup(
      name='maudio',
      version='0.0.2',
      author='Mohammed Sinan KH',
      maintainer='Mohammed Sinan KH',
      author_email='devsinankh123@gmail.com',
      license='MIT',
      description='Minimal Morse code audio encoder ( WAV format )',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url=giturl,
      packages=[ 'maudio' ,],

      classifiers=[
      'Development Status :: 3 - Alpha',
      'License :: OSI Approved :: MIT License',
      'Intended Audience :: Developers',
      'Topic :: Multimedia :: Sound/Audio',
      'Programming Language :: Python :: 3.2',
      'Programming Language :: Python :: 3.6',
      'Programming Language :: Python :: 3.7',
      'Programming Language :: Python :: 3.8',
      'Programming Language :: Python :: 3.9',
      ],
      keywords='morse code audio generation',
      python_requires='>=3.6',

      entry_points={
        'console_scripts': [
        'maudio=maudio.__main__:main',
          ],
      },
      project_urls={
        'Source': giturl,
        'Tracker': giturl +'/issues',
      },
)
