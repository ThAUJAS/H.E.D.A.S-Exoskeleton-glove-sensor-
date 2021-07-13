#include<Wire.h>
#include <curveFitting.h>
#include "MedianFilterLib.h"

//IMU var
const int MPU_ADDR = 0x68; 
int16_t accX, accY, accZ;
double xAngle, yAngle, zAngle;
MedianFilter<float> medianFilterRoll(10);
MedianFilter<float> medianFilterPitch(10);
MedianFilter<float> medianFilterYaw(10);
double pitch,roll,yaw;

//Mux variables
int s0 = 4;
int s1 = 5;
int s2 = 6;
int s3 = 7;
int SIG_pin = 6;

const int sizeAngle = 20;
double angles[sizeAngle];

int muxChannel[16][4]={
  {0,0,0,0}, //channel 0
  {1,0,0,0}, //channel 1
  {0,1,0,0}, //channel 2
  {1,1,0,0}, //channel 3
  {0,0,1,0}, //channel 4
  {1,0,1,0}, //channel 5
  {0,1,1,0}, //channel 6
  {1,1,1,0}, //channel 7
  {0,0,0,1}, //channel 8
  {1,0,0,1}, //channel 9
  {0,1,0,1}, //channel 10
  {1,1,0,1}, //channel 11
  {0,0,1,1}, //channel 12
  {1,0,1,1}, //channel 13
  {0,1,1,1}, //channel 14
  {1,1,1,1}  //channel 15
};

void setup(){
  pinMode(s0, OUTPUT); 
  pinMode(s1, OUTPUT); 
  pinMode(s2, OUTPUT); 
  pinMode(s3, OUTPUT); 
  digitalWrite(s0, LOW);
  digitalWrite(s1, LOW);
  digitalWrite(s2, LOW);
  digitalWrite(s3, LOW);
  
  Serial.begin(115200);
    
   Wire.begin();
  Wire.beginTransmission(MPU_ADDR); // Begins a transmission to the I2C slave (GY-521 board)
  Wire.write(0x6B); // PWR_MGMT_1 register
  Wire.write(0); // set to zero (wakes up the MPU-6050)
  Wire.endTransmission(true);
}
 
void loop(){
 //-------Finger joints----------//
  for(int i = 0; i<4;i++){
      int channel = i*3+2;
      // PIP joints
      angles[i+1] = readMux(channel);
      // MCP x joints
      angles[i+6] = readMux(channel+1);
      // MCP z joints
      angles[i+11] = readMux(channel+2);
  }
  for (int j = 0; j<3;j++){
      angles[j*5] = analogRead(j);
  }
  angles[15] = analogRead(3);
  angles[16] = analogRead(7);
  
  //----IMU reading-------//
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B); 
  Wire.endTransmission(false); 
  Wire.requestFrom(MPU_ADDR, 6, true);
  accX = Wire.read()<<8 | Wire.read(); 
  accY = Wire.read()<<8 | Wire.read(); 
  accZ = Wire.read()<<8 | Wire.read(); 
  
  xAngle = map(accX, 265, 402, -90, 90);
  yAngle = map(accY, 265, 402, -90, 90);
  zAngle = map(accZ, 265, 402, -90, 90);
  
  angles[17] = medianFilterRoll.AddValue(degrees(atan2(-yAngle, -xAngle) + PI)); //roll
  angles[18] = medianFilterPitch.AddValue(degrees(atan2(-xAngle, -zAngle) + PI)); // pitch
  angles[19] = medianFilterYaw.AddValue(degrees(atan2(-yAngle, -xAngle) + PI)); //yaw
  
  //-Printing on the serial monitor for Python to receive the data-//





























  
  for(int i = 0; i < sizeAngle-1; i++)
  {
    Serial.print(angles[i]);Serial.print(" ");
  }
  Serial.println(angles[sizeAngle-1]);
 }

//functions
int readMux(int channel){
  int controlPin[] = {s0, s1, s2, s3};
  //loop through the 4 sig
  for(int i = 0; i < 4; i ++){
    digitalWrite(controlPin[i], muxChannel[channel][i]);
  }

  //read the value at the SIG pin
  int val = analogRead(SIG_pin);

  //return the value
  return val;
}
