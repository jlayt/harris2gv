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

from sys import argv

source =''
destination = ''

dataset = ''
nodes = []
edges = []

def parseValueList(input, tag):
    return input[len(tag):].strip().replace(',', ' ').split()

def getNode(id):
    for node in nodes:
        if node['id'] == id:
            return node

def setNode(node, unit, above, below):
    nodes.append({'id': node, 'unit': unit, 'above': above, 'below': below})

def setEdges(parent, children):
    for child in children:
        edges.append({'from': parent, 'to': child, 'weight': 1})

def childEdgesForNode(id):
    children = []
    for edge in edges:
        if edge['from'] == id:
            children.append(edge)
    return children

def parentEdgesForNode(id):
    parents = []
    for edge in edges:
        if edge['to'] == id:
            parents.append(edge)
    return parents

def readFile():
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
            if (line == ''):
                pass
            elif (not line.startswith('            ')):
                setNode(context, unit, len(above), len(below))
                setEdges(context, below)
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

        setNode(context, unit, len(above), len(below))
        setEdges(context, below)

def weightEdges():
    for edge in edges:
        if getNode(edge['from'])['below'] == 1:
            edge['weight'] = edge['weight'] + 2
        if getNode(edge['to'])['above'] == 1:
            edge['weight'] = edge['weight'] + 2

if len(argv) == 2:
    cmd, source = argv
else:
    cmd, source, destination = argv

readFile()
#weightEdges()

print 'strict digraph' + dataset.replace(' ', '_') + '{'
print '    splines=polyline' # Should be ortho but ports support not implemented
print '    concentrate=true'
print '    ranksep="1.0 equally"'
print '    nodesep="2.0 equally"'
print '    node [shape=box]'
print '    edge [arrowhead=none headport=n tailport=s]'

#print 'Nodes:'
#for node in nodes:
#    print node

#print 'Edges'
for edge in edges:
    print '    ' + '"' + edge['from'] + '"' + ' -> ' + '"' + edge['to'] + '" [weight=' + str(edge['weight']) + '];'

print '}'
