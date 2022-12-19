def duplicate(array):
    check = False
    for i in range(len(array)):
        for j in range(i+1,len(array)):
            if array[i] == array[j]:
                check = True
                break   
        if check:
            return "Duplicate"          
    return "Not Duplicate"