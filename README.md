=============
markup2beamer
=============

A pain-free experience of writing beautiful, fast and readable slides.


Design Requirements
-------------------

- the text file must be **readable**, which implies
  * support for indentation
  * support for fancy addition that should not perturb the code
- Via a simple command, one should be able to change the style of the
  presentation (leaving the style Tex file outside of the beamer
  presentation).
- All non supported commands should be interpreted directly by LaTeX.
- Readability differs from one person to the other, so the code should
  support different languages, that must be specified in a separate
  file.
- The preprocessing should be as fast as possible, and should be able
  to work as a script to update the .tex every time the input file is
  changed.


Installation
------------

If you have the setup tools installed, simply run

    $ python setup.py install --user

Otherwise, you can add the alias markup2beamer to your rc file,
calling:

    $ python source/markup2beamer


Usage
-----

See the example folders for the basic syntax. The language is defined
in the file `source/language.py`. To use the script, simply call

    $ python source/markup2beamer example/simple.md


Current Limitations (see Roadmap)
---------------------------------

The interactive mode is not very general, and only runs on Mac, for
Skim viewer. 

Inspiration
------------

The basic inspiration for this project was taken from rst2beamer
(<https://github.com/rst2beamer/rst2beamer>), as well as some tips for
the regular expression handling.
