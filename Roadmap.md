o if an input command is in the headers, do not include a
  \documentclass command
o have a clean way of asking for \only, in blocks ...
- and anywhere
o support images
o allow for slides with no Title (None), and coming before the title
  and outline slide
o nested environments work
o allow for <2> type options for blocks, anything.
o for verbatim, remove the strip command, and the empty options
o good handling of column environments
o better option handling
o have a short environment type (for commands like vspace, column)
~ recognise *toto*, **toto**, for it and bf,  and `toto`, ``toto``,
  ```toto``` for user defined emphasis (like \color{BrickRed}\bf,
  etc). So far, no user defined !
o being able to use a * in a math environment without interpretating
  it ! (should work)
o specify in headers which environments should start a fragile
  environment
o being able to specify 'fragile' for a given slide.
o detect language from extension
o automatic installer (decide between setup.py and a normal python
  file)
o can be run as a script (if the file changed on disk, reapply the
  convert, texify, and output)
- allow for clear new languages definitions (proper use of flags,
  etc)
