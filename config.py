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
GlobalImage = cv2.imread("ToDrawMap/EmptyMap.jpg")

Dpn = NameAndNodes["Node"][DT.GetIndex(NameAndNodes["Name"], DEFAULT_PLACE)] - 1

Dpc = DT.NodeToCoord(Dpn)

YouAreHereImg = cv2.imread("Items/YouAreHere.png", -1)

GlobalImage = Backend.AddHere(x = int(Dpc[1]), y = int(Dpc[0]), background_img = GlobalImage.copy(), img_to_overlay_t = YouAreHereImg, Ratio = 0.07)

# Backend.Draw().AddFlag(x = int(Dpc[0]), y = int(Dpc[1]), background_img = GlobalImage, img_to_overlay_t = YouAreHereImg, Ratio = 0.045)