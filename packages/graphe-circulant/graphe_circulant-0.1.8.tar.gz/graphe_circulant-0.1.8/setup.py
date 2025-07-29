from setuptools import setup, find_packages

setup(
    name='graphe_circulant',
    version = '0.1.8',
    author='lakrakar_labibi',
    author_email='lakrakarouafaa@email.com',
    description='Package pour le calcul de diamètres de graphes circulants',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'matplotlib',
        'numpy',
        'customtkinter'
    ],
    entry_points={
        'console_scripts': [
            'graphe_circulant = graphe_circulant.interface:lancer_interface',
        ]
    },

    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.7',
)
