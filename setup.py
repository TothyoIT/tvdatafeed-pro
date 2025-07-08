from setuptools import setup, find_packages

setup(
    name='tvdatafeed-pro',
    version='0.1.0',
    description='TradingView data fetcher (modified version)',
    author='TothyoIT',
    author_email='kamalhussain193213@outlook.com',
    url='https://github.com/TothyoIT/tvdatafeed-pro',
    packages=find_packages(),
    install_requires=[
        'selenium',
        'pandas',
        'chromedriver-autoinstaller',
        'websocket-client'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.6',
)

