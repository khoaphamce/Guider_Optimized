import pandas as pd
import Backend
import cv2
import csv

DT = Backend.Data('NameAndNodes.csv', 'NodesAndCoord.csv', 'NodesAndDistance.csv')
NameAndNodes = DT.NameNodes()
descript_list = []
des_len = len(NameAndNodes["Name"])
descript_list = [[str(i+1), NameAndNodes["Name"][i]] for i in range(0, des_len)]
descript_list.insert(0, ["no", "place"])

with open("description.csv", mode='w') as csv_file:
    writer = csv.writer(csv_file)
    # writer.writeheader()
    
    writer.writerows(descript_list)
    
    csv_file.close()

data = pd.read_csv('description.csv')
BUILDING_LIST = tuple(list(data['place'])) 
NodesAndDistance = DT.NodesDistance()
NodesAndCoord = DT.NodesCoord()
Al = Backend.Algorithm(NodesAndDistance, NodesAndCoord)
LineColor = (0, 50, 200)
MarkColor = (255, 110, 0)
GlobalImage = cv2.imread("ToDrawMap/ToDrawMap.jpg")