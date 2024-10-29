#include <SPI.h>
#include <MFRC522.h>
#define SS_PIN  15
#define RST_PIN 2

MFRC522 rfid(SS_PIN, RST_PIN);

int  N=16;
int UID[ ] = {

	559,
	652,
	735,
	631,

	577,
	702,
	647,
	889,

	739,
	621,
	605,
	883,

	655,
	674,
	551,
	729,
	
0
} ;

	int _get_Address( int uid ) {
		for(int i=0; i<N; i++ ){
			if ( uid ==  UID[i] )
			{
				return i ;
				}
			}
		
		return uid  ;  }
	
	int get_Address( int uid ) {
		int    i=0;
		while(   UID[ i ] != 0 && i < N ) {
			if ( uid ==  UID[ i ] )
			{
				return i   ;
				}
			i++;
			}
		
		return uid;  }
		
	
void setup() {
	Serial.begin(9600);
	Serial.print("------------STARTING UP spi ------------\n");
	SPI.begin();
	Serial.print("------------STARTING UP rfid------------\n");
	rfid.PCD_Init();
	Serial.println("Tap an RFID/NFC tag on the RFID-RC522 reader");
	}
String uidString = " ";
int uid =0 ;
void loop() {
	
	if (rfid.PICC_IsNewCardPresent()) {
	
		if (rfid.PICC_ReadCardSerial()) {
		
			MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);
			// //////
			// //////
			uid = 0;
			
			for (int i = 0; i < rfid.uid.size; i++) {
				////
				uid += rfid.uid.uidByte[i] ;
				}
			
			rfid.PICC_HaltA();
			rfid.PCD_StopCrypto1();
			uid =  get_Address( uid ) ;
			Serial.print( uid ); Serial.println(  "," );
			}
		}
	// //////
	}
//  Export  Date: 11:27:02 PM - 28:Oct:2024;

