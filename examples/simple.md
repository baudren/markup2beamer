~~~ headers
usepackage:     graphicx, wasysym, hyperref 
usepackage:     color
usetheme:       CambridgeUS
usecolortheme:  orchid

title:          [presentation]
author:         [BA] Benjamin Audren
institute:      [EPFL] \'Ecole Polytechnique F\'ed\'erale de Lausanne
date:           \today
~~~

=================================
A nice and quick presentation
=================================

# Title #
# Outline #

# Section

## First subsection

Slide title
-----------
Slide subtitle

    body of text, with

    ~~~ block | A catchy block title; 80%
    some text, and some more text
    ~~~

    ~~~ exampleblock
    A nice intro about life **etc**, without title. It will contain
    * a list
    * of nice items
    ~~~

Another slide
-------------

    This time with no subtitle, but with a centered image!

    ~~~ image | A nice programming language; center, scale=0.4
    python-logo.png
    ~~~

## Another subsection

# Second section

A lonely slide in a lonely world
--------------------------------

    ~~~ columns; 50%
    +- but at least
    +- it has a reveal
    +- enumerate in it !
    ~~~

    ~~~ alertblock | This one is red; 50%
    just to show all the possible blocks !
    ~~~

    It more importantly contains some \verb?verbatim?
