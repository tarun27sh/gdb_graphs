# gen_graph.py

![Alt text](gallery/some_library_graph.png?raw=true "")


## Description
Python command line tool to visualize function-call-flow for a C/C++ program using graphviz dot object and matplotlib.
    
    Directory structure:

    ├── gallery
    │   ├── graph_GNU_MAKE_.png
    │   ├── graph_QEMU.png
    │   ├── graph_VIM.png
    │   ├── some_library_graph.png
    │   ├── test.png
    │   └── test.svg
    ├── gen_graph.py
    ├── LICENSE
    ├── README.md
    ├── requiments.txt
    └── test
        ├── test.c
        └── test.log

## Motivation
I wanted to view call-graph for OS source (written in C, C++) that connected APIs within one layer and APIs across layers.
This helps in getting a bigger picture of the source code and makes understanding large code bases QUICK.

## Input
Requires data from gdb to get nodes (functions) and edges (function 1 calling function 2).

## Output
Di-graph showing relationship between functions across software layers, the "bigger picture".


# Usage 

There are two parts to the whole process:
1. get data by runnning process under gdb
2. process this data with gen_graph.py


## Part I: Get data from GDB

### Test code    
    $ cat test.c
    #include<stdio.h>


    static void func9(void) { printf("leaf\n");; }
    void func8(void) { func9(); }
    void func7(void) { func8(); }
    void func6(void) { func7(); }
    void func5(void) { func6(); }
    void func4(void) { func5(); }
    void func3(void) { func4(); }
    void func2(void) { func3(); }
    void func1(void) { func2(); }
    int main()
    {
            func1();
            return 0;
    }

### Enable debugging symbols    
    $ test -g test.c

### Now, the GDB part
#### start binary under GDB     
    $ gdb a.out
    . . .
    Reading symbols from a.out...done.

#### Insert breakpoints on functions of interest, or to put in every funtion in a file:    

    (gdb) rbreak test.c:.
    Breakpoint 1 at 0x40058f: file he.c, line 12.
    void func1(void);
    Breakpoint 2 at 0x400583: file he.c, line 11.
    void func2(void);
    Breakpoint 3 at 0x400577: file he.c, line 10.
    void func3(void);
    Breakpoint 4 at 0x40056b: file he.c, line 9.
    void func4(void);
    Breakpoint 5 at 0x40055f: file he.c, line 8.
    void func5(void);
    Breakpoint 6 at 0x400553: file he.c, line 7.
    void func6(void);
    Breakpoint 7 at 0x400547: file he.c, line 6.
    void func7(void);
    Breakpoint 8 at 0x40053b: file he.c, line 5.
    void func8(void);
    Breakpoint 9 at 0x40052a: file he.c, line 4.
    void func9(void);
    Breakpoint 10 at 0x40059b: file he.c, line 15.
    int main();

#### Enable logging
    (gdb) set pagination off
    (gdb) set print pretty
    (gdb) set logging file ./test.log
    (gdb) set logging on
    Copying output to ./test.log.

#### Tell gdb to print backtrace and continue without asking when it hits  a breakpoint    
    (gdb) command
    Type commands for breakpoint(s) 1-10, one per line.
    End with a line saying just "end".
    >bt
    >c
    >end


#### Start  the program    
    (gdb) r
    Starting program: /home/vagrant/c_code/a.out


#### Once the program finishes, it would have dumped the logs to the disk in test.log    

    $ cat test.log
    Type commands for breakpoint(s) 1-10, one per line.
    End with a line saying just "end".
    Starting program: /home/vagrant/c_code/a.out

    Breakpoint 9, main () at he.c:15
    15              func1();
    #0  main () at he.c:15

    Breakpoint 1, func1 () at he.c:12
    12      void func1(void) { func2(); }
    #0  func1 () at he.c:12
    #1  0x00000000004005a0 in main () at he.c:15

    Breakpoint 2, func2 () at he.c:11
    11      void func2(void) { func3(); }
    #0  func2 () at he.c:11
    #1  0x0000000000400594 in func1 () at he.c:12
    #2  0x00000000004005a0 in main () at he.c:15

    Breakpoint 3, func3 () at he.c:10
    10      void func3(void) { func4(); }
    #0  func3 () at he.c:10
    #1  0x0000000000400588 in func2 () at he.c:11
    #2  0x0000000000400594 in func1 () at he.c:12
    #3  0x00000000004005a0 in main () at he.c:15

    Breakpoint 4, func4 () at he.c:9
    9       void func4(void) { func5(); }
    #0  func4 () at he.c:9
    #1  0x000000000040057c in func3 () at he.c:10
    #2  0x0000000000400588 in func2 () at he.c:11
    #3  0x0000000000400594 in func1 () at he.c:12
    #4  0x00000000004005a0 in main () at he.c:15

    Breakpoint 5, func5 () at he.c:8
    8       void func5(void) { func6(); }
    #0  func5 () at he.c:8
    #1  0x0000000000400570 in func4 () at he.c:9
    #2  0x000000000040057c in func3 () at he.c:10
    #3  0x0000000000400588 in func2 () at he.c:11
    #4  0x0000000000400594 in func1 () at he.c:12
    #5  0x00000000004005a0 in main () at he.c:15

    Breakpoint 6, func6 () at he.c:7
    7       void func6(void) { func7(); }
    #0  func6 () at he.c:7
    #1  0x0000000000400564 in func5 () at he.c:8
    #2  0x0000000000400570 in func4 () at he.c:9
    #3  0x000000000040057c in func3 () at he.c:10
    #4  0x0000000000400588 in func2 () at he.c:11
    #5  0x0000000000400594 in func1 () at he.c:12
    #6  0x00000000004005a0 in main () at he.c:15

    Breakpoint 7, func7 () at he.c:6
    6       void func7(void) { func8(); }
    #0  func7 () at he.c:6
    #1  0x0000000000400558 in func6 () at he.c:7
    #2  0x0000000000400564 in func5 () at he.c:8
    #3  0x0000000000400570 in func4 () at he.c:9
    #4  0x000000000040057c in func3 () at he.c:10
    #5  0x0000000000400588 in func2 () at he.c:11
    #6  0x0000000000400594 in func1 () at he.c:12
    #7  0x00000000004005a0 in main () at he.c:15

    Breakpoint 8, func8 () at he.c:5
    5       void func8(void) { func9(); }
    #0  func8 () at he.c:5
    #1  0x000000000040054c in func7 () at he.c:6
    #2  0x0000000000400558 in func6 () at he.c:7
    #3  0x0000000000400564 in func5 () at he.c:8
    #4  0x0000000000400570 in func4 () at he.c:9
    #5  0x000000000040057c in func3 () at he.c:10
    #6  0x0000000000400588 in func2 () at he.c:11
    #7  0x0000000000400594 in func1 () at he.c:12
    #8  0x00000000004005a0 in main () at he.c:15

    Breakpoint 10, func9 () at he.c:4
    4       static void func9(void) { printf("leaf\n");; }
    #0  func9 () at he.c:4
    #1  0x0000000000400540 in func8 () at he.c:5
    #2  0x000000000040054c in func7 () at he.c:6
    #3  0x0000000000400558 in func6 () at he.c:7
    #4  0x0000000000400564 in func5 () at he.c:8
    #5  0x0000000000400570 in func4 () at he.c:9
    #6  0x000000000040057c in func3 () at he.c:10
    #7  0x0000000000400588 in func2 () at he.c:11
    #8  0x0000000000400594 in func1 () at he.c:12
    #9  0x00000000004005a0 in main () at he.c:15
    [Inferior 1 (process 3363) exited normally]
    $



## Part II: run gen_graph.py on collected data

### Dependencies    

    sudo apt-get install graphviz
    sudo python3 -m pip install -r requiments.txt


### Now run gen_graph.py    

    $ python gen_graphs.py
    Usage:
    python3 ./gen_graphs.py  <gdb_backtrace_logs>
    

    $ python3 gen_graphs.py test.log
    [1] parsing gdb logs..
    [2] adding nodes..
            # of nodes: 10
    [3] adding edges..
            # of edges: 9
    [4] saving graph to:
            /home/vagrant/gdb_graphs/test.svg

Open the svg file in a browser
![Alt text](gallery/test.png?raw=true "")


## New 
- Interactive graphs:
  Click on a node and entire parent and child chain is highlighted
  (to reset -  reload page - untill I find a better way to do from JS)
- C++ Support
