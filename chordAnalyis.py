# -*- coding: utf-8 -*-
"""
Created on Fri May  2 11:02:49 2014

@author: cuaras
"""
import os
import glob
import json
import operator

#Hacer pruebas para comprobar que quedó bien, aunque parece que si

class Chord:
    pass

class ChordTable:
    
    def setChords(self, gtChord, chord):
    #Input chords as strings
        if gtChord not in self.chordTable.keys():
            self.chordTable[gtChord] = {}
        if chord not in self.chordTable[gtChord].keys():
            self.chordTable[gtChord][chord] = 0
        self.chordTable[gtChord][chord] += 1
    
    def mergeTable(self, table):
        for gtChord in table.keys():
            if gtChord not in self.chordTable:
                self.chordTable[gtChord] = {}
            for chord in table[gtChord].keys():
                if chord not in self.chordTable[gtChord]:
                    self.chordTable[gtChord][chord] = 0
                self.chordTable[gtChord][chord] += table[gtChord][chord]
            
    
    def __init__(self, filename= None):
    #Load a Chord table from a json file if specified
        self.chordTable = {}
        self.chordTable.clear()
        if filename != None:        
            with open(filename, 'r') as f:    
                self.chordTable = json.load(f)
    
def parseChords(filename):
#Opens a mirex chord file and returns a list with chord objects
    song = []
    with open(filename, 'r') as f:
        for line in f:
            #Intentar con separadores ' ' y '\t' 
            try:            
                start, end, label = line.strip().split('\t')
            except:
                try:
                    start, end, label = line.split(' ')
                except:
                    print 'error'
            label = label.strip('\n')       #Quitar End carriage
            chord = Chord()
            chord.start = float(start)
            chord.end = float(end)
            chord.label = label
            song.append(chord)
    return song

def processSong(gtSong, song):
    idx = 0
    chordTable = ChordTable()
    chordTable.chordTable.clear()
    #Avanza los dos cuando hay que cambiar chord
    for chord in song:
        isGreater = True
        while isGreater:
            #print chord.start, chord.end, gtSong[idx].start, gtSong[idx].end
            #Si la intersección es mayor a 75 ms
            if min(chord.end, gtSong[idx].end) - max(chord.start, gtSong[idx].start) > .075:
                chordTable.setChords(gtSong[idx].label, chord.label)
            isGreater = chord.end > gtSong[idx].end
            if isGreater: 
                idx += 1 #Aumentar el indice para gt
                isGreater = False if idx >= len(gtSong) else True
    return chordTable

def analyseChords():
    #Analyze chords vs ground truth and generate json files per song
    baseFolder = '../outputs/billboard2012/BillboardTest2012/'
    subDirs = os.walk(baseFolder).next()[1]
    subDirs.remove('Ground-truth')    
    
    for gtFilename in glob.glob(baseFolder+'Ground-truth/*.lab'):
        print gtFilename
        baseFilename = gtFilename.split('/')[-1][:-3]+'wav.txt' #Filename in txt without directory
        gtSong = parseChords(gtFilename)     
        for folder in subDirs:
            filename = baseFolder + folder + '/' + baseFilename
            song = parseChords(filename)
            chordTable = processSong(gtSong, song)
            with open(filename[:-3]+'json', 'w') as f:
                j = json.dumps(chordTable.chordTable)
                print >> f, j

def mergeAllSongs():
    baseFolder = '../outputs/billboard2012/BillboardTest2012/'
    allChords = ChordTable()
    for filename in glob.iglob(os.path.join(baseFolder, '*', '*.json')):
        tmp = ChordTable(filename)
        allChords.mergeTable(tmp.chordTable)
    with open('allChords.json', 'w') as f:
        j = json.dumps(allChords.chordTable)
        print >> f, j
        
def topXtopY(chordTable, x, y):
    #Return a dictionary trimmed to top X gtChords and top Y chords from a chordTable
    sortedTable = ChordTable()    
    topX = countByChord(chordTable)[:x]
    
    for i in range(len(topX)):      #Iterate through gtChords
        gtKey = topX[i][0]          #get key
        sortedTable.chordTable[gtKey] = {}
        topY = sorted(chordTable[gtKey].iteritems(), 
                                 key = operator.itemgetter(1), reverse = True)
        topY = topY[:y]
        for i in range(len(topY)):  #Read top chord tags and iterate
            chordKey = topY[i][0]
            sortedTable.chordTable[gtKey][chordKey] = chordTable[gtKey][chordKey]
    return sortedTable
    
def countByChord(chordTable):
    counter = 0
    allGT = dict()
    for gtChord in chordTable.keys():
        for chord in chordTable[gtChord]:
            counter += chordTable[gtChord][chord]
        allGT[gtChord] = counter
        counter = 0
    allGT = sorted(allGT.iteritems(), key = operator.itemgetter(1),
                   reverse = True)
    return allGT
            
if __name__ == "__main__":
    song1 = parseChords('../outputs/billboard2012/BillboardTest2012/Ground-truth/1002.lab')
    song2 = parseChords('../outputs/billboard2012/BillboardTest2012/CF2/1002.wav.txt')
    a = ChordTable()
    b = ChordTable()
    a.setChords('a', 'a')
    a.setChords('a', 'b')
    a.setChords('b', 'b')
    b.setChords('b', 'a')
    b.setChords('b', 'b')
    b.setChords('c', 'a')

        