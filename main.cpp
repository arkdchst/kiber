#include <time.h>
#include <stdio.h>
#include <math.h>
#include <vector>

#include <SFML/Graphics.hpp>


// std::vector<float> from_base(){

// 	std::vector<float> a(2);
// 	return std::vector<float> (2);
// }


std::vector<float> ** initLines(){

	std::vector<float> **lines = new std::vector<float>*[2];
		lines[0] = new std::vector<float>[2];
			lines[0][0] = std::vector<float>(2, 0);
			lines[0][1] = std::vector<float>(2, 0);
		lines[1] = new std::vector<float>[2];
			lines[1][0] = std::vector<float>(2, 0);
			lines[1][1] = std::vector<float>(2, 0);

	return lines;

}


void process(std::vector<float> **lines, float time, sf::RenderWindow &window){
	const float v0 = 10;
	const float l0 = 50;
	float a = sin(time);
	float b = cos(time);

	float l = v0 * time;

	float x1 = l * cos(a);
	float y1 = l * sin(a);

	float x2 = (l0 * sin(b) + l) * cos(a) - l0 * sin(a) * cos(b);
	float y2 = (l0 * sin(b) + l) * sin(a) + l0 * cos(b) * cos(a);



		lines[0][1][0] = x1;
		lines[0][1][1] = y1;
		lines[1][0][0] = x1;
		lines[1][0][1] = y1;
		lines[1][1][0] = x2;
		lines[1][1][1] = y2;


	printf("%f %f %f %f\n", x1, y1, x2, y2);
}


void draw(std::vector<float> **lines, sf::RenderWindow &window){
	sf::VertexArray line1(sf::Lines, 2);
	sf::VertexArray line2(sf::Lines, 2);

		line1[0].position = sf::Vector2f(lines[0][0][0], lines[0][0][1]);
		line1[1].position = sf::Vector2f(lines[0][1][0], lines[0][1][1]);
		line2[0].position = sf::Vector2f(lines[1][0][0], lines[1][0][1]);
		line2[1].position = sf::Vector2f(lines[1][1][0], lines[1][1][1]);

		line1[0].color = sf::Color::Red;
		line1[1].color = sf::Color::Red;
		line2[0].color = sf::Color::Green;
		line2[1].color = sf::Color::Green;


	window.draw(line1);
	window.draw(line2);
}


int main(){
	float time = 0;

	sf::RenderWindow window(sf::VideoMode(600, 600), "", sf::Style::None);
	window.display();

	window.setView(sf::View(sf::Vector2f(250, 0), sf::Vector2f(500, -500)));

	std::vector<float> **lines = initLines();

	while (window.isOpen()){
		sf::Event event;
		while(window.pollEvent(event)) if (event.type == sf::Event::Closed)
				window.close();

		window.clear(sf::Color::Black);
			process(lines, time, window);
			draw(lines, window);
			window.display();


		sf::sleep(sf::milliseconds(5));

		time += 0.01;
	}

	return 0;
}
