~~~ headers
input:          theme.tex
usetheme:       CambridgeUS
usecolortheme:  orchid

title:          [CLASS/{\bf MP} on Github]
author:         [BA] Benjamin Audren
institute:      [EPFL] \'Ecole Polytechnique F\'ed\'erale de Lausanne
date:           17/10/2013

outline-at-sections
no-navigation-symbols
~~~


===============================
Git version control - Github
===============================

# Title #

None
--------------

``This must be Thursday. I never could get the hang of Thursdays''
{\Grey\it (Arthur Dent, a few minutes before the Earth gets
destroyed)}


# Outline | subsectionstyle=hide #


# Version Control with Git

## Motivation

Motivation
-----------

    ~~~ block | What is Version Control ?; 80%
    * System that keeps tracks of different {\bf\Green versions} of a
      code (several file), tracking its entire {\bf\Red
      history} of creation.
    * Accessible from a {\bf\Blue central repository}, that stores all
      the versions, and allow communication between developers.
    * Can revert to a previous version to {\bf\Red reproduce} exactly
      the behaviour at a certain time (bug hunting)
    ~~~


Softwares
-----------

    ~~~ block | Version Control Softwares; 60%
    * CVS (Concurrent Versions System)
    * Apache Subversion (SVN)
    * {\only<2>{\Red\bf} Git}
    ~~~

    \vspace{0.5cm}
    \only<2>{ {\it Linus Torvalds}: ``Subversion used to say CVS done
    right: with that slogan there is nowhere you can go. There is no way
    to do cvs right.''}
  
