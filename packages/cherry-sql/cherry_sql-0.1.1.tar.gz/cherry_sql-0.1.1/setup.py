from setuptools import setup, find_packages

setup(
    name='cherry-sql',
    version='0.1.1',
    description='Библиотека для работы с SQL и вспомогательными файлами',
    author='shareofpie',
    author_email='your@email.com',
    url='https://pypi.org/project/cherry-sql/',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'CherrySQL': ['*.ico', '*.png', '*.sql', '*.xlsx'],
    },
    install_requires=[],
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
)
