o if an input command is in the headers, do not include a
  \documentclass command
o have a clean way of asking for \only, in blocks ...
- and generally
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
  etc). So far, no user defined, and not recognised everywhere, only in
  body: make something more general !
