#!/usr/bin/env python
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

import sys, os, argparse

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

def setEdges(sourceId, sourceLabel, targets):
    global edgeId
    for targetLabel in targets:
        edges.append({'id': edgeId, 'source': sourceId, 'sourceLabel': sourceLabel, 'target': -1, 'targetLabel': targetLabel})
        edgeId += 1

def nodeIdForLabel(label):
    for node in nodes:
        if node['label'] == label:
            return node['id']
    return -1

def readLst(file):
    line = file.readline().strip()
    if (line is None or not line.startswith('Stratigraphic Dataset')):
        print 'Invalid Header Line'
        return
    dataset = line.strip()[len('Stratigraphic Dataset'):].strip()
    if args.name:
        dataset = args.name
    elif not dataset:
        dataset = 'harris'
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
                setEdges(nodeId, context, below)
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
        setEdges(nodeId, context, below)
        setNode(context, unit)

    for edge in edges:
        edge['target'] = nodeIdForLabel(edge['targetLabel'])


def writeGv(simple):
    print 'digraph' + dataset.replace(' ', '_') + '{'
    if not simple:
        print '    splines=polyline' # Should be ortho but ports support not implemented
        print '    concentrate=true'
        print '    ranksep="1.0 equally"'
        print '    nodesep="2.0 equally"'
        print '    node [shape=box]'
        print '    edge [arrowhead=none headport=n tailport=s width=' + str(boxWidth) + ' height=' + str(boxHeight) + ']'

    for edge in edges:
        print '    ' + '"' + str(edge['sourceLabel']) + '"' + ' -> ' + '"' + str(edge['targetLabel']) + '";'

    print '}'


def writeGml(simple):
    print 'graph ['
    print '    directed 1'

    for node in nodes:
        print '    node ['
        print '        id ' + str(node['id'])
        print '        label "' + str(node['label']) + '"'
        if not simple:
            print '        graphics ['
            print '            type "rectangle"'
            print '            w 50.0'
            print '            h 25.0'
            print '        ]'
        print '    ]'

    for edge in edges:
        print '    edge ['
        print '        id ' + str(edge['id'])
        print '        source ' + str(edge['source'])
        print '        target ' + str(edge['target'])
        if not simple:
            print '        graphics ['
            print '            arrow "none"'
            print '        ]'
        print '    ]'

    print ']'


def writeGraphML(simple):
    print '<?xml version="1.0" encoding="UTF-8"?>'

    print '<graphml xmlns="http://graphml.graphdrawing.org/xmlns"'
    print '         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
    print '         xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">'

    print '    <graph id="' + dataset + '" edgedefault="directed">'

    for node in nodes:
        if simple:
            print '        <node id="' + str(node['label']) + '"/>'
        else:
            print '        <node id="' + str(node['label']) + '">'
            print '            <port name="North"/>'
            print '            <port name="South"/>'
            print '        </node>'

    for edge in edges:
        if simple:
            print '        <edge id="' + str(edge['id']) + '" source="' + str(edge['sourceLabel']) + '" target="' + str(edge['targetLabel']) + '"/>'
        else:
            print '        <edge id="' + str(edge['id']) + '" source="' + str(edge['sourceLabel']) + '" target="' + str(edge['targetLabel']) + '" sourceport="South" targetport="North"/>'

    print '    </graph>'
    print '</graphml>'


parser = argparse.ArgumentParser(description='A tool to convert legacy .LST Harris Matrix files into modern graph formats.')
parser.add_argument("-g", "--graph", help="Choose output graph format, optional, defaults to outfile suffix", choices=['gv', 'dot', 'gml', 'graphml'])
parser.add_argument("-n", "--name", help="Name for graph")
parser.add_argument("-s", "--simple", help="Only output basic node/edge data", action='store_true')
parser.add_argument('infile', help="Source .lst file", nargs='?', type=argparse.FileType('r'), default=sys.stdin)
parser.add_argument('outfile', help="Destination graph file", nargs='?', type=argparse.FileType('w'), default=sys.stdout)

args = parser.parse_args()

graph = 'gml'
if args.graph:
    graph = args.graph
elif args.outfile.name != '<stdout>':
    basename, graph = os.path.splitext(args.outfile.name)
    graph = graph.strip('.')

graph = graph.lower()
readLst(args.infile)

old_stdout = sys.stdout
sys.stdout = args.outfile
#if (args.output):
#    sys.stdout = open(args.outfile, 'w')

if (graph == 'gv' or graph == 'dot'):
    writeGv(args.simple)
elif (graph == 'graphml'):
    writeGraphML(args.simple)
else:
    writeGml(args.simple)

#if (args.output):
sys.stdout = old_stdout
