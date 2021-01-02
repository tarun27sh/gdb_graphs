#include<stdio.h>
#include<stdbool.h>
#include<stdlib.h>
#include<time.h>


static void func9(void) { printf("leaf\n"); }
void func8(void) { func9(); }

void func7_1(bool is_true, int *p) { printf("leaf (is_true=%d, ptr=%p\n", is_true, p); }
void func7(void) { 
    int a;
    func7_1(false, &a);
    func8(); 
}

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
