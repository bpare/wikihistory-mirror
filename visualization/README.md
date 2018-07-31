This software needs the file "d3-timeline.js" in the visualization directory.
you can get it here: https://github.com/jiahuang/d3-timeline/tree/master/src.


To see the visualization properly, you need to create a local web server within the visualization directory.
You can use python:

      python -m SimpleHTTPServer 8000
      
For python 3.x:

      python -m http.server 8000
      
then go to http://localhost:8000/
      
Click on any of the article html files to start

you can navigate by clicking on the timeline, in order to see the article from that date.

by clicking "Overview" you will see a matrix visualization consisting of subsections from the article over time.

clicking anywhere on this matrix will link you back to the respective article from that date.

clicking on the article name in the top left will open the article on wikipedia.

      
