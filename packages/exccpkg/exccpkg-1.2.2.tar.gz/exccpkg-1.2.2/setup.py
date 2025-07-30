from setuptools import setup

setup(
    name = 'exccpkg',
    version = '1.2.2',
    # shutil.rmtree onexc https://docs.python.org/3/library/shutil.html#shutil.rmtree
    python_requires='>=3.12',
    description = 'An explicit C++ package builder.',
    author = 'AdjWang',
    author_email = 'wwang230513@gmail.com',
    packages = ['exccpkg'],
    install_requires = ['requests'],
)
