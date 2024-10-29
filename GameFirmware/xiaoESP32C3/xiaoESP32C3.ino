#include <SPI.h>
#include <MFRC522.h>
#define SS_PIN  15
#define RST_PIN 2

MFRC522 rfid(SS_PIN, RST_PIN);

void setup() {
	Serial.begin(9600);
	Serial.print("------------STARTING UP spi ------------\n");
	SPI.begin();
	Serial.print("------------STARTING UP rfid------------\n");
	////
	////
	rfid.PCD_Init();
	Serial.println("Tap an RFID/NFC tag on the RFID-RC522 reader");
	}
void loop() {
	
	if (rfid.PICC_IsNewCardPresent()) {
	
		if (rfid.PICC_ReadCardSerial()) {
		
			MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);
			Serial.print("RFID/NFC Tag Type: ");
			Serial.println(rfid.PICC_GetTypeName(piccType));
			
			Serial.print("UID:");
			for (int i = 0; i < rfid.uid.size; i++) {
				Serial.print(rfid.uid.uidByte[i] < 0x10 ? " 0" : " ");
				Serial.print(rfid.uid.uidByte[i], HEX);
				}
			
			Serial.println();
			rfid.PICC_HaltA();
			rfid.PCD_StopCrypto1();
			}
		}
	Serial.print("."); delay(2000);
	}
//  Export  Date: 01:16:11 PM - 25:Oct:2024;

