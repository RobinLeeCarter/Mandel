# Mandel
Open-source Mandelbrot Explorer using Python, Qt, Cuda and threading.\
Designed as a project to improve my general Python skills, so any comment or feedback is very welcome.

**Current requirements:**
- A fairly recent Nvidia graphics card (for Cuda)
- Linux (tested on Ubuntu 19.10)
- Conda

I intend to try to get it to run on Window 10 in the near future also. I have not tried it yet.

See build_script.md for how to build the Conda environment from environment.yml if unfamiliar.
Or if having problems you could try using environment-exact-YYYY-MM-DD.yml instead to use the same versions I had for testing master.\
**Warning: The environment was about 3Gb on my machine.**\
You can use an existing environment too of course if it meets all the requirements.

Once built, open a terminal in the code directory, then:
1) conda activate mandel (or whatever you called the environment)
2) python mandel.py
<br />
<br />

Icons in menus etc... are:\
Fugue Icons (unmodified) (C) 2013 Yusuke Kamiyamane. All rights reserved.\
<http://p.yusukekamiyamane.com/>\
These icons are licensed under a Creative Commons Attribution 3.0 License.\
<http://creativecommons.org/licenses/by/3.0/>

