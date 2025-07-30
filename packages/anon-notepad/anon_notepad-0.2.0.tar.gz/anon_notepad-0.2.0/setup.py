from setuptools import setup, find_packages

setup(
    name='anon-notepad', # THIS IS YOUR PACKAGE NAME FOR 'pip install'
    version='0.2.0', # Current version of your package
    packages=find_packages(), # Automatically find all packages (like 'noti')
    install_requires=[
        'google-generativeai', # Your package dependencies
    ],
    entry_points={
        'console_scripts': [
            'noti = noti.generator:main', # This creates the 'noti' command. It correctly points to 'noti.generator'
        ],
    },
    author='Prince', # <<< IMPORTANT: Replace with your actual name
    author_email='princecomputerlab0@gmail.com', # <<< IMPORTANT: Replace with your actual email
    description='A Python package to with anon Notepad input on Windows.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/PrinceYadav78/notepad', # <<< IMPORTANT: Replace with your actual public GitHub repo URL (plain URL, no Markdown)
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent', # Works on any OS
        'Operating System :: Microsoft :: Windows', # Specific feature for Windows
    ],
    python_requires='>=3.7', # Minimum Python version required
)