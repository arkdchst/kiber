#include <iostream>
#include <fstream>

#include <pigpiod_if2.h>

extern "C" {
void serial_setServo(unsigned char s_id, int pos, int time){
	int pi = pigpio_start(NULL, NULL);
	if(pi < 0){
		std::cerr << "error occured";
		return;
	}
	set_mode(pi, 17, PI_OUTPUT);
	set_mode(pi, 27, PI_OUTPUT);
	gpio_write(pi, 17, 0);
	gpio_write(pi, 27, 1);

	if(pos > 1000)
		pos = 1000;
	else if(pos < 0)
		pos = 0;

	if(time > 30000)
		time = 30000;
	else if(time < 10)
		time = 10;
	
	std::ofstream serial;
	serial.open("/dev/ttyAMA0");

	//TODO: portwrite

	auto *buf = new char[10];
	buf[0] = 0x55;
	buf[1] = 0x55;
	buf[2] = s_id;
	buf[3] = 7;
	buf[4] = 1;
	buf[5] = 0xff & pos;
	buf[6] = 0xff & (pos >> 8);
	buf[7] = 0xff & time;
	buf[8] = 0xff & (time >> 8);

	int sum = 0;
	for(int i = 0; i < 9; i++) sum += buf[i];

	sum = sum - 0x55 - 0x55;
	sum = ~sum;
	buf[9] = 0xff & sum;

	serial.write(buf, 10);
	serial.close();

	pigpio_stop(pi);
}

}
