import unittest
from Exercise.Ex4 import duplicate
from Exercise.Ex5 import sum_zero
from Exercise.Ex6 import sum_part_row,transpose,create_each_table,check_in_table
from Exercise.Ex7 import formula,find_x1268

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
        result = duplicate([-1,-2,-2,-2,-4,-5,-6,-2,-7,-4,-4,-1])
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
    import os
    path = os.getcwd()

    def test_ex6_func_create_each_table(self):
        file = open(self.path + "\\text\\Ex6input.txt", "r")
        contents = file.readlines()
        file.close()
        result = create_each_table(contents)
        assert result == [4,10,7,180]
    
    def test_ex6_func_sum_part_row1(self):
        result = sum_part_row([1,2,3,4,5,6,7,8,9,10],0,9)
        assert result == 55

    def test_ex6_func_sum_part_row2(self):
        result = sum_part_row([1],0,0)
        assert result == 1

    def test_ex6_func_sum_part_row3(self):
        result = sum_part_row([],0,0)
        assert result == 0

    def test_ex6_func_transpose1(self):
        result = transpose([[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4]])
        assert result == [[1,1,1,1],[2,2,2,2],[3,3,3,3],[4,4,4,4]]
    
    def test_ex6_func_transpose2(self):
        result = transpose([[1]])
        assert result == [[1]]
    
    def test_ex6_func_transpose3(self):
        result = transpose([[1,2],[1,2],[1,2]])
        assert result == [[1,1,1],[2,2,2]]

    def test_ex6_func_check_in_table1(self):
        result = check_in_table([[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4]])
        assert result == 4

    def test_ex6_func_check_in_table2(self):
        result = check_in_table([[1,3,5,7],[2,4,8,2],[6,3,1,1],[2,3,5,6]])
        assert result == 7

    def test_ex6_func_check_in_table3(self):
        result = check_in_table([[5,5],[5,5]])
        assert result == 4


class TestEx7(unittest.TestCase):
    import os
    path = os.getcwd()

    def test_ex7_find_x1268_case1(self):
        result = find_x1268([50, 150, 90, 140, 40, 30, 70, 20],200,-10)
        assert [50, 150, 30, 20] in result and [150, 50, 40, 30] in result

    def test_ex7_find_x1268_case2(self):
        result = find_x1268([50, 150, 90, 140, 40, 30, 70, 20],100,100)
        assert [30, 70, 50, 150] in result and [70, 30, 40, 140] in result

    def test_ex7_find_x1268_case3(self):
        result = find_x1268([50, 150, 90, 140, 40, 30, 70, 20],0,0)
        assert len(result) == 0
    
    def test_ex7_result_case1(self):
        file = open(self.path + "\\test\\text\\Ex7test1.txt", "r")
        contents = file.readlines()
        file.close()
        result = formula(contents)
        assert [50,150,20,70,90,40,130,30] in result

    def test_ex7_result_case2(self):
        file = open(self.path + "\\test\\text\\Ex7test1.txt", "r")
        contents = file.readlines()
        file.close()
        result = formula(contents)
        assert [70,130,20,90,50,150,200,140] in result

    def test_ex7_result_case3(self):
        file = open(self.path + "\\test\\text\\Ex7test2.txt", "r")
        contents = file.readlines()
        file.close()
        result = formula(contents)
        assert result == []

    def test_ex7_result_case4(self):
        file = open(self.path + "\\test\\text\\Ex7test3.txt", "r")
        contents = file.readlines()
        file.close()
        result = formula(contents)
        assert result == []
    

if __name__ == '__main__':
    unittest.main()

