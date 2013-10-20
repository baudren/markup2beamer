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
        # have different possibilities, so far this one is not very robust,
        # because need another test.
        if lang['md']['section'][1] == 'before':
            sections = re.compile('(%s+)\s(.*)' % (lang['md']['section'][0]))
                #lang['md']['section'][0]))

        # initialize position tracking
        in_slide = False

        for index, line in enumerate(text):
            special_frame = special.match(line)
            section = sections.match(line)

            # catch special frames, that are only one liners
            if special_frame is not None:
                action = special_frame.group(1).lower()
                special_action(tex, action)
                continue

            # catch (sub)sections
            elif section is not None:
                if section.group(2).find(lang['md']['section'][0]) == -1:
                    level = '%ssection' % ''.join(['sub' for i in
                        range(len(section.group(1))-1)])
                    if in_slide:
                        texify_slide(tex, text[first_index:index]) 
                        #slides.append([first_index, index-1])
                        in_slide = False
                    tex.append('\n\%s{%s}\n\n' % (level, section.group(2)))

            # Catch title frame
            elif line.find(lang['md']['frame-title'][0]) != -1:
                # This will be triggered at the first slide, and after sections
                if not in_slide:
                    in_slide = True
                    first_index = index-1
                    continue
                # triggered when reaching the end of a slide
                else:
                    last_index = index-2
                    texify_slide(tex, text[first_index:last_index+1])
                    first_index = index-1
                
            # when reaching the end, wrap up
            if index == len(text)-1:
                texify_slide(tex, text[first_index:index+1])

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

def texify_slide(tex, source):
    print 'deciphering slide'
    title = source[0]
    if source[2] != '':
        subtitle = source[2]
    else:
        subtitle = ''
    # check for a \verb environnement, and if present, add fragile
    fragile = False
    for line in source:
        if line.find('\\verb') != -1:
            fragile = True
            break

    # think about options syntax, like t, b, etc.
    options = ''
    if fragile:
        options += 'fragile'

    if options != '':
        tex.append('\n\\begin{frame}[%s]{%s}{%s}\n' % (options, title, subtitle))
    else:
        tex.append('\n\\begin{frame}{%s}{%s}\n' % (title, subtitle))

    # loop on the slide, have a nested way of deciphering environments.
    index = 3
    while True:
        print 'First search starting at %i' % index
        success, index = extract_environments(source, tex, index)
        print 'Search ended at %i: %s' % (index-1, source[index-1])
        print 'Starting at %i' % index
        if not success:
            break

    tex.append('\n\end{frame}\n')

def extract_environments(source, tex, start_index):

    env = re.compile('%s\s+(.*)' % lang['md']['environments'][0])
    list_env = re.compile('\s*([*+])([-]*)\s+(.*)')

    in_environment = False
    in_list = False

    for index, line in enumerate(source[start_index:]):
        print 'reading %i th line: %s' % (index, line)
        begin_env = env.match(line)
        begin_list = list_env.match(line)
        # enter one environment,
        # Please note that an environment can not appear inside a list...
        if begin_env is not None:
            # if not in one: get name
            if not in_environment:
                print ' /!\ entering env'
                in_environment = True
                options = []
                title = ''
                if len(begin_env.group(1).split(';')) == 1:
                    print '--> no options'
                    name = begin_env.group(1)
                else:
                    print '--> options'
                    name, options = begin_env.group(1).split(';')[0], begin_env.group(1).split(';')[1].split(',')
                if name.find('block') != -1:
                    # One can specify the title of the block with a |
                    print 'found a block'
                    print name.split('|')
                    if len(name.split('|')) > 1:
                        name, title = name.split('|')
                headers = get_surrounding_environment(name, options, title)
                tex.append(headers[0])
            # if in one, recursive call to this function
            else:
                index_nested = start_index+index
                while True:
                    success, index_nested = extract_environments(source, tex,
                            index_nested)
                    if not success:
                        return success, index_nested
        # Entering a list environment.
        elif begin_list is not None:
            if not in_list:
                in_list = True
                # Recover the type of the list
                if begin_list.group(1) == '+':
                    list_type = 'enumerate'
                else:
                    # take the only other possibility.
                    list_type = 'itemize'
                # Recover the potential option to have a reveal
                if begin_list.group(2) == '':
                    tex.append('\\begin{%s}\n' % list_type)
                else:
                    tex.append('\\begin{%s}[<+->]\n' % list_type)
            tex.append('\item %s\n' % begin_list.group(3))
        else:
            # if one finds the ending pattern, return success
            if line.find(lang['md']['environments'][1]) != -1:
                if in_list:
                    tex.append('\end{%s}\n' % list_type)
                    print '/!\ exiting list'
                if in_environment:
                    print '/!\ exiting environment'
                    tex.append(headers[1])
                    return True, start_index + index
            elif line in ['\n', '']:
                if in_list:
                    print 'I discovered an empty line, getting out of itemize'
                    tex.append('\end{%s}\n' % list_type)
            else:
                print 'normal line being written', line
                tex.append(line)
        # getting out
    print 'Am I getting here ?'

    return False, index

# Define all options, like width, this kind of things, and return an array of
# two lines, start and finish
def get_surrounding_environment(name, options, title):
    # take care of blocks
    start_line = ''
    if name.find('block') != -1:
        # if an option with a percentage was passed, include a begin columns
        # before
        option_string = ''
        has_extra_column_env = False
        for option in options:
            if option.find('%') != -1:
                has_extra_column_env = True
                number = float(option.split('%')[0])/100
                start_line += '\\begin{columns}\n\column{%g\\textwidth}\n' % number
            else:
                option_string += option+','

        start_line += '\\begin{%s}{%s}\n' % (name.strip(), title)
        stop_line = '\end{%s}\n' % name.strip()
        if has_extra_column_env:
            stop_line += '\end{columns}\n'
    elif name.find('image') != -1:
        stop_line = ''
    else:
        if name.find('columns') != -1:
            try:
                number = float(options[0].split('%')[0])/100
            except:
                print 'columns expect a percentage argument'
                exit()
            start_line += '\\begin{columns}\n\column{%g\\textwidth}\n' % number
            stop_line = '\end{columns}\n'
        else:
            start_line = '\\begin{%s}[%s]\n' % (name.strip(), ','.join(options))
            stop_line = '\end{%s}\n' % name.strip()
    return [start_line, stop_line]

