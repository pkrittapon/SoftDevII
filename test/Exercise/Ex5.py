def sum_zero(a):#ใช้หาชุดของตัวเลข3ตัวที่ผลรวมเป็น0
    n = len(a)
    triplets = []

    for i in range(n):#sorted data
        for j in range(0, n-i-1):
            if a[j] > a[j+1]:
                a[j], a[j+1] = a[j+1], a[j]

    for i in range(n - 2):#หาชุดของตัวเลข3ตัวที่ผลรวมเป็น0
        low = i + 1 
        high = n - 1
        while low < high:
            if a[low] + a[high] + a[i] < 0:
                low += 1
            elif a[low] + a[high] + a[i] > 0:
                high -= 1
            else:
                triplets.append((a[i], a[low], a[high]))
                low += 1
                high -= 1
    return triplets