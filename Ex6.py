def sum_part_row(row_list,start_index,stop_index):
    result = 0
    # print(row_list[start_index:length],end=' ')
    for i in range(start_index,stop_index):
        result += row_list[i]
    # print(result)
    return result

def transpose(matrix):
    table = [[tmp_row[tmp_i] for tmp_row in matrix] for tmp_i in range(len(matrix))]
    return(table)

def check_in_row(vector):
    for row in vector:# access in each row
            if sum_part_row(row,0,len(vector)) < 10:
                continue
            for index in range(len(row)-1):# first index for sum
                for width in range(index+1,len(vector+1):# last index for sum and more than 1 size of table
                    if sum_part_row(row,index,width) == 10 :
                        catch_ten += 1

file = open("Ex6.txt", "r")
contents = file.readlines()
file.close()

table_number = int(contents[0])
line_read = 1
for i in range(table_number):
    table_size = int(contents[line_read])
    line_read += 1
    table = []
    catch_ten = 0
    for j in range(table_size):
        table.append([int(n)for n in contents[line_read].split()])
        line_read += 1
    for num in range(2):
        if num == 1:
            table = transpose(table)#transpose table
        for row in table:# access in each row
            if sum_part_row(row,0,table_size) < 10:
                continue
            for index in range(len(row)-1):# first index for sum
                for width in range(index+1,table_size+1):# last index for sum and more than 1 size of table
                    if sum_part_row(row,index,width) == 10 :
                        catch_ten += 1
    print(catch_ten)
    