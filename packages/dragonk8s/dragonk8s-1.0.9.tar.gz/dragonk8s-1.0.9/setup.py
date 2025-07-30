from distutils.core import setup
from setuptools import find_packages

setup(
    name='dragonk8s',
    version='1.0.9',
    description="A k8s implement of Python3",
    author='ma',
    author_email='591867837@qq.com',
    url='https://dragonk8s.com',
    packages=find_packages(),
    install_requires=[
        'cachetools==5.2.0',
        'certifi==2022.9.24',
        'charset-normalizer==2.1.1',
        'google-auth==2.14.1',
        'idna==3.4',
        'kubernetes==25.3.0',
        'oauthlib==3.2.2',
        'pyasn1==0.4.8',
        'pyasn1-modules==0.2.8',
        'python-dateutil==2.8.2',
        'pytz==2022.7',
        'PyYAML==6.0.2',
        'requests==2.28.1',
        'requests-oauthlib==1.3.1',
        'rsa==4.9',
        'six==1.16.0',
        'urllib3==1.26.13',
        'websocket-client==1.4.2',
    ]
)