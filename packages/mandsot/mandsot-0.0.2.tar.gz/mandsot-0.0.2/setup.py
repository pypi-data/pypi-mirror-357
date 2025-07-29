from setuptools import setup, find_packages


def readfile(filename):
    with open(filename, 'r+') as f:
        return f.read()


setup(
    name="mandsot",
    version="0.0.2",
    description="CNN network for speech onset time (SOT) detection of Mandarin speech",
    long_description=readfile('README.md'),
    long_description_content_type='text/markdown',
    author="Tai Yuan",
    author_email="tai.yuan@stonybrook.edu",
    url="https://github.com/RyanYuanSun/MandSOT-CNN",
    py_modules=['mandsot'],
    python_requires='>3',
    packages=find_packages(),
    license=readfile('LICENSE'),
    install_requires=[
          'torch',
          'numpy',
          'pandas',
          'librosa',
          'noisereduce',
          'matplotlib',
          'scikit-learn',
          'tqdm',
          'praat-parselmouth',
      ],
    entry_points={
        'console_scripts': ['mandsot=mandsot.cli:main']
        },
    include_package_data=True,
    package_data={'': ['pretrained/*.pth']},
)
