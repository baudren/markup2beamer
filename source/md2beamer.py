# markdown to beamer converter
# for quick and powerful presentation making, with a lot of customisation
# possible
# Written by Benjamin Audren
# 08/10/2013

import parser_md2b
import file_process as fp
import language

import os

def md2beamer():
    """
    Main call of the function

    """
    # Parsing line argument
    command_line = parser_md2b.parse()

    # Recovering the format of the input file
    extension = command_line.input.split(os.path.sep)[-1].split('.')[-1]

    # Read all possibles extension in language file
    supported_extensions = language.language_definition.keys()

    if extension not in supported_extensions:
        print 'Your input file has a', extension, 'format, currently unsupported'
        print 'Develop your own format, or use one of the following'
        for ext in supported_extensions:
            print ext,
        print '\nExiting now'
        return
    
    # Text treatment from md to latex
    tex_file, success = fp.md_to_tex(command_line)

    if not success:
        print('Tried to texify your markup and failed... Please check your source')
        return success

    # Apply pdflatex enough times and check for issues (open a window with the
    # tex file if needed)
    success = fp.tex_to_pdf(tex_file, command_line.pdf)

    if not success:
        print('Tried to pdfify your tex and failed... Please check your source')

    return success

    
if (__name__ == '__main__'):
    md2beamer()
