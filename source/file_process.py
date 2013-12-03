"""
.. module:: file_process
    :synopsis: Perform manipulations on markup and tex files
.. moduleauthor:: Benjamin Audren <benjamin.audren@epfl.ch>

"""
from collections import OrderedDict as od
from language import language_definition as lang
from copy import deepcopy
import re
import os
import subprocess as sp
import hashlib
from time import sleep

class FileProcess(object):
    """
    Define all manipulations on files, markup and tex

    """

    def __init__(self, command_line):
        """
        The FileProcess class is a convenience class that define the main
        **methods**:

        * :func:`markup_to_tex`
        * :func:`tex_to_pdf`

        It also includes all the convenience methods used in these two main
        ones, namely:

        * :func:`catch`
        * :func:`texify`
        * :func:`texify_slide`
        * :func:`extract_header_command`
        * :func:`special_action`
        * :func:`extract_environments`
        * :func:`get_surrounding_environment`
        * :func:`parse_options`
        * :func:`read_command`
        * :func:`apply_emphasis`

        The **attributes** are mostly defined for storage reason.

        """
        # create references to some command_line variables for convenience.
        self.markup_file = command_line.input
        self.verbose = command_line.verbose
        self.ext = command_line.extension

        # Create a temporary tex file
        self.tex_file = self.markup_file.replace(
            '.'+self.ext, '.tex')
        self.source = []

        # Create a dictionnary that will store as a string the lines it started
        # from in the markup file, and the resulting process written on the
        # tex.
        self.transformator = od()
        self.tex = []

        # By default, the only keyword forcing the introduction of a
        # fragile slide is verbatim
        self.fragile_keywords = ['verb', '_', 'verbatim']

    def markup_to_tex(self):
        """
        Preprocess the markup file to tex output

        """
        # Define the sequence of different parts in the text file
        parts = ['headers', 'title', 'body']

        # Recover entire file
        with open(self.markup_file, 'r') as markup:
            for line in markup:
                self.source.append(line.strip('\n').rstrip())

        # Recover sequentially the different parts.
        current_line = 0

        # Recover the header, and title. The catch function is where the
        # language is processed.
        for name in parts:
            self.transformator[name], current_line = self.catch(
                current_line, name)
        """
        .. warning::

                Note that the order: headers, title, body must be respected

        """

        # Transcribe the header into a tex file
        for name in ['headers', 'body']:
            try:
                self.texify(name)
            except UnboundLocalError:
                return False

        with open(self.tex_file, 'w') as tex_writer:
            for line in self.tex:
                if self.verbose:
                    print line.rstrip('\n')
                tex_writer.write(line)

        return True

    # define helper function
    def catch(self, start_index, context):
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
        start_string, stop_string = lang[self.ext][context]

        # If the end is nothing, goble the rest of the file
        if stop_string == '':
            return [start_index, len(self.source)+1], len(self.source)+1

        # else, do a catch between the start and stop
        # Recover the exact first line
        first_temp = [elem for elem in self.source[start_index:] if
                      elem.find(start_string) != -1]
        try:
            first_index = self.source[start_index:].index(
                first_temp[0])+start_index
        except IndexError:
            # this means no start_string was found
            return [None, None], start_index

        # Recover the exact last line
        second_temp = [elem for elem in self.source[first_index+1:] if
                       elem.find(stop_string) != -1]
        try:
            second_index = (self.source[first_index+1:].index(second_temp[0]) +
                            first_index+1)
        except IndexError:
            # this means the finishing line was not found
            return [first_index, None], first_index+1

        return [first_index, second_index+1], second_index+1

    def texify(self, context):
        """
        Given the context (headers or body), translate the markup to tex

        When in the body part, it will call :func:`texify_slide` for each slide
        found.

        """
        start_index = self.transformator[context][0]
        stop_index = self.transformator[context][1]

        self.title = self.source[self.transformator['title'][0]+1]

        text = deepcopy(self.source[start_index:stop_index])
        if self.verbose:
            print 'Trying to texify the following', text
            print 'in the context of', context

        if context == 'headers':
            # must extract syntax and transform into latex commands
            for line in text:
                if self.verbose:
                    print 'header line', line
                if len(line) != 0:
                    self.extract_header_command(line)

        elif context == 'body':
            self.tex.append('\n\\begin{document}\n')

            # Search for special frames
            special = re.compile('%s\s+(.*)\s+%s' % (
                lang[self.ext]['special-frames'][0],
                lang[self.ext]['special-frames'][1]))

            # have different possibilities, so far this one is not very robust,
            # because need another test.
            if lang[self.ext]['section'][1] == 'before':
                sections = re.compile('(%s+)\s(.*)' % (
                    lang[self.ext]['section'][0]))

            # initialize position tracking
            in_slide = False

            for index, line in enumerate(text):
                special_frame = special.match(line)
                section = sections.match(line)

                # catch special frames, that are only one liners
                if special_frame is not None:
                    if self.verbose:
                        print 'catching special command', line
                    # first, exit current slide if any
                    if in_slide:
                        self.texify_slide(text[first_index:index])
                        in_slide = False
                    action = special_frame.group(1).lower()
                    self.special_action(action)
                    continue

                # catch (sub)sections
                elif section is not None:
                    if self.verbose:
                        print 'catching beginning of section'
                    if section.group(2).find(
                            lang[self.ext]['section'][0]) == -1:
                        level = '%ssection' % ''.join(
                            ['sub' for i in range(len(section.group(1))-1)])
                        if in_slide:
                            self.texify_slide(text[first_index:index])
                            in_slide = False
                        self.tex.append('\n\%s{%s}\n\n' % (
                            level, section.group(2)))

                # Catch title frame
                elif line.find(lang[self.ext]['frame-title'][0]) != -1:
                    # Recover potential options at the end of the line, like
                    # ------- fragile, t
                    # This will be triggered at the first slide, and after
                    # sections
                    if not in_slide:
                        in_slide = True
                        first_index = index-1
                        continue
                    # triggered when reaching the end of a slide
                    else:
                        last_index = index-2
                        self.texify_slide(text[first_index:last_index+1])
                        first_index = index-1

                # when reaching the end, wrap up
                if index == len(text)-1:
                    self.texify_slide(text[first_index:index+1])

            self.tex.append('\n\end{document}\n')

    def texify_slide(self, source):
        """
        Translate a source markup slide into tex

        """
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
            for elem in self.fragile_keywords:
                if line.find(elem) != -1:
                    fragile = True
                    break

        title = self.apply_emphasis(title, erase=False)
        subtitle = self.apply_emphasis(subtitle, erase=False)

        # think about options syntax, like t, b, etc.
        if fragile:
            if 'fragile' not in options:
                options_array = [elem for elem in options.split(',') if elem]
                options_array.append('fragile')
                options = ','.join(options_array)

        if options != '':
            self.tex.append('\n\\begin{frame}[%s]{%s}{%s}\n' % (
                options, title, subtitle))
        else:
            self.tex.append('\n\\begin{frame}{%s}{%s}\n' % (title, subtitle))

        # loop on the slide, have a nested way of deciphering environments.
        index = 3
        while True:
            success, index = self.extract_environments(index, source)
            if not success:
                break

        self.tex.append('\n\end{frame}\n')

    def extract_header_command(self, line):
        """
        Recover the underlying meaning for a header line

        If a column is found within the command, it will be interpreted as a
        latex command, and will simply put curly brackets around. In the other
        case, it will try to match any self-implemented methods.

        """
        is_normal_command = False
        if line.find(':') != -1:
            is_normal_command = True

        if is_normal_command:
            action, arguments = line.split(':')
            # on the first line, either an input or document class
            if len(self.tex) == 0:
                if action != 'input':
                    self.tex.append('\documentclass\
                        [xcolor=dvipsnames]{beamer}\n')
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
                        main = self.title
                    self.tex.append('\%s[%s]{%s}\n' % (
                        action, option, main))
                else:
                    self.tex.append(
                        '\%s{%s}\n' % (action, argument))
        # if there was no :, it means it is a special command
        else:
            if line.find('outline-at-sections') != -1:
                self.tex.append('\AtBeginSection[]\n\
                    {\\begin{frame}<beamer>\n')
                self.tex.append('\\frametitle{Outline}\n\
                    \\tableofcontents[\n')
                self.tex.append('currentsection,sectionstyle=show/shaded,')
                self.tex.append('subsectionstyle=show/show/hide]\n\
                    \end{frame}}\n')
            elif line.find('no-navigation-symbols') != -1:
                self.tex.append('\setbeamertemplate\
                    {navigation symbols}{}\n')
            elif line.find('automatic-fragile') != -1:
                self.fragile_keywords.extend(
                    line.split('=')[-1].strip().split(','))
            else:
                pass

    def tex_to_pdf(self, pdf_file, texify_only=False):
        """
        Run once a pdflatex compilation, and open the pdf file

        .. warning::
            So far, only for Mac users with the open command

        """

        # Simply run twice pdflatex
        local_tex = self.tex_file.split(os.path.sep)[-1]
        if not texify_only:
            os.chdir(os.path.sep.join(self.tex_file.split(os.path.sep)[:-1]))

            if not pdf_file:
                pdf_file = local_tex.replace('.tex', '.pdf')
            else:
                pdf_file = pdf_file.split(os.path.sep)[-1]

        sp.call(["pdflatex", local_tex])
        sp.call(["pdflatex", local_tex])
        if not texify_only:
            sp.call(["open", "-a", "/Applications/Skim.app", pdf_file])

        return True

    def interactive_pdf(self, pdf_file):
        """
        Run interactively the pdflatex compilation

        It loops indefinitely, and as soon as it changes on disc, recompile the
        texfile.
        """
        local_pdf = pdf_file.split(os.path.sep)[-1]
        local_markup = self.markup_file.split(os.path.sep)[-1]
        root_dir = os.path.abspath(os.curdir)
        tex_dir = os.path.abspath(
            os.path.sep.join(self.tex_file.split(os.path.sep)[:-1]))

        # going to the latex dir
        os.chdir(tex_dir)

        self.tex_to_pdf(pdf_file, texify_only=True)
        sp.call(["open", "-a", "/Applications/Skim.app", local_pdf])
        # Store the hash md5 of the tex file
        md5sum = md5_for_file(local_markup, hr=True)
        while True:
            sleep(1)
            os.chdir(tex_dir)
            newmd5 = md5_for_file(local_markup, hr=True)
            if newmd5 != md5sum:
                os.chdir(root_dir)
                # Clean the variables
                self.source = []
                self.transformator = od()
                self.tex = []
                # Reprocess the markup
                success = self.markup_to_tex()
                if success:
                    os.chdir(tex_dir)
                    self.tex_to_pdf(pdf_file, texify_only=True)
                    md5sum = newmd5

    def special_action(self, action):
        """
        Define the behaviour for special slides

        So far, only `title` and `outline` are implemented. For the syntax
        needed to call such a slide, look at the language file.

        """
        self.tex.append('\\begin{frame}\n')
        if action == 'title':
            self.tex.append('\\titlepage\n')
        elif action.find('outline') != -1:
            # check if option is specified with pipe
            self.tex.append('\\frametitle{Outline}\n')
            if len(action.split('|')) == 1:
                self.tex.append('\\tableofcontents\n')
            else:
                action, complement = action.split('|')
                self.tex.append('\\tableofcontents[%s]\n' % complement)
        else:
            print 'warning, %s not understood', action
        self.tex.append('\end{frame}\n')

    def extract_environments(self, start_index, source):
        """
        Extract the latex environment from start_index

        """

        # All regular expression to look out for
        env = re.compile('\s*%s\s+(.*)' % lang[self.ext]['environments'][0])
        short_env = re.compile(
            '\s*%s\s+(.*)\s+%s\s*' % (
                lang[self.ext]['environments'][0],
                lang[self.ext]['environments'][1]))
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
            # if a nested environment was found, pass until index is
            # index_nested
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
                    if self.verbose:
                        print 'caught a short env'
                    name, title, options = self.read_command(
                        has_short_env.group(1))
                    for option in options:
                        if option.find('%') != -1:
                            number = float(option.split('%')[0])/100
                            option_string = '%g\\textwidth' % number
                        else:
                            option_string = option
                    self.tex.append('\%s{%s}\n' % (name, option_string))

                # if not in one: get name
                elif not in_environment:
                    if self.verbose:
                        print ' /!\ entering env'
                    in_environment = True
                    name, title, options = self.read_command(
                        begin_env.group(1))
                    headers = self.get_surrounding_environment(
                        name, options, title)
                    text_buffer += headers[0]
                    text_buffer = self.apply_emphasis(text_buffer)
                    #tex.append(headers[0])
                    # in the case of verbatim environment, spacing matter:
                    # recover the index of the first character of the line
                    if name in self.fragile_keywords:
                        index_to_strip = line.index('~')

                # if in one, recursive call to this function
                else:
                    index_nested = start_index+index
                    if self.verbose:
                        print 'found nested env'
                    success, index_nested = self.extract_environments(
                        index_nested, source)
                    #found_sub_environment = True
                    found_sub_environment = success
                    continue
            # Entering a list environment.
            elif begin_list is not None:
                if self.verbose:
                    print line, 'detected a list'
                if not in_list:
                    text_buffer = self.apply_emphasis(text_buffer)
                    in_list = True
                    # Recover the type of the list
                    if begin_list.group(1) == '+':
                        list_type = 'enumerate'
                    else:
                        # take the only other possibility.
                        list_type = 'itemize'
                    # Recover the potential option to have a reveal
                    if begin_list.group(2) == '':
                        self.tex.append('\\begin{%s}\n' % list_type)
                    else:
                        self.tex.append('\\begin{%s}[<+->]\n' % list_type)
                text_buffer += '\item %s\n' % begin_list.group(3)
            else:
                # if one finds the ending pattern, return success
                if line.find(lang[self.ext]['environments'][1]) != -1:
                    if in_list:
                        text_buffer = self.apply_emphasis(text_buffer)
                        self.tex.append('\end{%s}\n' % list_type)
                        if self.verbose:
                            print '/!\ exiting list'
                        in_list = False
                    if in_environment:
                        if self.verbose:
                            print '/!\ exiting environment'
                        text_buffer = self.apply_emphasis(text_buffer)
                        self.tex.append(headers[1])
                        return True, start_index + index
                elif line.strip() == '':
                    if in_list:
                        if self.verbose:
                            print('I discovered an empty line, \
                                getting out of itemize')
                        text_buffer = self.apply_emphasis(text_buffer)
                        self.tex.append('\end{%s}\n' % list_type)
                        in_list = False
                    else:
                        text_buffer += '\n'
                else:
                    if self.verbose:
                        print 'normal line being written', line
                    if (in_environment and name in self.fragile_keywords):
                        self.tex.append(line[index_to_strip:]+'\n')
                        continue
                    text_buffer += line+'\n'
        # getting out

        # If we are still inside an environment, close it automatically:
        if in_environment:
            if self.verbose:
                print '/!\ exiting environment'
            text_buffer = self.apply_emphasis(text_buffer)
            self.tex.append(headers[1])
        text_buffer = self.apply_emphasis(text_buffer)
        return False, start_index+index

    # Define all options, like width, this kind of things, and return an array
    # of two lines, start and finish
    def get_surrounding_environment(self, name, options, title):
        # take care of blocks
        start_line = ''
        out, flags = self.parse_options(options)

        if flags['extra_column_env']:
            start_line += '\\begin{columns}\n\
                \column{%g\\textwidth}\n' % out['number']

        if name.find('block') != -1:
            start_line += '\\begin{%s}{%s}%s\n' % (
                name.strip(), title, out['slide_show'])
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
                    if self.verbose:
                        print 'no width specified, expecting column arguments'
                    start_line += '\\begin{columns}\n'
                else:
                    start_line += '\\begin{columns}\
                        \n\column{%g\\textwidth}\n' % out['number']
                stop_line = '\end{columns}\n'
            else:
                start_line = '\\begin{%s}[%s]%s\n' % (
                    name.strip(), out['option_string'], out['slide_show'])
                stop_line = '\end{%s}\n' % name.strip()
        # Finishing the extra columns
        if flags['extra_column_env']:
            stop_line += '\end{columns}\n'

        return [start_line, stop_line]

    def parse_options(self, options):

        out = {'option_string': '', 'slide_show': '', 'number': 0, 'align': ''}

        flags = {'extra_column_env': False, 'has_align': False}

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

    def read_command(self, argument):

        options = []
        title = ''
        if len(argument.split(';')) == 1:
            name = argument
        else:
            name, options = (
                argument.split(';')[0], argument.split(';')[1].split(','))
        if name.find('|') != -1:
            # One can specify the title of the block with a |
            name, title = name.split('|')
        return name.strip(), title.strip(), options

    def apply_emphasis(self, text_buffer, erase=True):
        """
        The text buffer contains concatenated lines, with line breaks, to treat
        through emphasis detection

        """

        #emphasis = re.compile('([^*]*)([*]+)(.*)')
        bf_it = re.compile("( \*{3})([^ \*].*?[^ \*])(\*{3})", re.DOTALL)
        bf = re.compile("( \*{2})([^ \*].*?[^ \*])(\*{2})", re.DOTALL)
        it = re.compile("( \*{1})([^ \*].*?[^ \*])(\*{1})", re.DOTALL)
        # The option DOTALL ensures that the newlines are considered as part of
        # .

        text_buffer = bf_it.sub(r" {\\bf\\it \2} ", text_buffer)
        text_buffer = bf.sub(r" {\\bf \2} ", text_buffer)
        text_buffer = it.sub(r" {\\it \2} ", text_buffer)

        if erase:
            self.tex.append(text_buffer)
            return ''
        else:
            return text_buffer


def md5_for_file(path, block_size=256*128, hr=False):
    '''
    Block size directly depends on the block size of your filesystem
    to avoid performances issues
    Here I have blocks of 4096 octets (Default NTFS)

    Taken from http://stackoverflow.com/a/17782753
    '''
    md5 = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(block_size), b''):
            md5.update(chunk)
    if hr:
        return md5.hexdigest()
    return md5.digest()
