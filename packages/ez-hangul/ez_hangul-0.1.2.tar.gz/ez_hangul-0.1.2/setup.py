from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='ez-hangul',
    version='0.1.2',
    description='한글 자모 분리, 조합, 조사 자동 처리 유틸리티',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Jinyoon',
    author_email='jinyoonbz@gmail.com',
    url='https://github.com/newhajinyoon/ez-hangul',  # 선택 사항
    packages=find_packages(),
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Text Processing :: Linguistic',
        'Natural Language :: Korean',
    ],
)
