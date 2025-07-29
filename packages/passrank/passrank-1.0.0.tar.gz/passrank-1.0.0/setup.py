from setuptools import setup, find_packages

setup(
    name='passrank',  # Your package name (must be unique on PyPI)
    version='1.0.0',  # Start with 1.0.0
    author='Aditya Anand',
    author_email='your.email@example.com',  # Optional, but recommended
    description='AI-inspired password strength scoring system',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/passrank',  # Optional, or use your GitHub
    packages=find_packages(),  # Automatically includes all folders with __init__.py
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    license='MIT',
    python_requires='>=3.6',
)
