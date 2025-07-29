# setup.py
from setuptools import setup, find_packages

setup(
    name='bailing-text-analysis-plugin',
    version='0.2.0',
    description='百炼文本分析插件',
    author='xindy',
    author_email='qixiong168@163.com',
    packages=find_packages(),
    install_requires=[
        'nltk==3.8.1',
        # 其他依赖
    ],
    entry_points={
        'bailing.plugins': [
            'text_analysis = my_plugin:create_plugin',
        ],
    },
)