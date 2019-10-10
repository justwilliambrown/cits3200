#lab4
#1
'''a="myprogram.exe"
b=a[5:9]
c=a[0:9]'''
#2 Caesar cipher
'''m=input("please in put the code\n\r")
m=m.replace(" ","")
list(m)
c=""
for n,j in enumerate(range(26)):
    for i in m:
        unicode=ord(i)+j
        if ord('z')-unicode>=0:
            c+=chr(unicode)
        else:
            c+=chr(ord('a')-ord('z')+unicode-1)
    print(n,c)
    c=""'''
#3 decimal->octal
'''number=int(input("please input a number\n\r"))
print (oct(number))
ten=""
while(int(number/8)):
    ten=str(number%8)+ten
    number=int(number/8)
ten=str(number)+ten
print(ten)'''
#3' octal->decimal
'''ten=list(ten)
octal=0
for i in range(len(ten)):
    octal=int(ten[i])*8**(len(ten)-i-1)+octal
print(octal)'''


#4
'''str_test="Python rules!"
list_str=list(str_test)
str_test=str_test.upper()
f=str_test.find("RULES")
str_test=str_test.replace("!","?")
print(str_test)'''

#5 file

'''file_test=open("test.txt",mode='a')
file_test.write("hello world")
file_test.close()'''

#6 bit shift

'''direction=input("please input the direction l\r /r/n")
bio=str(input("please input a binary number"))
bias=input("please input the bias")'''

#8
import os
#print(os.walk(top="/."))
import os
for root, dirs, files in os.walk(".", topdown=False):
    for name in files:
        print(os.path.join(root, name))
    for name in dirs:
        print(os.path.join(root, name))


