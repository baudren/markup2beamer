=============
markup2beamer
=============

A pain-free experience of writing beautiful, fast and readable slides.


Design Requirements
-------------------

- the text file must be **readable**, which implies
  * support for indentation
  * support for fancy addition that should not perturb the code
- Readability differs from one person to the other, so the code should
  support different languages, that must be specified in a separate
  file.
- The preprocessing should be as fast as possible, and work as a
  script to update the .tex every time the input file is changed.


Installation
------------

If you have the setup tools installed, simply run

    $ python setup.py install --user

Otherwise, you can add the alias markup2beamer to your rc file,
calling:

    $ python source/markup2beamer

Usage
-----

