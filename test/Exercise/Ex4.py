def duplicate(array):
    dup_item = []
    for i in range(len(array)):
        for j in range(i+1,len(array)):
            if array[i] == array[j]:
                dup_item.append(array[i])  
    if len(dup_item) == 0:        
        return "Not Duplicate"
    return dup_item