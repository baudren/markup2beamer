# markdown to beamer converter
# for quick and powerful presentation making, with a lot of customisation
# possible
# Written by Benjamin Audren
# 08/10/2013

import parser_md2b
import file_process as fp

def md2beamer():
    """
    Main call of the function

    """
    # Parsing line argument
    command_line = parser_md2b.parse()

    # Text treatment from md to latex
    tex_file, success = fp.md_to_tex(command_line.input)

    if not success:
        print('Tried, failed... Please check your .md')
        return success

    # Apply pdflatex enough times and check for issues (open a window with the
    # tex file if needed)
    success = fp.tex_to_pdf(tex_file, command_line.pdf)

    if not success:
        print('Tried, failed... Please check your .md')

    return success

    
if __name__ == '__main__':
    md2beamer()
