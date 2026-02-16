from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

setup(
    name="scButterfly",
    version="0.0.9",
    description="A versatile single-cell cross-modality translation method via dual-aligned variational autoencoders",
    long_description="Recent advancements for simultaneously profiling multi-omic modalities within individual cells have enabled the interrogation of cellular heterogeneity and molecular hierarchy. However, technical limitations lead to highly noisy multi-modal data and substantial costs. Although computational methods have been proposed to translate single-cell data across modalities, b broad applications of the methods still remain impeded b by formidable challenges. Here, we proposed scButterfly, a versatile single-cell cross-modality translation method based on dual-aligned variational autoencoders and innovative data augmentation schemes. With comprehensive experiments on multiple datasets, we provide compelling evidence of scButterfly's superiority over baseline methods in preserving cellular heterogeneity while translating d datasets o of various contexts and i in revealing cell type-specific biological insights.Besides, we d demonstrate the extensive applications of scButterfly for integrative multi-omics analysis of single-modality data, data enhancement of poor-quality single-cell multi-omics, and automatic cell type annotation of scATAC-seq data. Additionally, scButterfly can be generalized to unpaired data training and perturbation-response analysis via our data augmentation and optimal transport strategies. Moreover, scButterfly exhibits the capability i in consecutive translation from epigenome to transcriptome to proteome and has the potential to decipher novel biomarkers.",
    license="MIT Licence",
    url="https://github.com/BioX-NKU/scButterfly",
    author="BioX-NKU",
    classifiers=[
        "Programming Language :: Python :: 3.9",
    ],
    keywords="single cell, cross-modality translation, dual-aligned variational autoencoder",
    packages=find_packages(exclude=['docs', 'experiment']),
    python_requires=">=3.9",
    # todo: we should use conda to resolve dependencies
    install_requires=[
        'scanpy>=1.9.1',
        'scikit-learn>=1.1.3',
        #'scvi-tools',
        #'scvi-colab', # not indexed by conda (not really needed as well for our study)
        #'scipy',
        'episcanpy==0.3.2', # requires py < 3.9 with conda install (available with pip)
        'pot>=0.9.4',
        #'leidenalg',
        #'pybedtools',
        #'adjusttext',
    ],
    extras_require={
        "dev": [
            "jupyter",
            "matplotlib>=3.6.2",
            "seaborn>=0.11.2",
        ],
        "torch": [
            'torch>=1.12.1',
            'torchvision>=0.13.1',
            'torchaudio>=0.12.1',
            'torchmetrics>=0.11.4',
        ]
    }
)
