#!/usr/bin/env python

import re
import os
from lxml import etree as ET

# process window info output
def process_wi(s):
    lines = {i.strip() for i in s.splitlines()}
    mcf = [l for l in lines if 'mCurrentFocus' in l][0]
    mfa = [l for l in lines if 'mFocusedApp' in l][0]
    mcf = re.findall(r'Window{\w+ \w+ (([^/]+)/)?([^}:]+)[}|:]', mcf)
    mfa = re.findall(r'ActivityRecord{\w+ \w+ (([^/]+)/)?([^}]+) \w+}', mfa)
    if mfa:
        mfa = mfa[0]
    else:
        mfa = ('','','')
    if mcf:
        mcf = mcf[0]
    else:
        mcf = ('','','')

    # returns mcurrentfocus app + mcurrentfocus activity +
    #         mfocusedapp app + mfocusedapp activity
    return mcf[1:]+mfa[1:]

# get all xpaths from xml (gives all elements and layers)
def get_all_xpaths(dump):
    parser = ET.XMLParser(remove_blank_text=True)
    xml = ET.XML(dump.encode('utf-8'), parser=parser)
    s = set()
    for e in xml.xpath('//*[not(*)]'):
        s.add(element_to_str(e))

    return frozenset(s)

# stringify XML node using only important information
def element_to_str(e):
    return str(e.get('class')) \
            + '#' + str(e.get('resource-id')) \
            + '%' + str(e.get('enabled')) \
            + '%' + str(e.get('focused')) \


# finds UI element that fits the smallest area of a given coordinate
def get_element_by_boundaries(xml,x,y):

    # pre-compile our regex
    bnd = re.compile('\[([-]?\d+),([-]?\d+)\]\[([-]?\d+),([-]?\d+)\]')

    # retrieve the tree
    parser = ET.XMLParser(remove_blank_text=True)
    tree = ET.XML(xml.encode('utf-8'), parser=parser)

    # set initial values for the element
    area = 9999999999
    elem = None

    # search through active leaf nodes
    for e in tree.xpath('//*[not(*) and @enabled="true"]'):

        # get bounds
        b = e.get('bounds')

        # if empty, skip
        if not b:
            continue

        # convert boundary coordinates into integers
        b = [ int(i) for i in bnd.findall(b)[0] ]

        # calculate the area
        ar = (b[2] - b[0]) * (b[3] - b[1])

        # if coordinate within boundaries and area of boundaries is smaller
        # use the element, hardcoded for now
        if x > b[0] and x < b[2] and  800-y > b[1] and 800-y < b[3] and ar < area:
            area = (b[2] - b[0]) * (b[3] - b[1])
            elem = e

    # convert element to string if not None
    if elem is not None:
        elem = element_to_str(elem)

    # return the string or None, depending if the element was found
    return elem

# --------
# OBSOLETE
# --------

# process xml dump
def process_xd(s):
    xslt = ET.fromstring(xslt_remove_attr())
    transform = ET.XSLT(xslt)
    parser = ET.XMLParser(remove_blank_text=True)
    xml = ET.XML(s.encode('utf-8'), parser=parser)
    cxml = transform(xml)
    cxml_str = ET.tostring(cxml)
    return cxml_str

def xslt_remove_attr():
    return '''
    <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
        <xsl:template match="*">
            <xsl:copy>
                <xsl:copy-of select="@class | @package | @checkable | @checked | @clickable | @enabled | @focusable | @focused | @scrollable | @long-clickable | @password | @selected" />
                <xsl:apply-templates/>
            </xsl:copy>
        </xsl:template>
        <xsl:template match="node[@class]">
            <xsl:element name="{translate(@class,'$','-')}">
                <xsl:copy-of select="@package | @checkable | @checked | @clickable | @enabled | @focusable | @focused | @scrollable | @long-clickable | @password | @selected"/>
                <xsl:apply-templates/>
            </xsl:element>
        </xsl:template>
    </xsl:stylesheet>
    '''

def xslt_remove_attr_old():
    return '''
    <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
        <xsl:template match="*">
            <xsl:copy>
                <xsl:copy-of select="@class | @package"/>
                <xsl:apply-templates/>
            </xsl:copy>
        </xsl:template>
        <xsl:template match="node[@class]">
            <xsl:element name="{translate(@class,'$','-')}">
                <xsl:copy-of select="@package"/>
                <xsl:apply-templates/>
            </xsl:element>
        </xsl:template>
    </xsl:stylesheet>
    '''
