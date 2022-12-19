def formula(files):
    A = set()
    c1 = 0
    c2 = 0

    for i in range(len(files)):
        if i == 0:
            c1 = int(files[i].split(" ")[1])
            c2 = int(files[i].split(" ")[2])
        else:
            A.add(int(files[i]))

    a = sorted(list(A)) 
    x12 = []
    x68 = []
    x1268 = []  

    for i in range(0, len(a)-1):
        for j in range(i+1, len(a)):
            if a[j] + a[i] == c1:
                x12.append([a[i],a[j]])
                x12.append([a[j],a[i]])
            if c2 < 0:
                if a[i] - a[j] == c2:
                    x68.append([a[j],a[i]])
            elif c2 >= 0:
                if a[j] - a[i] == c2:
                    x68.append([a[i],a[j]])
    for i in x12:
        for j in x68:
            if not (i[0] in j or i[1] in j):
                x1268.append([i[0],i[1],j[0],j[1]])

    x = {}
    x_key_value = []
    for i in x1268:
        x.update({
            "x1":i[0],
            "x2":i[1],
            "x6":i[2],
            "x8":i[3]
        })
        remain = sorted(list((set(a)-set(i))))#list without x1 x2 x6 x8
        for j in range(0, len(remain)-1):
            for k in range(j+1, len(remain)):
                if remain[k] - remain[j] == x["x1"]:
                    x.update({
                        "x3":remain[j],
                        "x4":remain[k]
                    })
                    remain2 = sorted(list((set(remain)-set([remain[k],remain[j]]))))#list without x1 x2 x6 x8 x3 x4
                    for l in range(0, len(remain2)-1):
                        for m in range(l+1, len(remain2)):
                            if remain2[m] - remain2[l] == x["x6"]:
                                x.update({
                                    "x5":remain2[l],
                                    "x7":remain2[m]
                                })
                                x_key_value.append(sorted(x.items()))
    results = []
    result = []

    for i in x_key_value:
        for j in i:
            result.append(j[1])
        results.append(result)
        result = []
    return results
