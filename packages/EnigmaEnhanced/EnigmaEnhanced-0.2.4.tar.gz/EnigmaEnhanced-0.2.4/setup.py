from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='EnigmaEnhanced',
    version='0.2.4',
    author='PaulLiszt',
    author_email='paullizst@gmail.com',
    description='A stateless enhanced Enigma cipher machine with full CLI support',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/PaulLiszt/EnigmaEnhanced',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'enigmaenhanced = enigma_enhanced.engine:cli'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Education',
        'Intended Audience :: Developers',
        'Topic :: Security :: Cryptography',
        'Topic :: Education'
    ],
    python_requires='>=3.6',
    license='MIT',
    keywords='enigma cipher cryptography security education',
    project_urls={
        'Source': 'https://github.com/PaulLiszt/EnigmaEnhanced',
        'Bug Reports': 'https://github.com/PaulLiszt/EnigmaEnhanced/issues',
        'Documentation': 'https://github.com/PaulLiszt/EnigmaEnhanced/blob/main/README.md'
    },
    include_package_data=True,
)