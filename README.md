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

	$  cat test.c
	#include<stdio.h>
	#include<stdbool.h>
	#include<stdlib.h>
	#include<time.h>
	
	
	static void func9(void) { printf("leaf\n"); }

	void func8(void) { func9(); }
	
	void func7_1(bool is_true, int *p) { printf("leaf (is_true=%d, ptr=%p\n", is_true, p); }
	void func7(void) { func8(); }
	
	void func6(void) { func7(); }
	
	void func5_1(const char* str) { printf("leaf (%s)\n", str); }
	void func5(void) {
	    func5_1("graph me\n");
	    func6();
	}
	
	void func4(void) { func5(); }
	void func3_1(int a, int b, int c) { printf("leaf\n"); }
	void func3(void) {
	    func3_1(rand(), rand(), rand());
	    func4();
	}
	
	void func2_1(int a, int b) { printf("leaf (%d, %d)\n", a, b);}
	void func2(void) {
	    func2_1(rand(),rand());
	    func3();
	}
	void func1(void) { func2(); }
	int main()
	{
	    srand(time(NULL));
	    for(int i=0; i<10; ++i) {
	            func1();
	    }
	        return 0;
	}

### Enable debugging symbols    
    $ gcc -g test.c

### Start binary under GDB     
    $ gdb a.out
    . . .
    Reading symbols from a.out...done.

#### Insert breakpoints on functions of interest, or to put in every funtion in a file:    

	(gdb) rbreak test.c:.
	Breakpoint 1 at 0x400786: file test/test.c, line 33.
	void func1(void);
	Breakpoint 2 at 0x400760: file test/test.c, line 30.
	void func2(void);
	Breakpoint 3 at 0x40073d: file test/test.c, line 28.
	void func2_1(int, int);
	Breakpoint 4 at 0x400704: file test/test.c, line 24.
	void func3(void);
	Breakpoint 5 at 0x4006f0: file test/test.c, line 22.
	void func3_1(int, int, int);
	Breakpoint 6 at 0x4006d7: file test/test.c, line 21.
	void func4(void);
	Breakpoint 7 at 0x4006c1: file test/test.c, line 17.
	void func5(void);
	Breakpoint 8 at 0x4006a4: file test/test.c, line 15.
	void func5_1(const char *);
	Breakpoint 9 at 0x400690: file test/test.c, line 13.
	void func6(void);
	Breakpoint 10 at 0x400684: file test/test.c, line 11.
	void func7(void);
	Breakpoint 11 at 0x400664: file test/test.c, line 10.
	void func7_1(_Bool, int *);
	Breakpoint 12 at 0x40064b: file test/test.c, line 8.
	void func8(void);
	Breakpoint 13 at 0x400796: file test/test.c, line 36.
	int main();
	Breakpoint 14 at 0x40063a: file test/test.c, line 7.
	static void func9(void);

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

    Once the program finishes, it would have dumped the logs to the disk in test.log    


## Part II: run gen_graph.py on collected data

### Dependencies    

    sudo apt-get install graphviz
    sudo python3 -m pip install -r requiments.txt


### Run gen_graph.py    
    $  python3 gen_graph.py
    usage: gen_graph.py [-h] -i INPUT_FILE [-f {gdb,objdump}]
    gen_graph.py: error: the following arguments are required: -i/--input_file

    $  python3 gen_graph.py -i test/test.log
	01/02/2021 08:36:58 PM [1] processing gdb bt data
	01/02/2021 08:36:58 PM [2] adding nodes, edges, #ofnodes=13
	01/02/2021 08:36:59 PM [3] Embedding JS
	01/02/2021 08:36:59 PM [4] saving graph to:
	01/02/2021 08:36:59 PM       /home/vagrant/dwnlds/gdb_graphs/test.svg
	01/02/2021 08:36:59 PM Finished
 

Open the svg file in a browser
![Alt text](gallery/test.png?raw=true "")


## New 
- Interactive graphs:
  Click on a node and entire parent and child chain is highlighted
  (to reset -  reload page - untill I find a better way to do from JS)
- C++ Support
- Node tooltip shows function arguments (max 6)
