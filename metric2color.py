#!/usr/bin/python

import os
import wiki2graph as w2g


# Assumes the existence of a dictionary from an applied metric,
#   a content file, and a model file



NUMSHADES=1791




def colorPercentile(model, metricDict):
    """
        Assigns edit ids in model to colors by percentile based on
            metricDict. Returns a dictionary of colors.
    """
    print "Assigning colors . . ."
    
    # Sort by decreasing scores
    a=[(metricDict[x[1]], x[1]) for x in model]
    s=set(a)
    a=sorted(list(s), reverse=True)

    # Assign colors to nodes
    length=len(a)

    percentLen = int(length*0.1)

    colors = {}

    # Top 1%
    for i in range(percentLen):
        colors[a[i][1]]="darkred"
    # 1-5
    for i in range(percentLen, percentLen*2):
        colors[a[i][1]]="red"
    # 5-10
    for i in range(percentLen*2, percentLen*3):
        colors[a[i][1]]="mediumred"
    # 10-15
    for i in range(percentLen*3, percentLen*4):
        colors[a[i][1]]="lightred"
    # 15-25
    for i in range(percentLen*4, percentLen*5):
        colors[a[i][1]]="pink"
    for i in range(percentLen*5,length):
        colors[a[i][1]]="white"
    
    return colors



    
def writeColors(title, remove, metricName, model, content, colors):
    """
        Writes the most recent revision to a .html file based on the dictionary
            colors.
        metricName will be part of the file title
    """
    print "Writing heat map . . ."

    if not os.path.isdir('heatmaps'):
        os.mkdir('heatmaps')
    
    if remove:
        colorFile = open("heatmaps/"+(metricName+"_"+title).replace(" ", "_")+"_rem.html", "w")
    else:
        colorFile = open("heatmaps/"+(metricName+"_"+title).replace(" ", "_")+".html", "w")

    # Write style sheet
    colorFile.write("<!DOCTYPE html>\n<html>\n<head>\n<style/>\n")
    colorFile.write(".white {\n\tbackground-color: white;\n\tcolor: black;\n}\n")
    colorFile.write(".pink {\n\tbackground-color: #ffcccc;\n\tcolor: black;\n}\n")
    colorFile.write(".lightred {\n\tbackground-color: #ff9999;\n\tcolor: black;\n}\n")
    colorFile.write(".mediumred {\n\tbackground-color: #ff4d4d;\n\tcolor: black;\n}\n")
    colorFile.write(".red {\n\tbackground-color: #cc0000;\n\tcolor: black;\n}\n")
    colorFile.write(".darkred {\n\tbackground-color: #990000;\n\tcolor: black;}\n")
    colorFile.write("</style>\n</head>\n")

    # Write content
    colorFile.write("<body>\n")

    content=content.split("\n")
    content=[line.split() for line in content]

    pos=0
    dif = model[pos][0]
    color="white"
    
    for line in content:
        current = "<p><span class="+color+">"
        for i in range(len(line)):
            if dif == 0:
                while dif==0:
                    pos+=1
                    color=colors[model[pos][1]]
                    dif = model[pos][0] - model[pos-1][0]
                current+="</span><span class="+color+">"

            current+=line[i]+ " "
            dif-=1
        current+="</span></p>\n"
        colorFile.write(current)

    colorFile.write("</body>\n</html>")
    colorFile.close()




def metric2color(title, remove, metricName, metricDict):
    """
        Writes a heatmap of the most recent revision of title as a .html
            file in heatmaps, based on the percentile of the text according
            to metricDict.
    """
    content = w2g.readContent(title, remove)
    model = w2g.readModel(title, remove)
    colors=colorPercentile(model, metricDict)
    writeColors(title, remove, metricName, model, content, colors)




def getShades(model, metricDict):
    """
        Assigns a position in the color range to edits in the model, based on
            the scores in metricDict rather than percentile.
        Returns a dictionary of colors.
    """
    maxScore=max([metricDict[x[1]] for x in model])
    colors={}
    #rbg(r,b,g) From 0-255

    for (end, edit) in model:
        color=metricDict[edit]/maxScore
        colors[edit]=int(color*NUMSHADES)

    return colors




def writeShades(title, remove, metricName, model, content, colors):
    """
        Writes the most recent revision to a .html file based on the shades in the
            dictionary, colors.
        metricName will be part of the file title
    """
    print "Writing heat map . . ."

    if not os.path.isdir('heatmaps'):
        os.mkdir('heatmaps')
    
    if remove:
        colorFile = open("heatmaps/"+(metricName+"_"+title).replace(" ", "_")+"_rem.html", "w")
    else:
        colorFile = open("heatmaps/"+(metricName+"_"+title).replace(" ", "_")+".html", "w")

    # Write style sheet
    colorFile.write("<!DOCTYPE html>\n<html>\n<head>\n<style>\n")
    colorFile.write("p {\n\tcolor: black;\n}\n")

    # Write content
    colorFile.write("</style><body>\n")

    content=content.split("\n")
    content=[line.split() for line in content]

    pos=0
    dif = model[pos][0]
    color=getrgb(colors[model[pos][1]])
    
    for line in content:
        current = "<p><span style=background-color:"+color+";>"
        for i in range(len(line)):
            if dif == 0:
                while dif==0:
                    pos+=1
                    color=getrgb(colors[model[pos][1]])
                    dif = model[pos][0] - model[pos-1][0]
                current+="</span><span style=background-color:"+color+";>"

            current+=line[i]+ " "
            dif-=1
        current+="</span></p>\n"
        colorFile.write(current)

    colorFile.write("</body>\n</html>")
    colorFile.close()




def getrgb(color):
    """
        Transforms the in color into an rgb string based on
            color's position in the color range.
    """
    crange=color/256
    cval=color%256

    # Loweest scores
    # White - pink
    if crange==0:
        rgb='rgb(255,'+str(255-cval)+',255)'
    # Pink - blue
    elif crange==1:
        rgb='rgb('+str(255-cval)+',0,255)'
    # Blue - blue-green
    elif crange==2:
        rgb='rgb(0,'+str(cval)+',255)'
    # Blue-green - green
    elif crange==3:
        rgb='rgb(0,255,'+str(255-cval)+')'
    # Green - yellow
    elif crange==4:
        rgb='rgb('+str(cval)+',255,0)'
    # Yellow - red
    elif crange==5:
        rgb='rgb(255,'+str(255-cval)+',0)'
    # Red - black
    else:
        rgb='rgb('+str(255-cval)+',0,0)'

    return rgb




def metric2shades(title, remove, metricName, metricDict):
    """
        Writes a heatmap of the most recent revision of title as a .html
            file in heatmaps, based on the score in metricDict, rather
            than percentile.
    """
    content = w2g.readContent(title, remove)
    model = w2g.readModel(title, remove)
    colors=getShades(model, metricDict)
    writeShades(title, remove, metricName, model, content, colors)
