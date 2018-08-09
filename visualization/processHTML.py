#!/usr/bin/python

from bs4 import BeautifulSoup
import argparse
import re
import os.path
import styleHTML
import scoreHTML

def process(title, directory):
    """
    Finds all articles with title to create csv with
    section titles, dates, and scores. Also adds HTML styling
    """


    fileNameList = []

    for fileName in os.listdir(directory):
        if title in fileName and fileName.endswith('.html'):
            fileNameList.append(fileName)


    #need to make sure files are in chronological order
    fileNameList.sort()
    print (fileNameList)
    for i in range(len(fileNameList)-1):

        with open(directory + fileNameList[i]) as fp:
            soup = BeautifulSoup(fp,"html.parser")

        #find dates using time stamp in title
        print(fileNameList[i])
        startDate = re.search(r'\d+\-\d+\-\d+', fileNameList[i]).group()
        endDate = re.search(r'\d+\-\d+\-\d+', fileNameList[i+1]).group()


        sectionScores, totalScore = scoreHTML.findSectionScore(soup)
        scoreHTML.writeCSV(sectionScores, totalScore, startDate, endDate, title, directory)

        soup = styleHTML.addID(soup, title)

        #rewrite HTML to how we want it to look...
        with open(directory + fileNameList[i],'w+') as file:
            file.write(str(soup.prettify()))



def fileSetUp(title, directory):
    """ Uses the template javascript files to create the ones needed for each article"""

    with open(directory + '/../temp.js') as f:
        contents = f.read()
        contents = contents.replace("TITLE", title)

    with open(directory + '/' + title + '.js', 'w') as f:
        f.write(contents)

    with open(directory + '/../temp_mat1.js') as f:
        contents = f.read()
        contents = contents.replace("TITLE", title)

    with open(directory + title + '_mat.js', 'w') as f:
            f.write(contents)

    with open(directory + '/../temp_mat2.html') as f:
            contents = f.read()
            contents = contents.replace("TITLE", title)

    with open(directory + title + '_mat.html', 'w') as f:
            f.write(contents)


def parse_args():
    parser = argparse.ArgumentParser(usage='processHTML.py [article title] [article path]')

    parser.add_argument('title', help='title of article')
    parser.add_argument('directory', help='path to html of articles')
    n=parser.parse_args()

    process(n.title, n.directory)

    fileSetUp(n.title, n.directory)

if __name__ == '__main__':
    parse_args()
