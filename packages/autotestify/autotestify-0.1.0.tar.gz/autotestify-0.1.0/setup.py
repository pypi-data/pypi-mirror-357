from setuptools import setup

setup(
    name='autotestify',
    version='0.1.0',
    description='Auto-generate pytest tests for Python functions with @autotest decorator',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Sardor Safarov',
    author_email='sardor.safarov200320@gmail.com',  # Optional
    url='https://github.com/SafarovSardorDev/autotestify',  # Optional
    packages=['autotestify'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'autotestify=autotestify.cli:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
