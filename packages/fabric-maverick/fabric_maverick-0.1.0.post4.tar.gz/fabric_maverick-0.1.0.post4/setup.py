from setuptools import setup, find_packages

setup(
    name='fabric_maverick',
    version='0.1.0.post4',
    description='A Fabric Package for Semantic/Dataset validation',
    author='Nisarg Patel',
    author_email='nisargp@maqsoftware.com',
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",

        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        "Framework :: Jupyter"
    ],
    python_requires=">=3.10,<3.12"
)

# python3 setup.py sdist
# python3 -m build 
# python3 -m  twine upload dist/* 

#“major.minor” versioning with developmental releases, release candidates and post-releases for minor corrections:

# 0.1.0.dev1
# 0.1.0.dev2
# 0.1.0.dev3
# 0.1.0.dev4
# 0.1.0
# 0.1.0.post1 <- for minor corrections
# 0.1.1.dev1
# 0.1.1.dev2
# 0.1.1