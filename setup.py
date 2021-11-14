from setuptools import setup

entry_points={
    'console_scripts': [
        'hassembler = hassembler.hassembler:main',
        'vmt = hassembler.vmtranslator:main',
    ]
}

setup(name='hassembler', package_dir = {'': 'src'}, entry_points = entry_points)
