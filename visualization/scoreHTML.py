#!/usr/bin/python

from bs4 import BeautifulSoup
import re
import csv
import os.path


def findColor(score):
    """ returns the color used to represent the numerical score """
    if score >= 0 and score < 5:
        color = '#F5F9FC'
    elif score >= 5 and score < 10:
        color = '#EBF4FA'
    elif score >= 10 and score < 15:
        color = '#E1EFF7'
    elif score >= 15 and score < 20:
        color = '#D7EAF5'
    elif score >= 20 and score < 25:
        color = '#CDE4F3'
    elif score >= 25 and score < 30:
        color = '#C3DFF0'
    elif score >= 30 and score < 35:
        color = '#BADAEE'
    elif score >= 35 and score < 40:
        color = '#B0D5EB'
    elif score >= 40 and score < 45:
        color = '#A6CFE9'
    elif score >= 45 and score < 50:
        color = '#9CCAE7'
    elif score >= 50 and score < 55:
        color = '#92C5E4'
    elif score >= 55 and score < 60:
        color = '#88C0E2'
    elif score >= 60 and score < 65:
        color = '#7EBADF'
    elif score >= 65 and score < 70:
        color = '#75B5DD'
    elif score >= 70 and score < 75:
        color = '#6BB0DB'
    elif score >= 75 and score < 80:
        color = '#61ABD8'
    elif score >= 80 and score < 85:
        color = '#57A5D6'
    elif score >= 85 and score < 90:
        color = '#439BD1'
    elif score >= 95 and score <= 100:
        color = '#3A96CF'
    else:
        color = '#ffffff'

    return color

def findTagScore(tag, wordCount, score):
    """
    parses each tag for word count and score (c0-c4)
    to update and return overall scores and word count
    """

    if tag.get("class")[0] == u'c0':
        score += len(re.findall('\w+', tag.text))*100
        wordCount += len(re.findall('\w+', tag.text))
    if tag.get("class")[0] == u'c1':
        score += len(re.findall('\w+', tag.text))*80
        wordCount += len(re.findall('\w+', tag.text))
    if tag.get("class")[0] == u'c2':
        score += len(re.findall('\w+', tag.text))*60
        wordCount += len(re.findall('\w+', tag.text))
    if tag.get("class")[0] == u'c3':
        score += len(re.findall('\w+', tag.text))*40
        wordCount += len(re.findall('\w+', tag.text))
    if tag.get("class")[0] == u'c4':
        score += len(re.findall('\w+', tag.text))*20
        wordCount += len(re.findall('\w+', tag.text))

    return score, wordCount

def findSectionScore(soup):
    """
    Returns 0-100 score for each section and total score.
    This would be more accurate if we could use the
    decimal score for each span rather than a 0-4 score
    """

    #wordCount and score are used for each section, totalScore and totalWords are for the entire article
    wordCount = 0
    sectionScores = {}
    currentSection = ''
    score = 0
    totalScore = 0
    totalWords = 0

    # we go through all of the text in the article
    for tag in soup.findAll("span"):

        #figure out which sub section the words belong to
        newSection = tag.find_previous(text=re.compile(r'^=='))

        if newSection == None:
            continue

        #update sectionScores and totalScore if we come to the end of a section
        if newSection is not currentSection:
            if wordCount and score:
                score = score/wordCount
                sectionScores[currentSection] = score

            currentSection = newSection
            totalWords += wordCount
            totalScore += score *wordCount

            score = 0
            wordCount = 0

        score, wordCount = findTagScore(tag, wordCount,score)

    if totalWords:

        totalScore = totalScore/totalWords



    return sectionScores, totalScore

def writeCSV(sectionScores, totalScore, startDate, endDate, title, directory):
    """
    Writes 2 CSV files - one for section scores
    and one for total scores. writes a new csv file
    if it does not exist or updates existing one.
    """


    fieldnames = ['Start','End','Section', 'Color','Rate']


    if os.path.exists(directory + title + ".csv"):
        with open(directory + title + ".csv",'a') as csvfile:
            writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
            for section in sectionScores:
                writer.writerow({'Start': startDate,'End': endDate,'Section': section.replace("=",''), 'Color': findColor(sectionScores[section]), 'Rate': sectionScores[section]})
    else:
        with open(directory + title + ".csv",'w+') as csvfile:
            writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
            writer.writeheader()
            for section in sectionScores:
                writer.writerow({'Start': startDate,'End': endDate,'Section': section.replace("=",''), 'Color': findColor(sectionScores[section]), 'Rate': sectionScores[section]})

    if os.path.exists(directory + title + "Total.csv"):

        with open(directory + title + "Total.csv",'a') as csvfile:
            fieldnames = ['Start','End','Color','Rate']
            writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
            writer.writerow({'Start': startDate,'End': endDate, 'Color': findColor(totalScore), 'Rate': totalScore})
    else:
        with open(directory + title + "Total.csv",'w+') as csvfile:
            fieldnames = ['Start','End','Color','Rate']
            writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({'Start': startDate,'End': endDate, 'Color': findColor(totalScore), 'Rate': totalScore})
