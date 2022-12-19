def duplicate(array):
    for i in range(len(array)):
        for j in range(i+1,len(array)):
            if array[i] == array[j]:
                return "Duplicate"          
    return "Not Duplicate"