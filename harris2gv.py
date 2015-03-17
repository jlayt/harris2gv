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

dataset = ''
nodes = []
edges = []

def parseValueList(input, tag):
    return input[len(tag):].strip().replace(',', ' ').split()

def setNode(node, unit):
    nodes.append({'id': node, 'unit': unit})

def setEdges(node, below):
    for descendent in below:
        edges.append([node, descendent])

def readFile():
    with open(source) as file:
        print 'Opened file :' + source
        line = file.readline().strip()
        if (line is None or not line.startswith('Stratigraphic Dataset')):
            print 'Invalid Header Line'
            return
        dataset = line.strip().lstrip('Stratigraphic Dataset').strip()
        print 'Reading dataset: ' + dataset
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
                setNode(context, unit)
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

        setNode(context, unit)
        setEdges(context, below)

if len(argv) = 2:
    cmd, source = argv
else:
    cmd, source, destination = argv

readFile()

if
print 'Nodes:'
for node in nodes:
    print node

print 'Edges'
for edge in edges:
    print '    ' + edge[0] + ' -> ' + edge[1] + ';'
