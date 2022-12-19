import unittest

class TestDuplicate(unittest.TestCase):

    def test_ex4_case1(self):
        result = duplicate([])
        assert result == "Not Duplicate"
    
    def test_ex4_case2(self):
        result = duplicate([1,2,4,6,8,9,0,3])
        assert result == "Not Duplicate"
    
    def test_ex4_case3(self):
        result = duplicate([1,2,3,4,5,6,7,8,1])
        assert result == "Duplicate"

    def test_ex4_case4(self):
        result = duplicate([-1,-2,-3,-4,-5,-6,-7,-8,-1])
        assert result == "Duplicate"

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


if __name__ == '__main__':
    unittest.main()