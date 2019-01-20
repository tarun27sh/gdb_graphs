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
