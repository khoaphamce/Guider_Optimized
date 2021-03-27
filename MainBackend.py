import Backend
# import pandas as pd
import time
import cv2
import multiprocessing as mp


def FindPath(SP, EP):
    if (SP.upper() == EP.upper()):

        StartTime = time.time()

        PointCoord = DT.NodeToCoord(DT.NameToNode(SP.upper()))
        print(PointCoord)

        DrawMap = "ToDrawMap/ToDrawMap.jpg"
        Image = cv2.imread(DrawMap)
        CoordList = [PointCoord]
        FlagImage = cv2.imread('Items/flag.png', -1)
        Drawing = Backend.Draw(Image, CoordList, (0,0,0), True, (0,0,0))
        Image = Drawing.AddFlag(Image, FlagImage, PointCoord[1], PointCoord[0], 0.045)
        cv2.imwrite('Path.jpg', Image)

        print('DONE')
        print('')

        print(f'--------------- {time.time() - StartTime} seconds ---------------')

        return 1

    def MPNodeToCoord(NodeIndex):
            CoordList.append(DT.NodeToCoord(NodeList[NodeIndex]))

    def SavePath(Name, PathImg):
        cv2.imwrite(f'{Name}.jpg', PathImg)

    StartTime = time.time()

    SN = DT.NameToNode(SP.upper())
    if (SN == -1):
        print(f"{SP} is not the right place name.")
        return -1

    EN = DT.NameToNode(EP.upper())
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
    MarkColor = (255, 110, 0)

    CoordList = []
    for i in range(len(NodeList)):
        MPNodeToCoord(i)
        # mp1 = mp.Process(target = MPNodeToCoord, args = (i,))
        # mp1.start()
        # mp1.join()

    Drawing = Backend.Draw(Image, CoordList, LineColor, True, MarkColor)
    Image = Drawing.Path()

    mp1 = mp.Process(target=SavePath, args=("Path", Image,))
    mp1.start()

    print('DONE')
    print('')

    print(f'--------------- {time.time() - StartTime} seconds ---------------')

    return 1

#------ TEST AREA ------



# ---------- FIND PATH BY TYPING ------------
# if __name__ == '__main__':
Signal = 'y'

DT = Backend.Data('NameAndNodes.csv', 'NodesAndCoord.csv', 'NodesAndDistance.csv')
NodesAndDistance = DT.NodesDistance()
NodesAndCoord = DT.NodesCoord()
Al = Backend.Algorithm(NodesAndDistance, NodesAndCoord)

while(Signal == 'y' or Signal == 'Y'):
    SP = input("Start place: ")
    EP = input("End place: ")

    ReturnVal = FindPath(SP, EP)

    if (ReturnVal == -1):
        continue

    Signal = input("Signal: ")

#------- FAIL DETECTION --------

# ProcessCount = 0
# Name = pd.read_csv("NameAndNodes.csv");
# for i in range(len(Name["Name"])):
#     SP = Name["Name"][i]
#     for j in range(i):
#         if (i == j): continue
#         EP = Name["Name"][j]
#         ProcessCount += 1
#         if ProcessCount <= 5:
#             mp1 = mp.Process(target = FindPath, args = (SP, EP))
#             mp1.start()
#         else:
#             mp1.join()
#             mp1 = mp.Process(target = FindPath, args = (SP, EP))
#             mp1.start()
#             ProcessCount = 0
#         # ReturnVal = FindPath(SP, EP)
        # if (ReturnVal == -1):
        #     print(f"Failed to find path from {SP} to {EP}")
# mp1.join()