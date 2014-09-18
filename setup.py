from distutils.core import setup

setup(
    name='rust-bench',
    version='0.3.0',
    author='Corey Richardson',
    author_email='corey@octayn.net',
    scripts=['benchit.py'],
    url='http://github.com/cmr/rust-bench',
    license='MIT',
    description='simple rust benchmarking runner using cgroups',
    long_description=open('README.txt').read(),
    install_requires=["plumbum"],
)
