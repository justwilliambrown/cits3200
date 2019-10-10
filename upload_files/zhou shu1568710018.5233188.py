#lab1&lab2
from graphics import *
import math
import time

'''def main():
    win = GraphWin("My Circle", 1000, 1000)
    x=int(input("please input the coordinate of x of center\r\n"))
    y=int(input("please input the coordinate of y of center\r\n"))
    r=int(input("please input the radius of center\r\n"))

    c = Circle(Point(x,y), r)
    c.draw(win)
    l=round(math.pi*2*r,2)
    s=round(math.pi*r**2,2)
    Text(Point(x+50,y+50), "perimeter:"+str(l)).draw(win)
    Text(Point(x+100,y+100), "area:"+str(s)).draw(win)

    win.getMouse() # Pause to view result
    win.close()    # Close window when done

main()'''
#3&4
'''def main():
    start_pointx=int(input("please input the x of coordinate of starting point:\r\n"))
    start_pointy=int(input("please input the y of coordinate of starting point:\r\n "))   
    Length=int(input("please input the length:\r\n"))
    width=int(input("please input the width:\r\n"))
    win = GraphWin("My rectangle", 1000, 1000)
    r = Rectangle(Point(start_pointx,start_pointy),Point(start_pointx+width,start_pointy+Length))
    r.draw(win)
    time.sleep(2)
    r.move(100,100)'''

#5
'''def main():
    win = GraphWin("concentric", 1000, 1000)
    r=0.001
    for i in range(20):
        c = Circle(Point(500,500), r)
        c.draw(win)
        r*=2'''
#6
def main():
    n=1
    while(n%10):
        shape=int(input('''
                           1:Circle
                           2:square
                           3:exit\r\n
                           '''))
        win = GraphWin("win", 1000, 1000)

        if shape==1:
            x=int(input("please input the coordinate of x of center\r\n"))
            y=int(input("please input the coordinate of y of center\r\n"))
            r=int(input("please input the radius of center\r\n"))
            c = Circle(Point(x,y), r)
            c.setOutline('green')
            c.draw(win)
        elif shape==2:
            start_pointx=int(input("please input the x of coordinate of starting point:\r\n"))
            start_pointy=int(input("please input the y of coordinate of starting point:\r\n "))   
            Length=int(input("please input the length:\r\n"))
            r = Rectangle(Point(start_pointx,start_pointy),Point(start_pointx+length,start_pointy+Length))
            c.setOutline('blue')
            r.draw(win)
        elif shape==3:
            break

        

    
    
    

main()