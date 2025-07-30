from setuptools import setup, find_packages

setup(
    name="student_portal_models",
    version="0.1.0",
    packages=find_packages(exclude=["tests*", "docs*"]),
    install_requires=[
        "alembic==1.16.2",
        "asyncpg==0.30.0",
        "SQLAlchemy==2.0.41",
        "pydantic==2.11.7",
        "pydantic-settings==2.9.1",
        "python-dotenv==1.1.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    include_package_data=True,
)
