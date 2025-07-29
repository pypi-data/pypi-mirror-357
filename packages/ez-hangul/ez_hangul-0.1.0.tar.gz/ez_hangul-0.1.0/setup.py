from setuptools import setup, find_packages

setup(
    name='ez-hangul',
    version='0.1.0',
    description='쉽고 강력한 한글 자모 결합 조합 처리, 조사 자동화, 순우리말 변환 유틸리티',
    author='Jinyoon',
    author_email='jinyoonbz@gmail.com',
    packages=find_packages(),
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Text Processing :: Linguistic',
        'Natural Language :: Korean',
    ],
)
