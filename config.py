import pandas as pd
import Backend
import cv2

data = pd.read_csv('NameAndNodes.csv', encoding = "utf8")
BUILDING_LIST = sorted(tuple(list(data['Name']))) 
DEFAULT_PLACE = 'CONG LY THUONG KIET'
DT = Backend.Data('NameAndNodes.csv', 'NodesAndCoord.csv', 'NodesAndDistance.csv')
NameAndNodes = DT.NameNodes()
NodesAndDistance = DT.NodesDistance()
NodesAndCoord = DT.NodesCoord()
Al = Backend.Algorithm(NodesAndDistance, NodesAndCoord)
LineColor = (0, 50, 200)
MarkColor = (255, 110, 0)
GlobalImage = cv2.imread("ToDrawMap/ToDrawMap.jpg")