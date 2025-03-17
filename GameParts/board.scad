include <E:\Users\luisr\OneDrive\Desktop\PROJECTS\SCAD_Modules\modules.scad>

BX = 120;
BY = BX ;
BH = 2.5;
module board( R = 26/2 , t=1.6 ) {
	difference(){
	union(){
		box( BX, BY , BH );
	} #union(){
		Dim = 3;
		SPACING = 6;
		S = 2*R+ (Dim*SPACING) / 4 ;
		Dx = S ;
		for  ( X = [ 0:Dim ]) {
			for  ( Y = [ 0:Dim ]) {
				translate( [ -S - Dx/2  , -S -Dx/2 , 0 ] )
				translate( [ X*Dx, Y*Dx , BH - t+.01 ] )  cylinder( r = R, h = 5, center=false);
				}
			
			}
		
		} }
	}
board ( );
//  Export  Date: 03:47:40 PM - 17:Mar:2025...

