from setuptools import setup, find_packages

setup(
    name='todos-cmd',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'click>=8.0',
        'colorama>=0.4',
    ],
    entry_points={
        'console_scripts': [
            'todo=todo_cli.cli:main',
        ],
    },
    license='MIT',
    author='Rajat Nayak',
    description='A powerful CLI Todo App with search, tagging, priority, and due date support',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/rajat-gith/todo-cli',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Environment :: Console',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
