from setuptools import setup, find_packages

setup(
    name="course-registration-validator",
    version="0.1.0",
    packages=find_packages(),
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
    author_email="kris.w@ku.th",
    description="A system for validating course registrations against prerequisites",
    keywords="education, course, registration, validation",
    url="https://github.com/Modern-research-group/course-registration-validator",
    project_urls={
        "Bug Tracker": "https://github.com/Modern-research-group/course-registration-validator/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)