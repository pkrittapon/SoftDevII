def plane(n):
    if n == 0:
        return 1
    return plane(n-1) + n

plane(3)