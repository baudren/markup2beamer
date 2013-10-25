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

    ~~~ vspace; 0.5cm ~~~

    \only<2>{ {\it Linus Torvalds}: ``Subversion used to say CVS done
    right: with that slogan there is nowhere you can go. There is no way
    to do cvs right.''}
  

An example of rst source files
-------------------------------
Or "How sphinx is magical"

    \scriptsize 

    ~~~ columns

    ~~~ column; 45% ~~~
        mcmc.rst: 
        ~~~ verbatim
        Mcmc module 
        =========== 

        .. automodule:: mcmc 
            :members: 
            :undoc-members: 
            :show-inheritance: 
        ~~~

    ~~~ column; 45% ~~~
        analyze.rst: 
        ~~~ verbatim
        Likelihood class module 
        ======================= 

        .. automodule:: likelihood_class 
            :members: 
            :undoc-members: 
            :show-inheritance: 
        ~~~

    ~~~

    ~~~ vspace; 0.5cm ~~~

    Notice the alignment inside the verbatim environment !


Illustration of emphasis
-------------------------
Different possibilities


    ~~~ block | How to emphasize your point; 60%
    * *an italic italian
      on several lines*
    * **a bold statement**
    * `a user defined emphasize`

    Note also the usage of a block without an end. It is not
    recommanded, but can be used.


Another Slide
-------------
With nothing in it

