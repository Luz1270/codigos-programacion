//Luz Elena Bautista Santiago 362313098

#include <conio.h>
#include <stdio.h>
#define pi 3.1416

class circulo{
	private:
		float radio;
	
	public:
		circulo(float r) : radio(r){}
		
		float calcularPerimetro(){
			return 2 * pi * radio;
		}
		
		float calcularArea(){
			return pi * radio * radio;
		}
		
		void setRadio(float r){
			radio = r;
		}
		
		float getRadio(){
			return radio;
		}
};

main()
{
	float radio;
	char opcion;
	
	printf("Introdusca P para el perimetro o A para el area: ");
	opcion = getch();
	
	printf("\nDame el radio: ");
	scanf("%f", &radio);
	
	circulo miCirculo(radio);
	
	if(opcion == 'p'){
		printf("\nEl perimetro es: %.2f", miCirculo.calcularPerimetro());
	}
	
	else if(opcion == 'a'){
		printf("\nEl area es: %.2f", miCirculo.calcularArea());
	}
	getch();	
}
