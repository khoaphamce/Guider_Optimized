import Backend

Signal = 'y'

while(Signal == 'y' or Signal == 'Y'):
    SP = input("Start place: ")
    EP = input("End place: ")

    ReturnVal = Backend.FindPath(SP, EP)

    if (ReturnVal == -1):
        continue
    
    Signal = input("Signal: ")