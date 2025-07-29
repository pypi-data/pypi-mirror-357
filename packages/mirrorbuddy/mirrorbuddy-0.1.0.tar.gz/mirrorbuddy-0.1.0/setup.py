from setuptools import setup, find_packages

setup(
    name='mirrorbuddy',                      
    version='0.1.0',                        
    author='GM',
    author_email='rox639@gmail.com',
    description='A cool and fun library to clone your body in realtime and it can also detect handshake between you and your clone using Mediapipe',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/yourlibname',  
    packages=find_packages(),                
    install_requires=[
        'opencv-python',
        'mediapipe',
        'pyttsx3'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License', 
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
