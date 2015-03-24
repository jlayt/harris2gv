# -*- coding: utf-8 -*-
"""
/***************************************************************************
                                      Ark
                                 A QGIS plugin
             QGIS Plugin for ARK, the Archaeological Recording Kit
                              -------------------
        begin                : 2015-03-02
        git sha              : $Format:%H$
        copyright            : (C) 2015 by L - P: Heritage LLP
        copyright            : (C) 2015 by John Layt
        email                : john@layt.net
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import sys

source =''
destination = ''
graph = 'gml'

dataset = ''
nodes = []
edges = []
nodeId = 0
edgeId = 0
boxWidth = 50
boxHeight = 25

def parseValueList(input, tag):
    return input[len(tag):].strip().replace(',', ' ').split()

def setNode(node, unit):
    global nodeId
    if node:
        nodes.append({'id': nodeId, 'label': node, 'unit': unit})
        nodeId += 1

def setEdges(source, targets):
    global edgeId
    for target in targets:
        edges.append({'id': edgeId, 'source': source, 'target': -1, 'targetLabel': target})
        edgeId += 1

def nodeIdForLabel(label):
    for node in nodes:
        if node['label'] == label:
            return node['id']
    return -1

def readLst():
    with open(source) as file:
        #print 'Opened file : ' + source
        line = file.readline().strip()
        if (line is None or not line.startswith('Stratigraphic Dataset')):
            print 'Invalid Header Line'
            return
        dataset = line.strip()[len('Stratigraphic Dataset'):].strip()
        #print 'Reading dataset: ' + dataset
        line = file.readline().strip()
        if (line is None or line != ''):
            print 'Missing Blank Line'
            return
        line = file.readline().strip()
        if (line is None or line != 'Name'):
            print 'Invalid Name Line'
            return
        context = ''
        above = []
        contemporary = []
        equal = []
        below = []
        unit = ''
        for line in file:
            if (line.strip() == ''):
                pass
            elif (not line.startswith(' ')):
                if (context):
                    setEdges(nodeId, below)
                    setNode(context, unit)
                context = line.strip()
                above = []
                contemporary = []
                equal = []
                below = []
                unit = ''
            else:
                attribute = line.strip()
                if (attribute.lower().startswith('above:')):
                    above.extend(parseValueList(attribute, 'above:'))
                elif (attribute.lower().startswith('contemporary with:')):
                    contemporary.extend(parseValueList(attribute, 'contemporary with:'))
                elif (attribute.lower().startswith('equal to:')):
                    equal.extend(parseValueList(attribute, 'equal to:'))
                elif (attribute.lower().startswith('below:')):
                    below.extend(parseValueList(attribute, 'below:'))
                elif (attribute.lower().startswith('unit class:')):
                    unit = attribute[len('unit class:'):].strip()

        if context:
            setEdges(nodeId, below)
            setNode(context, unit)

        for edge in edges:
            edge['target'] = nodeIdForLabel(edge['targetLabel'])


def writeGv():
    print 'digraph' + dataset.replace(' ', '_') + '{'
    print '    splines=polyline' # Should be ortho but ports support not implemented
    print '    concentrate=true'
    print '    ranksep="1.0 equally"'
    print '    nodesep="2.0 equally"'
    print '    node [shape=box]'
    print '    edge [arrowhead=none headport=n tailport=s width=' + boxWidth + ' height=' + boxHeight + ']'

    for edge in edges:
        print '    ' + '"' + edge['source'] + '"' + ' -> ' + '"' + edge['target'] + '";'

    print '}'


def writeGml():
    print 'graph ['
    print '    directed 1'
    i = 0
    for node in nodes:
        print '    node ['
        print '        id ' + str(node['id'])
        print '        label "' + str(node['label']) + '"'
        print '        graphics ['
        print '            x 0.0'
        print '            y 0.0'
        print '            w 50.0'
        print '            h 25.0'
        print '        ]'
        print '    ]'
        i += 1

    i = 0
    for edge in edges:
        print '    edge ['
        print '        id ' + str(edge['id'])
        print '        source ' + str(edge['source'])
        print '        target ' + str(edge['target'])
        print '        graphics ['
        print '            fill "0"'
        print '            arrow "none"'
        print '        ]'
        print '    ]'

    print ']'

if len(sys.argv) == 2:
    cmd, source = sys.argv
else:
    cmd, source, destination = sys.argv

readLst()

old_stdout = sys.stdout
if (destination):
    sys.stdout = open(destination, 'w')

if graph = 'gv':
    writeGv()
else:
    writeGml()

if (destination):
    sys.stdout = old_stdout
