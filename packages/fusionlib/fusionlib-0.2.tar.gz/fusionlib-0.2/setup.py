from setuptools import setup, find_packages

setup(
    name='fusionlib',
    version='0.2',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'matplotlib',
        'seaborn',
        'scipy',
        'scikit-learn',
        'textblob',
        'nltk',
        'requests',
        'beautifulsoup4',
        'pillow'
    ],
    description='FusionLib: One import for all common Python libraries',
    author='Your Name',
    author_email='youremail@example.com',
    keywords=['numpy', 'pandas', 'matplotlib', 'textblob', 'utility', 'seaborn', 'scikit-learn', 'nltk', 'requests'],
)
