import os
path = os.getcwd()

def sum_part_row(row_list,start_index,stop_index):
    result = 0
    # print(row_list[start_index:length],end=' ')
    if len(row_list) == 0:
        return 0
    for i in range(start_index,stop_index+1):
        result += row_list[i]
    # print(result)
    return result

def transpose(matrix):
    table = [[tmp_row[tmp_i] for tmp_row in matrix] for tmp_i in range(len(matrix[0]))]
    return(table)

def create_each_table(data):
    table_number = int(data[0])
    line_read = 1
    result = []
    for i in range(table_number):  
        table = []
        table_size = int(data[line_read])
        line_read += 1
        for j in range(table_size):
            table.append([int(n)for n in data[line_read].split()])
            line_read += 1
        result.append(check_in_table(table))
    return result
    
def check_in_table(matrix):
    catch_ten = 0
    for num in range(2):
        if num == 1:
            matrix = transpose(matrix)#transpose table
        for row in matrix:# access in each row
            if sum_part_row(row,0,len(matrix)-1) < 10:
                continue
            for index in range(len(row)-1):# first index for sum
                for width in range(index+1,len(matrix)):# last index for sum and more than 1 size of table
                    if sum_part_row(row,index,width) == 10 :
                        catch_ten += 1
    return catch_ten
    
    # for j in range(table_size):
    #     table.append([int(n)for n in contents[line_read].split()])
    #     line_read += 1
    # for num in range(2):
    #     if num == 1:
    #         table = transpose(table)#transpose table
    #     for row in table:# access in each row
    #         if sum_part_row(row,0,table_size) < 10:
    #             continue
    #         for index in range(len(row)-1):# first index for sum
    #             for width in range(index+1,table_size+1):# last index for sum and more than 1 size of table
    #                 if sum_part_row(row,index,width) == 10 :
    #                     catch_ten += 1
    # print(catch_ten)
    