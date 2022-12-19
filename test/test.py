import unittest
from Exercise.Ex4 import duplicate
from Exercise.Ex5 import sum_zero
from Exercise.Ex7 import formula

class TestEx4(unittest.TestCase):

    def test_ex4_case1(self):
        result = duplicate([])
        assert result == "Not Duplicate"
    
    def test_ex4_case2(self):
        result = duplicate([1,2,4,6,8,9,0,3])
        assert result == "Not Duplicate"
    
    def test_ex4_case3(self):
        result = duplicate([1,2,3,4,5,6,7,8,1])
        assert result == [1]

    def test_ex4_case4(self):
        result = duplicate([-1,-2,-2,-4,-5,-6,-7,-4,-1])
        assert result == [-1,-2,-4]


class TestEx5(unittest.TestCase):

    def test_ex5_case1(self):
        result = sum_zero([])
        assert result == []
    
    def test_ex5_case2(self):
        result = sum_zero([0,-1,2,-3,1,-2])
        assert result == [(-3,1,2),(-2,0,2),(-1,0,1)]
    
    def test_ex5_case3(self):
        result = sum_zero([0,5,4,6,3,7,2,8,1,9])
        assert result == []

    def test_ex5_case4(self):
        result = sum_zero([-6,3,5,-2,4,-1,1])
        assert result == [(-6,1,5),(-2,-1,3)]


class TestEx6(unittest.TestCase):
    pass


class TestEx7(unittest.TestCase):
    import os
    path = os.getcwd()
    
    def test_ex7_case1(self):
        file = open(self.path + "\\test\\text\\Ex7test1.txt", "r")
        contents = file.readlines()
        file.close()
        result = formula(contents)
        assert [50,150,20,70,90,40,130,30] in result

    def test_ex7_case2(self):
        file = open(self.path + "\\test\\text\\Ex7test1.txt", "r")
        contents = file.readlines()
        file.close()
        result = formula(contents)
        assert [70,130,20,90,50,150,200,140] in result

    def test_ex7_case3(self):
        file = open(self.path + "\\test\\text\\Ex7test2.txt", "r")
        contents = file.readlines()
        file.close()
        result = formula(contents)
        assert result == []

    def test_ex7_case4(self):
        file = open(self.path + "\\test\\text\\Ex7test3.txt", "r")
        contents = file.readlines()
        file.close()
        result = formula(contents)
        assert result == []
    

if __name__ == '__main__':
    unittest.main()

