import setuptools

setuptools.setup(
    name="crawley",
    packages=setuptools.find_packages(),
    entry_points='''
        [console_scripts]
        crawley=crawley:startup
    '''
)
