from setuptools import setup, find_packages
import os

# Get a list of all top-level Python files
py_files = [f[:-3] for f in os.listdir('.') if f.endswith('.py')]

setup(
    name="course-registration-validator",
    version="0.1.0",
    py_modules=py_files,  # Include all top-level Python files
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "PyPDF2>=2.0.0",
    ],
    entry_points={
        'console_scripts': [
            'course-validator=integrated_solution:main',
        ],
    },
    python_requires='>=3.8',
    author="Modern Research Group",
    description="A system for validating course registrations against prerequisites",
    url="https://github.com/Modern-research-group/course-registration-validator",
)
