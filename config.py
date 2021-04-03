import pandas as pd
import Backend
import cv2

data = pd.read_csv('description.csv')
BUILDING_LIST = tuple(list(data['place'])) 
DT = Backend.Data('NameAndNodes.csv', 'NodesAndCoord.csv', 'NodesAndDistance.csv')
NodesAndDistance = DT.NodesDistance()
NodesAndCoord = DT.NodesCoord()
Al = Backend.Algorithm(NodesAndDistance, NodesAndCoord)
LineColor = (0, 50, 200)
MarkColor = (255, 110, 0)
GlobalImage = cv2.imread("ToDrawMap/ToDrawMap.jpg")