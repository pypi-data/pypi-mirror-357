from setuptools import setup, find_packages

with open("readme.md", "r") as fh:
    long_description = fh.read()

setup(
    name='selfshadingcorrection',
    version='1.0.2',
    author='Yulun Wu',
    author_email='yulunwu8@gmail.com',
    description='Applies self-shading correction to water-leaving reflectance measurements collected through the skylight-blocked approach',
    long_description=long_description,      # Long description read from the the readme file
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3'
    ],
    python_requires='>=3.8',
    install_requires=['pandas','numpy','scipy']
)




