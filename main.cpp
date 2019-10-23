#include <time.h>
#include <stdio.h>
#include <math.h>

#include <SFML/Graphics.hpp>


sf::VertexArray * initLines(){
	sf::VertexArray line1(sf::Lines, 2);
	sf::VertexArray line2(sf::Lines, 2);
	line1[0].color = sf::Color::Red;
	line1[1].color = sf::Color::Red;
	line2[0].color = sf::Color::Green;
	line2[1].color = sf::Color::Green;


	sf::VertexArray *lines = new sf::VertexArray[2];
	lines[0] = line1;
	lines[1] = line2;


	return lines;

}


void process(sf::VertexArray * lines, float t, sf::RenderWindow &window){
	const float v0 = 10;
	const float l0 = 50;

	float x1,y1,x2,y2;

	x1 = v0 * t * cos(sin(t));
	y1 = v0 * t * sin(sin(t));

	x2 = x1 - l0 * sin(sin(t) - cos(t));
	y2 = y1 + l0 * cos(sin(t) - cos(t));

	lines[0][0].position = sf::Vector2f(0, 0);
	lines[0][1].position = sf::Vector2f(x1, y1);
	lines[1][0].position = sf::Vector2f(x1, y1);
	lines[1][1].position = sf::Vector2f(x2, y2);


	printf("%f %f %f %f\n", x1, y1, x2, y2);
}


void draw(sf::VertexArray * lines, sf::RenderWindow &window){

	window.draw(lines[0]);
	window.draw(lines[1]);
}


int main(){
	float t = 0;

	sf::RenderWindow window(sf::VideoMode(600, 600), "", sf::Style::None);
	window.display();

	window.setView(sf::View(sf::Vector2f(250, 0), sf::Vector2f(500, -500)));

	sf::VertexArray *lines = initLines();

	while (window.isOpen()){
		sf::Event event;
		while(window.pollEvent(event)) if (event.type == sf::Event::Closed)
				window.close();

		window.clear(sf::Color::Black);
			process(lines, t, window);
			draw(lines, window);
			window.display();


		sf::sleep(sf::milliseconds(10));

		t += 0.01;
	}

	return 0;
}
