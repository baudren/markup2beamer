from collections import OrderedDict as od
from language import language_definition as lang
from copy import deepcopy
import re

def md_to_tex(command_line, **kwargs):

    # create references to some command_line variables for convenience.
    md_file = command_line.input
    verbose = command_line.verbose

    # Create a temporary tex file
    tex_file = md_file.replace('.md', '.tex')
    source = []

    # Define the sequence of different parts in the text file
    parts = ['headers', 'title', 'body']

    # Create a dictionnary that will store as a string the lines it started
    # from in the md file, and the resulting process written on the tex.
    transformator = od()
    
    # Recover entire file
    with open(md_file, 'r') as md:
        for index, line in enumerate(md):
            source.append(line.strip('\n').strip())

    # Recover sequentially the different parts.
    current_line = 0

    # Recover the header, and title. The catch function is where the language
    # is processed.
    for name in parts:
        transformator[name], current_line = catch(
            source, current_line, name, verbose)
    """
    .. warning::

            Note that the order: headers, title, body must be respected

    """

    # Transcribe the header into a tex file
    tex = od()

    for name in ['headers', 'body']:
        tex[name] = texify(source, name, transformator, verbose)

    with open(tex_file, 'w') as tex_writer:
        for key, value in tex.iteritems():
            for line in value:
                print line.rstrip('\n')
                tex_writer.write(line)

    return 'toto', False

def tex_to_pdf(tex_file, pdf_file, verbose):

    return False

def texify(source, context, transformator, verbose):

    start_index = transformator[context][0]
    stop_index = transformator[context][1]

    title = source[transformator['title'][0]+1]

    text = deepcopy(source[start_index:stop_index])
    if verbose:
        print 'Trying to texify the following',text
        print 'in the context of', context

    tex = []

    if context == 'headers':
        # must extract syntax and transform into latex commands
        for line in text:
            if len(line) != 0:
                try:
                    action, arguments = line.split(':')
                    # on the first line, either an input or document class
                    if len(tex) == 0:
                        if action != 'input':
                            tex.append('\documentclass[xcolor=dvipsnames]{beamer}\n')
                    # Strip out spaces from both sides
                    arguments = arguments.strip()
                    for argument in arguments.split(','):
                        argument = argument.strip()
                        if argument.find('[') != -1:
                            # the argument contains extra information
                            m = re.compile('\[.*\]')
                            temp = m.match(argument)
                            option = temp.group()[1:-1]
                            main = argument[temp.end():].strip()
                            if action == 'title':
                                main = title
                            tex.append('\%s[%s]{%s}\n' % (action, option, main))
                        else:
                            tex.append(
                                '\%s{%s}\n' % (action, argument))
                except:
                    pass


    elif context == 'body':
        tex.append('\n\\begin{document}\n')
        special = re.compile('%s\s+(.*)\s+%s' % (
            lang['md']['special-frames'][0], lang['md']['special-frames'][1]))
        for line in text:
            # catch special frames, 
            temp = special.match(line)
            if temp is not None:
                action = temp.group(1).lower()
                special_action(tex, action)
                
        tex.append('\n\end{document}\n')


    return tex

# define helper function
def catch(source, start_index, context, verbose):
    """
    Recover element surrounded by given start and stop strings

    Also set the flags to the next in line

    Returns
    -------
    output:
        array of two index recovering the desired information
    new_index:
        current position after extraction

    """

    # Recover start and stop strings definition from the language file
    start_string, stop_string = lang['md'][context]

    # If the end is nothing, goble the rest of the file
    if stop_string == '':
        return [start_index, len(source)+1], len(source)+1

    # else, do a catch between the start and stop
    # Recover the exact first line
    first_temp = [elem for elem in source[start_index:] if
            elem.find(start_string) != -1]
    try:
        first_index = source[start_index:].index(first_temp[0])+start_index
    except IndexError:
        # this means no start_string was found
        return [None, None], start_index

    # Recover the exact last line
    second_temp = [elem for elem in source[first_index+1:] if
            elem.find(stop_string) != -1]
    try:
        second_index = source[first_index+1:].index(second_temp[0])+first_index+1
    except IndexError:
        # this means the finishing line was not found
        return [first_index, None], first_index+1

    return [first_index, second_index+1], second_index+1

def special_action(tex, action):
    

    tex.append('\\begin{frame}\n')
    if action == 'title':
        tex.append('\\titlepage\n')
    elif action == 'outline':
        tex.append('\\frametitle{Outline}\n')
        tex.append('\\tableofcontents\n')
    else:
        print 'warning, %s not understood', action
    tex.append('\end{frame}\n')
