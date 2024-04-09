from setuptools import setup

setup(
    name='scrsvr',
    version='0.0',
    license='MIT',
    url = 'https://github.com/GillesArcas/scrsvr',
    author = 'Gilles Arcas',
    author_email = 'gilles.arcas@gmail.com',
    entry_points = {
        'console_scripts': ['scrsvr=scrsvr:scrsvr'],
    },
    zip_safe=False,
    install_requires = [
    ]
)
