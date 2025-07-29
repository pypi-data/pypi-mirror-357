from setuptools import setup, find_packages

setup(
    name='Mahesh-BPE',
    version='0.1.0',
    description='Custom BPE function for Mahesh',
    long_description='Mahesh Code Assistant for developers and students and enthusiastic individuals who want to explore AI.',
    long_description_content_type='text/markdown',
    author='Durja LLC, Manoj Nayak',
    author_email='llcdurja.ai@gmail.com',
    maintainer='Manoj Nayak',
    maintainer_email='manojvnayak@outlook.in',
    license='MIT',
    packages=find_packages(),  # No need for `where="src"`
    install_requires=['numpy'],
    python_requires='>=3.7',
)
