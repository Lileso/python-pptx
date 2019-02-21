.. image:: https://travis-ci.org/scanny/python-pptx.svg?branch=master
   :target: https://travis-ci.org/scanny/python-pptx

*python-pptx* is a Python library for creating and updating PowerPoint (.pptx)
files.

A typical use would be generating a customized PowerPoint presentation from
database content, downloadable by clicking a link in a web application.
Several developers have used it to automate production of presentation-ready
engineering status reports based on information held in their work management
system. It could also be used for making bulk updates to a library of
presentations or simply to automate the production of a slide or two that
would be tedious to get right by hand.

More information is available in the `python-pptx documentation`_.

Browse `examples with screenshots`_ to get a quick idea what you can do with
python-pptx.

.. _`python-pptx documentation`:
   https://python-pptx.readthedocs.org/en/latest/

.. _`examples with screenshots`:
   https://python-pptx.readthedocs.org/en/latest/user/quickstart.html


==========New Feature Added==========
Autoplay for Videos
I've added an option for autoplay. This is still quite buggy but I am going to keep working on it in the background. 
To enable this just add the tag "autoplay=True" to the end of your add_movie statment as seen below.
```
slide.shapes.add_movie(MovieFile, left, top, width, height, poster_frame_image=None, mime_type='video/mp4', autoplay=True) 
```

Known Bug: Whilst the video autoplays if you have slide transitions enabled it won't wait until the end of the video in before moving on slides.
