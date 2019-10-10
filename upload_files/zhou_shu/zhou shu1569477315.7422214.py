'''def main():
    print("This program illustrates a chaotic function")
    x = float(input("Enter a number between 0 and 1: "))
    for i in range(10):
        x = 3.9 * x * (1 - x)
        print(x)
main()'''

back=[[1,0,1],[1,1,1],[1,0,1]];
def win():
    '''global back
    cols=[x is -1 for x in range(len(back[0]))];
    for col in range(len(back[0])):
        for row in range(len(back)):
            cols[row]=back[row][col];
            if cols.count(cols[0])==len(cols) and cols[0]!=0:
                print("win!");
                print("|")
                
        print(cols);'''
        
    d_col=range(len(back));
    d_row=reversed(range(len(back)));
    cood=zip(d_row,d_col);
    test1=[];
    for x,y in cood:
        test1.append(back[x][y]);
    if test1.count(test1[0])==len(test1) and test1[0]!=0:
        print("win!\\");       
    cood=zip(d_col,d_col);
    test2=[]
    for x,y in cood:
        test2.append(back[x][y]);
    if test1.count(test1[0])==len(test1) and test1[0]!=0:
        print("win!/");

        
win();




