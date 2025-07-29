from setuptools import setup, find_packages

# Safely read the README file with UTF-8 encoding to avoid Unicode errors
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='causal-drift',
    version='0.1.0',
    author='Kazi Sakib Hasan',
    author_email='simanto.alt@gmail.com',
    description='A causal feature selection (Causal DRIFT: Causal Dimensionality Reduction via Inference of Feature Treatments) library using residual-based ATE estimation.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/SakibHasanSimanto/deepCausal',  # Replace 'yourusername' once uploaded
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'scikit-learn'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)

