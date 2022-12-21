def duplicate(array):#หาชุดตัวเลขซ้ำในลิสต์
    dup_item = []
    for i in range(len(array)):
        for j in range(i+1,len(array)):
            if array[i] == array[j] and not array[i] in dup_item:#เพิ่มตัวเลขที่ซ้าเข้าไปในชุดคำตอบเมื่อในชุดคำตอบไม่มีตัวเลขนี้อยู่
                dup_item.append(array[i])  
    if len(dup_item) == 0:        
        return "Not Duplicate"
    return dup_item