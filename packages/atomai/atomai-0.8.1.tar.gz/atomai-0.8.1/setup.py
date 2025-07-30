__author__ = "Maxim Ziatdinov"
__copyright__ = "Copyright Maxim Ziatdinov (2020)"
__maintainer__ = "Maxim Ziatdinov"
__email__ = "maxim.ziatdinov@ai4microcopy.com"

from setuptools import setup, find_packages
import os

module_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(module_dir, 'atomai/__version__.py')) as f:
    __version__ = f.read().split("'")[1]

if __name__ == "__main__":
    setup(
        name='atomai',
        python_requires='>=3.8',
        version=__version__,
        description='Deep and machine learning for atom-resolved data',
        long_description=open(os.path.join(module_dir, 'README.md')).read(),
        long_description_content_type='text/markdown',
        url='https://github.com/pycroscopy/atomai/',
        author='Maxim Ziatdinov',
        author_email='maxim.ziatdinov@ai4microcopy.com',
        license='MIT license',
        packages=find_packages(),
        zip_safe=False,
        install_requires=[
            'torch>=1.0.0',
            'numpy>=1.18.5',
            'matplotlib>=3.4',
            'scipy>=1.3.0',
            'scikit-learn>=0.22.1',
            'scikit-image>=0.16.2',
            'opencv-python>=4.1.0',
            'networkx>=2.5',
            'mendeleev<=0.6.1',
            'torchvision>=0.13.0',
            'progressbar2>=3.38.0',
            'gpytorch>=1.9.1',
            'pandas>=1.1.5'
        ],
        classifiers=['Programming Language :: Python',
                     'Development Status :: 3 - Alpha',
                     'Intended Audience :: Science/Research',
                     'Operating System :: OS Independent',
                     'Topic :: Scientific/Engineering']
    )
