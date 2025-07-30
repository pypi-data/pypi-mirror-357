from setuptools import setup, find_packages

setup(
    name="szdx-ln-jupyter-extra",  # 与 pyproject.toml 保持一致
    version="0.1.41",              # 与 pyproject.toml 保持一致
    description="JupyterLab extension: ln-jupyter-extra",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="hewenbin",
    author_email="hewenbin@ln-jupyter.com",
    url="https://github.com/Mandy-Cheng/ln-notebook.git",
    license="BSD-3-Clause",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "ln_jupyter_extra": [
            "labextension/**",
        ]
    },
    install_requires=[
        "jupyterlab>=4.0.0,<5"
        # 其他依赖
    ],
    python_requires=">=3.8",
    classifiers=[
        "Framework :: Jupyter",
        "Framework :: Jupyter :: JupyterLab",
        "Framework :: Jupyter :: JupyterLab :: 4",
        "Framework :: Jupyter :: JupyterLab :: Extensions",
        "Framework :: Jupyter :: JupyterLab :: Extensions :: Prebuilt",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    entry_points={
        "jupyterlab.extension": [
            "ln-jupyter-extra = ln_jupyter_extra"
        ]
    },
    zip_safe=False,
)
