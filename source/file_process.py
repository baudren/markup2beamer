from collections import OrderedDict as od
from language import language_definition as lang
from copy import deepcopy
import re
import os
import subprocess as sp

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
            source.append(line.strip('\n').rstrip())

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
                if verbose:
                    print line.rstrip('\n')
                tex_writer.write(line)

    return tex_file, True

def tex_to_pdf(tex_file, verbose):

    # Simply run twice pdflatex 
    os.chdir(os.path.sep.join(tex_file.split(os.path.sep)[:-1]))
    
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
                # if there was no :, it means it is a special command
                except:
                    if line.find('outline-at-sections') != -1:
                        tex.append('\AtBeginSection[]\n{\\begin{frame}<beamer>\n')
                        tex.append('\\frametitle{Outline}\n\\tableofcontents[\n')
                        tex.append('currentsection,sectionstyle=show/shaded,')
                        tex.append('subsectionstyle=show/show/hide]\n\end{frame}}\n')
                    elif line.find('no-navigation-symbols') != -1:
                        tex.append('\setbeamertemplate{navigation symbols}{}\n')
                    else:
                        pass


    elif context == 'body':
        tex.append('\n\\begin{document}\n')

        # Search for special frames
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
                # first, exit current slide if any
                if in_slide:
                    texify_slide(tex, text[first_index:index], verbose)
                    in_slide = False
                action = special_frame.group(1).lower()
                special_action(tex, action, verbose)
                continue

            # catch (sub)sections
            elif section is not None:
                if section.group(2).find(lang['md']['section'][0]) == -1:
                    level = '%ssection' % ''.join(['sub' for i in
                        range(len(section.group(1))-1)])
                    if in_slide:
                        texify_slide(tex, text[first_index:index], verbose) 
                        in_slide = False
                    tex.append('\n\%s{%s}\n\n' % (level, section.group(2)))

            # Catch title frame
            elif line.find(lang['md']['frame-title'][0]) != -1:
                # Recover potential options at the end of the line, like
                # ------- fragile, t
                # This will be triggered at the first slide, and after sections
                if not in_slide:
                    in_slide = True
                    first_index = index-1
                    continue
                # triggered when reaching the end of a slide
                else:
                    last_index = index-2
                    texify_slide(tex, text[first_index:last_index+1], verbose)
                    first_index = index-1
                
            # when reaching the end, wrap up
            if index == len(text)-1:
                texify_slide(tex, text[first_index:index+1], verbose)

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

def special_action(tex, action, verbose):
    
    tex.append('\\begin{frame}\n')
    if action == 'title':
        tex.append('\\titlepage\n')
    elif action.find('outline') != -1:
        # check if option is specified with pipe
        tex.append('\\frametitle{Outline}\n')
        if len(action.split('|')) == 1:
            tex.append('\\tableofcontents\n')
        else:
            action, complement = action.split('|')
            tex.append('\\tableofcontents[%s]\n' % complement)
    else:
        print 'warning, %s not understood', action
    tex.append('\end{frame}\n')

def texify_slide(tex, source, verbose):
    # recover possible slide options
    if len(source[0].split('|')) > 1:
        title, options = [elem.strip() for elem in source[0].split('|')]
    else:
        title, options = source[0], ''
    if title == 'None':
        title = ''
    if source[2] != '':
        subtitle = source[2]
    else:
        subtitle = ''
    # check for a \verb environnement, and if present, add fragile
    fragile = False
    for line in source:
        if (line.find('verb') != -1 or line.find('_') != -1):
            # There might be some false positive, but who cares ?
            fragile = True
            break

    title = apply_emphasis([], title, erase=False)
    subtitle = apply_emphasis([], subtitle, erase=False)

    # think about options syntax, like t, b, etc.
    print options
    if fragile:
        if 'fragile' not in options:
            options = ','.join(options.split(',')+['fragile'])

    if options != '':
        tex.append('\n\\begin{frame}[%s]{%s}{%s}\n' % (options, title, subtitle))
    else:
        tex.append('\n\\begin{frame}{%s}{%s}\n' % (title, subtitle))

    # loop on the slide, have a nested way of deciphering environments.
    index = 3
    while True:
        success, index = extract_environments(source, tex, index, verbose)
        if not success:
            break

    tex.append('\n\end{frame}\n')

def extract_environments(source, tex, start_index, verbose):

    # All regular expression to look out for
    env = re.compile('\s*%s\s+(.*)' % lang['md']['environments'][0])
    short_env = re.compile('\s*%s\s+(.*)\s+%s\s*' %
        (lang['md']['environments'][0], lang['md']['environments'][1]))
    list_env = re.compile('\s*([*+])([-]*)\s+(.*)')
    # This will match strings like:
    # I *have a complete italic statement*
    # I **only have the start of a bold
    #emphasis = re.compile('([^*]*)([*]+)([^* ][^*]*[^* ])([*]+.*)?')
    in_environment = False
    in_list = False
    found_sub_environment = False

    text_buffer = ''

    for index, line in enumerate(source[start_index:]):
        # if a nested environment was found, pass until index is index_nested
        if found_sub_environment:
            if index < index_nested-1:
                continue
            else:
                found_sub_environment = False

        begin_env = env.match(line)
        has_short_env = short_env.match(line)
        begin_list = list_env.match(line)
        # enter one environment,
        # Please note that an environment can not appear inside a list
        # Note as well that entering an environment will print the current
        # buffer, after taking into account emphasis
        if begin_env is not None:
            # First, test if it is a short environment
            if has_short_env is not None:
                if verbose:
                    print 'caught a short env'
                name, title, options = read_command(has_short_env.group(1))
                for option in options:
                    if option.find('%') != -1:
                        number = float(option.split('%')[0])/100
                        option_string = '%g\\textwidth' % number
                    else:
                        option_string = option
                tex.append('\%s{%s}\n' % (name, option_string))

            # if not in one: get name
            elif not in_environment:
                if verbose:
                    print ' /!\ entering env'
                in_environment = True
                name, title, options = read_command(begin_env.group(1))
                headers = get_surrounding_environment(name, options,
                        title, verbose)
                text_buffer += headers[0]
                text_buffer = apply_emphasis(tex, text_buffer)
                #tex.append(headers[0])
                # in the case of verbatim environment, spacing matter: recover
                # the index of the first character of the line
                if name in ['verbatim']:
                    index_to_strip = line.index('~')

            # if in one, recursive call to this function
            else:
                index_nested = start_index+index
                if verbose:
                    print 'found nested env'
                success, index_nested = extract_environments(source, tex,
                    index_nested, verbose)
                found_sub_environment = True
                continue
        # Entering a list environment.
        elif begin_list is not None:
            if verbose:
                line, 'detected a list'
            if not in_list:
                text_buffer = apply_emphasis(tex, text_buffer)
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
            text_buffer += '\item %s\n' % begin_list.group(3)
        else:
            # if one finds the ending pattern, return success
            if line.find(lang['md']['environments'][1]) != -1:
                if in_list:
                    text_buffer = apply_emphasis(tex, text_buffer)
                    tex.append('\end{%s}\n' % list_type)
                    if verbose:
                        print '/!\ exiting list'
                    in_list = False
                if in_environment:
                    if verbose:
                        print '/!\ exiting environment'
                    text_buffer = apply_emphasis(tex, text_buffer)
                    tex.append(headers[1])
                    return True, start_index + index
            elif line.strip() == '':
                if in_list:
                    if verbose:
                        print 'I discovered an empty line, getting out of itemize'
                    text_buffer = apply_emphasis(tex, text_buffer)
                    tex.append('\end{%s}\n' % list_type)
                    in_list = False
                else:
                    text_buffer += '\n'
            else:
                if verbose:
                    print 'normal line being written', line
                # TODO change verbatim by verbatim, python, etc...
                if (in_environment and name in ['verbatim']):
                    tex.append(line[index_to_strip:]+'\n')
                    continue
                text_buffer += line+'\n'
    # getting out

    # If we are still inside an environment, close it automatically:
    if in_environment:
        if verbose:
            print '/!\ exiting environment'
        text_buffer = apply_emphasis(tex, text_buffer)
        tex.append(headers[1])
        print headers[1]
    text_buffer = apply_emphasis(tex, text_buffer)
    return False, start_index+index

# Define all options, like width, this kind of things, and return an array of
# two lines, start and finish
def get_surrounding_environment(name, options, title, verbose):
    # take care of blocks
    start_line = ''
    out, flags = parse_options(options, verbose)

    if flags['extra_column_env']:
        start_line += '\\begin{columns}\n\column{%g\\textwidth}\n' % out['number']

    if name.find('block') != -1:
        start_line += '\\begin{%s}{%s}%s\n' % (name.strip(), title,
            out['slide_show'])
        stop_line = '\end{%s}\n' % name.strip()

    elif name.find('image') != -1:
        start_line += '\\begin{figure}\n'
        if flags['has_align']:
            start_line += '\\begin{%s}' % out['align']
        start_line += '\includegraphics[%s]{' % (out['option_string'])
        if flags['has_align']:
            stop_line = '}\caption{%s}\n\end{%s}\n' % (title, out['align'])
        else:
            stop_line = '}\caption{%s}\n\end{figure}\n' % title
    elif name.find('verbatim') != -1:
        start_line += '\\begin{%s}\n' % name
        stop_line = '\end{%s}\n' % name
    else:
        if name.find('columns') != -1:
            if out['number'] == 0:
                if verbose:
                    print 'no width specified, expecting column arguments'
                start_line += '\\begin{columns}\n'
            else:
                start_line += '\\begin{columns}\n\column{%g\\textwidth}\n' % out['number']
            stop_line = '\end{columns}\n'
        else:
            start_line = '\\begin{%s}[%s]%s\n' % (name.strip(),
                out['option_string'], out['slide_show'])
            stop_line = '\end{%s}\n' % name.strip()
    # Finishing the extra columns
    if flags['extra_column_env']:
        stop_line += '\end{columns}\n'

    return [start_line, stop_line]

def parse_options(options, verbose):

    out = {'option_string':'', 'slide_show':'', 'number':0, 'align':''}

    flags = {'extra_column_env':False, 'has_align':False}

    for option in options:
        if option.find('%') != -1:
            flags['extra_column_env'] = True
            out['number'] = float(option.split('%')[0])/100
        # take care of slide appearance
        elif option.find('<') != -1:
            out['slide_show'] = option.strip()
        elif option.strip().lower() in ['center', 'left', 'right']:
            flags['has_align'] = True
            out['align'] = option
        else:
            out['option_string'] += option+','

    return out, flags

def read_command(argument):

    options = []
    title = ''
    if len(argument.split(';')) == 1:
        name = argument
    else:
        name, options = argument.split(';')[0], argument.split(';')[1].split(',')
    if name.find('|') != -1:
        # One can specify the title of the block with a |
        name, title = name.split('|')
    return name.strip(), title.strip(), options

def apply_emphasis(tex, text_buffer, erase=True):
    """
    The text buffer contains concatenated lines, with line breaks, to treat
    through emphasis detection

    """

    #emphasis = re.compile('([^*]*)([*]+)(.*)')
    bf_it = re.compile("( \*{3})([^ \*].*?[^ \*])(\*{3})", re.DOTALL)
    bf = re.compile("( \*{2})([^ \*].*?[^ \*])(\*{2})", re.DOTALL)
    it = re.compile("( \*{1})([^ \*].*?[^ \*])(\*{1})", re.DOTALL)
    # The option re.DOTALL ensures that the newlines are considered as part of .

    text_buffer = bf_it.sub(r" {\\bf\\it \2} ", text_buffer)
    text_buffer = bf.sub(r" {\\bf \2} ", text_buffer)
    text_buffer = it.sub(r" {\\it \2} ", text_buffer)

    if erase:
        tex.append(text_buffer)
        return ''
    else:
        return text_buffer

