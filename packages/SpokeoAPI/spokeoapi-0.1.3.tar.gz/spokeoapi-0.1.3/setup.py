from setuptools import setup, find_packages

setup(
    name='SpokeoAPI',
    version='0.1.3',  
    description='official API wrapper for Spokeo lookup service',
    long_description=open('readme.md').read(),
    long_description_content_type='text/markdown',
    author='Wei Zhang',
    author_email='zhangwei.api@protonmail.com',
    url='https://github.com/zhangxinxu',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        
        'SpokeoAPI': [
            'pyarmor_runtime_000000/*',
        ],
    },
    install_requires=[
        'requests',
        'tls_client'
    ],
    python_requires='>=3.6',
)
