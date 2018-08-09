from bs4 import BeautifulSoup
import re
import os.path
def addID(soup,title):
    doc = '''
        <!DOCTYPE html>

        <html>
        <head>
        <link href="../style.css" rel="stylesheet"/>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.6/d3.js"></script>
        <script src="../d3-timeline.js"></script>
        <script src="https://d3js.org/d3-zoom.v1.min.js"></script>
        <script src="TITLE.js"></script>
        </head>
        <body>
        <svg id="timeline1"></svg>
        <div id="box">
        <a href="https://en.wikipedia.org/wiki/TITLE" id="wikilink" target="_blank">
        <p><span class="c4" id="heading">TITLE</span></p></a>
        <a href="TITLE_mat.html" id="matlink"><p><span class="c4" id="heading">Overview</span></p></a>
        </div>
        <div id="textbody">


        </div></body>
        </html> '''

    doc = doc.replace("TITLE", title)


    tempSoup = BeautifulSoup(doc,"html.parser")

    textBody = tempSoup.find("div",id="textbody")
    text = soup.findAll("p")



    titles = soup.findAll("span",text=re.compile(r'=='))
    subtitles = soup.findAll("span",text=re.compile(r'==='))

    for element in titles:
        if element not in subtitles:

            element.string = element.text.replace("=",'')
            element['id'] = 'title'
            new_tag = soup.new_tag("hr")
            element.insert_after(new_tag)

    for element in subtitles:
        element.string = element.text.replace("=",'')
        element['id'] = 'subtitle'

    for element in text:
        textBody.append(element)

    return tempSoup
