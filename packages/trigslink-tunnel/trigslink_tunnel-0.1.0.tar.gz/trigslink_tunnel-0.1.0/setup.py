from setuptools import setup, find_packages

setup(
    name='trigslink-tunnel',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'trigslink-tunnel=trigslink.tunnel:tunnel',
        ],
    },
    author='Aakash',
    description='A CLI to create cloudflare tunnels for Trigslink MCP services',
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    keywords='trigslink cli tunnel cloudflare web3',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.7',
)