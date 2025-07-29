from setuptools import setup, find_packages

setup(
    name='sb_tencent_mmkv',
    version='0.1.3',
    author='Zhangxiaolong',
    author_email='lxc.rudy@gamil.com',
    description='Cross-platform MMKV Python binding',
    long_description=open("README.md", encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),  # 自动查找所有模块
    include_package_data=True, # 包括 MANIFEST 中的所有文件
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # 依赖的最低 Python 版本
)
