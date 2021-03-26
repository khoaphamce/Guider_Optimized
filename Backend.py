from queue import PriorityQueue
import pandas as pd
from math import sqrt
import cv2
import time
import json
import numpy as np


class Data:
    def __init__(self, NameAndNodes, NodesAndCoord, NodesAndDistance):
        self.NameAndNodes = NameAndNodes
        self.NodesAndCoord = NodesAndCoord
        self.NodesAndDistance = NodesAndDistance

    def NameNodes(self):
        ReturnValue = pd.read_csv(self.NameAndNodes)
        return ReturnValue
          
    def NodesCoord(self):
        ReturnValue = pd.read_csv(self.NodesAndCoord)
        return ReturnValue

    def NodesDistance(self):
        ReturnValue = pd.read_csv(self.NodesAndDistance)
        return ReturnValue

    def NodeToCoord(self, Node):
        CoordData = self.NodesCoord()
        CoordX = CoordData['X'][Node]
        CoordY = CoordData['Y'][Node]
        Coord = (CoordX, CoordY)
        return Coord

    def GetIndex(self, Arr, Value):
        for i in range(len(Arr)):
            if Value == Arr[i]:
                return i
        return -1

    def NameToNode(self, Name):
        NodeData = self.NameNodes()
        Ind = self.GetIndex(NodeData['Name'], Name)

        if(Ind != -1):
            return int(NodeData['Node'][Ind])-1
        else:
            return -1


class Algorithm:
    def __init__ (self, Graph, NodesAndCoord, NodeDistance, GDist, FDist):
        self.Graph = Graph
        self.NodesAndCoord = NodesAndCoord
        self.NodeDistance = NodeDistance
        self.GDist = GDist
        self.FDist = FDist


    def Euclidean(self, P1, P2):
        X1 = int(self.NodesAndCoord['X'][P1])
        Y1 = int(self.NodesAndCoord['Y'][P1])
        X2 = int(self.NodesAndCoord['X'][P2])
        Y2 = int(self.NodesAndCoord['Y'][P2])

        return sqrt((X1-X2)*(X1-X2) + (Y1-Y2)*(Y1-Y2))


    def AStar(self, StartNode, EndNode):
        StartTimeLoop = time.time()

        self.StartNode = StartNode
        self.EndNode = EndNode

        PriCount = 0
        OpenSet = PriorityQueue()
        OpenSet.put((0, PriCount, self.StartNode))
        CameFrom = {}
        Path = []

        self.GDist[self.StartNode] = 0
        self.FDist[self.StartNode] = self.Euclidean(self.StartNode, self.EndNode)


        OpenSetHash = {self.StartNode}

        while not OpenSet.empty() > 0:
            Current = OpenSet.get()[2]
            OpenSetHash.remove(Current)

            if Current == self.EndNode:
                print('found path')
                Path.append(self.EndNode)
                Current = CameFrom[Current]
                Path.append(Current)
                while Current in CameFrom:
                    Current = CameFrom[Current]
                    Path.append(Current)

                return Path

            for Neighbor in range(len(self.NodeDistance[Current])):
                Distance = self.NodeDistance[Current][Neighbor]
                if Distance > 0:

                    TempG = self.GDist[Current] + Distance
                    
                    if TempG < self.GDist[Neighbor]:
                        self.GDist[Neighbor] = TempG
                        self.FDist[Neighbor] = TempG + self.Euclidean(Neighbor, self.EndNode)
                        
                        CameFrom[Neighbor] = Current
                        if Neighbor not in OpenSetHash:
                            PriCount += 1
                            OpenSet.put((FDist[Neighbor], PriCount, Neighbor))
                            OpenSetHash.add(Neighbor)

        # JsonSaveFile = open(f'cache/{self.StartNode}_{self.EndNode}_Fail.json', 'w')
        # print('')

        return -1   


class Draw:
    def __init__ (self, Image, NodeList, Color, MarkOption, MarkColor):
        self.Image = Image
        self.Color = Color
        self.NodeList = NodeList

        self.PathOnlyColor = [0,0,0,0]

        for i in range(3):
            self.PathOnlyColor[i] = Color[i]
        self.PathOnlyColor[3] = 255

        self.PathMarkerColor = [0,0,0,0]

        for i in range(3):
            self.PathMarkerColor[i] = MarkColor[i]
        self.PathMarkerColor[3] = 255

        if MarkOption:
            self.MarkOption = MarkOption
        else:
            self.MarkOption = False
        if MarkColor:
            self.MarkColor = MarkColor
        else:
            self.MarkColor = (0,0,0)

    def Path(self):
        ReturnImage = self.Image
        Thickness = int(0.005*sqrt(ReturnImage.shape[0]*ReturnImage.shape[0] + ReturnImage.shape[1]*ReturnImage.shape[1]))
        # Thickness = 200\
        
        for i in range(len(self.NodeList)-1):
            P1 = (self.NodeList[i][1], self.NodeList[i][0])
            P2 = (self.NodeList[i+1][1], self.NodeList[i+1][0])
            ReturnImage = cv2.line(ReturnImage, P1, P2, self.PathOnlyColor, Thickness)
        
        if self.MarkOption == True:
            P1 = (self.NodeList[0][1], self.NodeList[0][0])
            Radius = int(round(Thickness*0.5, 0))
            MarkThickness = int(round(Radius*1.8, 0))
            ReturnImage = cv2.circle(ReturnImage, P1, Radius, self.MarkColor, MarkThickness)
            ReturnImage = cv2.circle(ReturnImage, P2, Radius, self.MarkColor, MarkThickness)
        
        return ReturnImage


#------------- MAIN FUNCTION - CALL THIS FUNCTION WHEN USER INPUT PLACE------

DT = Data('NameAndNodes.csv', 'NodesAndCoord.csv', 'NodesAndDistance.csv')
NodesAndDistance = DT.NodesDistance()
NodesAndCoord = DT.NodesCoord()
NameAndNodes = DT.NameNodes()


GDist = {}
FDist = {}


NodeDistanceTemp = []
NodeDistance = []

for Node_1 in NodesAndCoord['Node']:
    GDist[int(Node_1)] = float('inf')
    FDist[int(Node_1)] = float('inf')
    for Node_2 in NodesAndCoord['Node']:
        NodeDistanceTemp.append(0)
    NodeDistance.append(NodeDistanceTemp)
    NodeDistanceTemp = []


for i in range(len(NodesAndDistance['Distance'])):
    Node_1 = NodesAndDistance['Node_1'][i]
    Node_2 = NodesAndDistance['Node_2'][i]
    GraphDist = NodesAndDistance['Distance'][i]
    if Node_1 != Node_2:
        NodeDistance[int(Node_1)][int(Node_2)] = GraphDist
        NodeDistance[int(Node_2)][int(Node_1)] = GraphDist

Al = Algorithm(NodesAndDistance, NodesAndCoord, NodeDistance, GDist, FDist)

def FindPath(SP, EP):
    
    def MPNodeToCoord(NodeIndex):
        CoordList.append(DT.NodeToCoord(NodeList[NodeIndex]))

    StartTime = time.time()

    SN = DT.NameToNode(SP)
    if (SN == -1):
        print(f"{SP} is not the right place name.")
        return -1

    EN = DT.NameToNode(EP)
    if (EN == -1):
        print(f"{EP} is not the right place name.")
        return -1

    NodeList = Al.AStar(SN, EN)

    if (NodeList == -1):
        print("Some error occured, try again")
        return -1

    DrawMap = 'ToDrawMap/ToDrawMap.jpg'
    Image = cv2.imread(DrawMap)
    LineColor = (0, 50, 200)
    MarkColor = (237, 89, 147)

    CoordList = []
    for i in range(len(NodeList)):
        MPNodeToCoord(i)
        # mp1 = mp.Process(target = MPNodeToCoord, args = (i,))
        # mp1.start()
        # mp1.join()

    Drawing = Draw(Image, CoordList, LineColor, True, MarkColor)
    Image = Drawing.Path()

    cv2.imwrite('Path.jpg', Image)

    print('DONE')
    print('')

    print(f'--------------- {time.time() - StartTime} seconds ---------------')

    return 1