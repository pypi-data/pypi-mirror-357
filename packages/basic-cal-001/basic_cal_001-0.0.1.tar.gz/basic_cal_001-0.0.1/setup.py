from setuptools import setup, find_packages

setup(
    name='basic_cal_001',
    version='0.0.1',
    description='A very basic calculator for simple arithmetic operations',
    author='nandhu',
    author_email='ggnandhinigg@gmail.com',
    packages=find_packages(),
    install_requires=[],  # Add dependencies here if needed
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Education',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.7',
)
