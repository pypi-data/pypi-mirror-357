from setuptools import setup, find_packages

setup(
    name="qurancorpus-ziya",  # Benzersiz yeni isim
    version="0.1",
    description="Arabic Quranic Corpus Python API",
    long_description="A Python API for the Quranic Arabic Corpus project.",
    author="Assem Chelli",
    author_email="assem.ch@gmail.com",
    license="GPL",
    platforms=["any"],
    packages=find_packages(),
    install_requires=[
        "pyparsing"
    ],
    include_package_data=True,
    package_data={
        "qurancorpus": ["data/quranic-corpus-morpology.xml"]
    },
    zip_safe=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: Arabic",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="quran arabic corpus quranic",
)
    