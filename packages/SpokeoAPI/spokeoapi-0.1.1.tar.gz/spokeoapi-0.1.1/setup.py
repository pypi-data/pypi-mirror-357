from setuptools import setup, find_packages

setup(
    name='spokeoAPI',
    version='0.1.1',
    description='official Spokeo API wrapper',
    long_description='Automated OSINT and people search toolkit.',
    author='Wei Zhang',
    author_email='zhangwei.api@protonmail.com',
    url='https://github.com/zhangxinxu',
    project_urls={
        "Source": "https://github.com/zhangxinxu",
        "Documentation": "https://github.com/zhangxinxu"
    },
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=['requests', 'tls_client'],
)
