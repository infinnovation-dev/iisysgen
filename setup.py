from setuptools import setup
setup(name='iisysgen',
      version='0.2',
      description="Tools for generating GNU/Linux system images",
      author="Colin Hogben",
      author_email="colin@infinnovation.co.uk",
      project_urls={
          "Source Code": "https://github.com/infinnovation-dev/iisysgen.git",
      },
      license='MIT',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Topic :: System :: Installation/Setup',
          'Operating System :: POSIX :: Linux'
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
      ],
      packages=['iisysgen'],
      entry_points={
          'console_scripts': [
              'iisysgen = iisysgen.cmd:main',
          ],
      },
)
