import unittest

class TestDuplicate(unittest.TestCase):

    def test_ex4_case1(self):
        result = sum_zero([])
        assert result == []
    
    def test_ex4_case2(self):
        result = sum_zero([-3,2,-1,0,2,-2])
        assert result == [(-3,1,2),(-2,0,2),(-1,0,1)]
    
    def test_ex4_case3(self):
        result = sum_zero([0,5,4,6,3,7,2,8,1,9])
        assert result == []

    def test_ex4_case4(self):
        result = sum_zero([-6,3,5,-2,4,-1,1])
        assert result == [(-6,1,5),(-2,-1,3)]

def sum_zero(a):
    n = len(a)
    triplets = []

    for i in range(n):
        for j in range(0, n-i-1):
            if a[j] > a[j+1]:
                a[j], a[j+1] = a[j+1], a[j]

    for i in range(n - 2):
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


if __name__ == '__main__':
    unittest.main()