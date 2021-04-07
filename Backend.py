from queue import PriorityQueue
import pandas as pd
from math import sqrt
import cv2
import time
import json
import numpy as np
import dropbox
import qrcode


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
            FoundVal = str(NodeData["Node"][Ind])
            if (FoundVal != "nan"):
                return int(float(FoundVal)) - 1
            else:
                return self.NameToNode(str(NodeData["Label"][Ind]))
        else:
            return -1

class Algorithm:
    def __init__ (self, Graph, NodesAndCoord):
        self.Graph = Graph
        self.NodesAndCoord = NodesAndCoord

        DT = Data('NameAndNodes.csv', 'NodesAndCoord.csv', 'NodesAndDistance.csv')
        NodesAndDistance = DT.NodesDistance()
        NodesAndCoord = DT.NodesCoord()
        NameAndNodes = DT.NameNodes()

        self.NodeDistance_Main = []
        NodeDistanceTemp_Main = []
        self.GDist_Main = {}
        self.FDist_Main = {}

        for Node_1 in NodesAndCoord['Node']:
            self.GDist_Main[int(Node_1)] = float('inf')
            self.FDist_Main[int(Node_1)] = float('inf')
            for Node_2 in NodesAndCoord['Node']:
                NodeDistanceTemp_Main.append(0)
            self.NodeDistance_Main.append(NodeDistanceTemp_Main)
            NodeDistanceTemp_Main = []


        for i in range(len(NodesAndDistance['Distance'])):
            Node_1 = NodesAndDistance['Node_1'][i]
            Node_2 = NodesAndDistance['Node_2'][i]
            GraphDist = NodesAndDistance['Distance'][i]
            if Node_1 != Node_2:
                self.NodeDistance_Main[int(Node_1)][int(Node_2)] = GraphDist
                self.NodeDistance_Main[int(Node_2)][int(Node_1)] = GraphDist

        

    def Euclidean(self, P1, P2):
        X1 = int(self.NodesAndCoord['X'][P1])
        Y1 = int(self.NodesAndCoord['Y'][P1])
        X2 = int(self.NodesAndCoord['X'][P2])
        Y2 = int(self.NodesAndCoord['Y'][P2])

        return sqrt((X1-X2)*(X1-X2) + (Y1-Y2)*(Y1-Y2))


    def AStar(self, StartNode, EndNode):

        GDist_AStar = self.GDist_Main.copy()
        FDist_AStar = self.FDist_Main.copy()
        NodeDistance_AStar = self.NodeDistance_Main.copy()

        self.StartNode = StartNode
        self.EndNode = EndNode
    
        PriCount = 0
        OpenSet = PriorityQueue()
        OpenSet.put((0, PriCount, self.StartNode))
        CameFrom = {}
        Path = []

        GDist_AStar[self.StartNode] = 0
        FDist_AStar[self.StartNode] = self.Euclidean(self.StartNode, self.EndNode)

        OpenSetHash = {self.StartNode}

        while not OpenSet.empty() > 0:
            Current = OpenSet.get()[2]
            OpenSetHash.remove(Current)

            if Current == self.EndNode:
                print('Found path')
                Path.append(self.EndNode)
                Current = CameFrom[Current]
                Path.append(Current)
                while Current in CameFrom:
                    Current = CameFrom[Current]
                    Path.append(Current)
                
                return Path

            for Neighbor in range(len(NodeDistance_AStar[Current])):
                Distance = NodeDistance_AStar[Current][Neighbor]
                if Distance > 0:

                    TempG = GDist_AStar[Current] + Distance
                    
                    if TempG < GDist_AStar[Neighbor]:
                        GDist_AStar[Neighbor] = TempG
                        FDist_AStar[Neighbor] = TempG + self.Euclidean(Neighbor, self.EndNode)
                        
                        CameFrom[Neighbor] = Current
                        if Neighbor not in OpenSetHash:
                            PriCount += 1
                            OpenSet.put((FDist_AStar[Neighbor], PriCount, Neighbor))
                            OpenSetHash.add(Neighbor)
        
        return -1   


class Draw:
    def __init__ (self, Image, NodeList, Color, MarkOption, MarkColor):
        self.Image = Image
        self.Color = Color
        self.NodeList = NodeList

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


    def AddFlag(self, background_img, img_to_overlay_t, x, y, Ratio):

        bg_img = background_img.copy()
        
        bgWidth = background_img.shape[0]
        bgHeight = background_img.shape[1]

        frWidth = img_to_overlay_t.shape[0]
        frHeight = img_to_overlay_t.shape[1]

        if (frHeight >= frWidth):
            if (frHeight > bgHeight*Ratio):
                temp = frHeight
                frHeight = int(bgHeight*Ratio)
                frWidth = int(temp*1.0/frWidth * (bgHeight*Ratio)) 
        else:
            if (frWidth > bgWidth*Ratio):
                temp = frWidth
                frWidth = int(bgWidth*Ratio)
                frHeight = int(temp*1.0/frHeight * (bgWidth*Ratio)) 

        img_to_overlay_t = cv2.resize(img_to_overlay_t, (frWidth, frHeight))

        b,g,r,a = cv2.split(img_to_overlay_t)
        overlay_color = cv2.merge((b,g,r))
        
        mask = cv2.medianBlur(a,5)
        
        h, w, _ = overlay_color.shape
        
        roi = bg_img[max(y- int(h*0.5 + h*0.5), 0):y+int(h - h*0.5 - h*0.5), max(x - int(w*0.5), 0):x+int(w - w*0.5)]
        # Black-out the area behind the logo in our original ROI
        img1_bg = cv2.bitwise_and(roi.copy(),roi.copy(),mask = cv2.bitwise_not(mask))
        
        # Mask out the logo from the logo image.
        img2_fg = cv2.bitwise_and(overlay_color,overlay_color,mask = mask)

        # Update the original image with our new ROI
        bg_img[max(y- int(h*0.5 + h*0.5), 0):y+int(h - h*0.5 - h*0.5), max(x - int(w*0.5), 0):x+int(w - w*0.5)] = cv2.add(img1_bg, img2_fg)

        return bg_img


    def Path(self):
        ReturnImage = self.Image
        Thickness = int(0.005*sqrt(ReturnImage.shape[0]*ReturnImage.shape[0] + ReturnImage.shape[1]*ReturnImage.shape[1]))
        # Thickness = 200\
        
        for i in range(len(self.NodeList)-1):
            P1 = (self.NodeList[i][1], self.NodeList[i][0])
            P2 = (self.NodeList[i+1][1], self.NodeList[i+1][0])
            ReturnImage = cv2.line(ReturnImage, P1, P2, self.Color, Thickness)
        
        if self.MarkOption == True:
            P1 = (self.NodeList[0][1], self.NodeList[0][0])
            Radius = int(round(Thickness*0.7, 0))
            FlagImg = cv2.imread("Items/flag.png", -1)
            MarkThickness = int(round(Radius*1.85, 0))

            ReturnImage = cv2.circle(ReturnImage, P2, Radius, self.MarkColor, MarkThickness)

            ReturnImage = self.AddFlag(ReturnImage, FlagImg, P1[0], P1[1], 0.045)

        return ReturnImage


class Internet():

    def __init__ (self, LocalFileName):
        self.LocalFileName = LocalFileName
        self.Token = "j1aEZ3CCdtsAAAAAAAAAAbD9EPm35AhRDtdf3_4oS5XlqyBpcXgk-lj1PjFV4-Xe"
        self.dbx = dropbox.Dropbox(self.Token)

    def Upload(self, SP, EP):
        FileLocation = f"/Path/{SP}_{EP}.jpg"

        # FileExist = self.dbx.drop_exists(path = FileLocation, dtoken = get_dropbox_token())

        # if (FileExist == True):
        with open(self.LocalFileName, 'rb') as UploadFile:
            self.dbx.files_upload(UploadFile.read(), FileLocation, mode = dropbox.files.WriteMode.overwrite)
        try:
            URL = str(self.dbx.sharing_create_shared_link_with_settings(FileLocation).url)
        except:
            URL = str(self.dbx.sharing_get_shared_links(FileLocation).links[0].url)
            print(URL)
        
        URL.replace("dl=0", "dl=1")
        URL = list(URL)
        URL[len(URL) - 1] = '1'
        URL = "".join(URL)

        QrImage = qrcode.make(URL)
        QrImage = QrImage.convert("RGB")

        return QrImage
            

#------------- MAIN FUNCTION - CALL THIS FUNCTION WHEN USER INPUT PLACE------



# def FindPath(SP, EP):
    
#     def MPNodeToCoord(NodeIndex):
#         CoordList.append(DT.NodeToCoord(NodeList[NodeIndex]))

#     StartTime = time.time()

#     SN = DT.NameToNode(SP)
#     if (SN == -1):
#         print(f"{SP} is not the right place name.")
#         return -1

#     EN = DT.NameToNode(EP)
#     if (EN == -1):
#         print(f"{EP} is not the right place name.")
#         return -1

#     Al = Algorithm(NodesAndDistance, NodesAndCoord)

#     print(GDist_Main)
#     print(FDist_Main)

#     GDist_Pass = GDist_Main
#     FDist_Pass = FDist_Main
#     NodeDistance_Pass = NodeDistance_Main

#     NodeList = Al.AStar(SN, EN, NodeDistance_Pass, GDist_Pass, FDist_Pass)

#     if (NodeList == -1):
#         print("Some error occured, try again")
#         return -1

#     DrawMap = 'ToDrawMap/ToDrawMap.jpg'
#     Image = cv2.imread(DrawMap)
#     LineColor = (0, 50, 200)
#     MarkColor = (237, 89, 147)

#     CoordList = []
#     for i in range(len(NodeList)):
#         MPNodeToCoord(i)
#         # mp1 = mp.Process(target = MPNodeToCoord, args = (i,))
#         # mp1.start()
#         # mp1.join()

#     Drawing = Draw(Image, CoordList, LineColor, True, MarkColor)
#     Image = Drawing.Path()

#     cv2.imwrite('Path.jpg', Image)

#     print('DONE')
#     print('')

#     print(f'--------------- {time.time() - StartTime} seconds ---------------')

#     return 1