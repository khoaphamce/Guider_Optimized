#include "emulatetag.h"
#include "NdefMessage.h"

#if 1
  #include <SPI.h>
  #include <PN532_SPI.h>
  #include "PN532.h"

  PN532_SPI pn532spi(SPI, 10);
  EmulateTag nfc(pn532spi);
#elif 1
  #include <PN532_HSU.h>
  #include <PN532.h>
      
  PN532_HSU pn532hsu(Serial1);
  EmulateTag nfc(pn532hsu);
#endif

uint8_t ndefBuf[120];
NdefMessage message;
int messageSize;

uint8_t uid[3] = { 0x12, 0x34, 0x56 };
String SerialIn;

int HighLed = 8;

void setup()
{
  pinMode(HighLed, OUTPUT);
  
  Serial.begin(9600);

  while(!Serial.available()){
    Serial.println("Ready");
    delay(1000);
    continue;
  }
  
  SerialIn = Serial.readString();
  SerialIn.trim();
  
  message = NdefMessage();
  message.addUriRecord(SerialIn);
  messageSize = message.getEncodedSize();
  
//  if (messageSize > sizeof(ndefBuf)) {
//      Serial.println("ndefBuf is too small");
//      while (1) { }
//  }
  
//  Serial.print("Ndef encoded message size: ");
//  Serial.println(messageSize);

  message.encode(ndefBuf);
  
  // comment out this command for no ndef message
  nfc.setNdefFile(ndefBuf, messageSize);
  
  // uid must be 3 bytes!
  nfc.setUid(uid);
  
  nfc.init();
}


void loop(){
    // uncomment for overriding ndef in case a write to this tag occured
    Serial.println("yes");
    nfc.emulate();
    
    // nfc.setTagWriteable(false);
    
    if(nfc.writeOccured()){
       Serial.println("\nWrite occured !");
       uint8_t* tag_buf;
       uint16_t length;
       
       nfc.getContent(&tag_buf, &length);
       NdefMessage msg = NdefMessage(tag_buf, length);
       msg.print();
    }
}
