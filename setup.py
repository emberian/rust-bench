from distutils.core import setup

setup(
    name='rust-bench',
    version='0.1.0',
    author='Corey Richardson',
    author_email='corey@octayn.net',
    py_modules=['benchlib'],
    scripts=['rust-bench.py', 'mem-bench.py'],
    url='http://github.com/cmr/rust-bench',
    license='MIT',
    description='simple rust benchmarking runner using cgroups',
    long_description=open('README.txt').read(),
    install_requires=["plumbum"],
)
