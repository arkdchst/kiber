#include <time.h>
#include <stdio.h>
#include <math.h>
#include <vector>

#include <SFML/Graphics.hpp>



struct Line{
	std::vector<float> A = std::vector<float>(2,0);
	std::vector<float> B = std::vector<float>(2,0);
};




std::vector<float> move(std::vector<float> vec, std::vector<float> delta){ //res = vec + delta
	std::vector<float> res(2);
	res = {vec[0] + delta[0], vec[1] + delta[1]};

	return res;
}

std::vector<float> rotate(std::vector<float> vec, float a){ //a - angle
	std::vector<float> res = std::vector<float>(vec); //copy
	res = {	vec[0] * cos(a) - vec[1] * sin(a), 
			vec[0] * sin(a) + vec[1] * cos(a)};

	return res;	
}




void process(Line *lines, float time){
	const float v0 = 10;
	const float l0 = 50;
	float a = sin(time);
	float b = cos(time);

	float l = v0 * time;

	std::vector<float> vec1 = {l, 0};
	vec1 = rotate(vec1, a);

	std::vector<float> vec2 = {l0, 0};
	vec2 = rotate(move(rotate(vec2, M_PI/2 - b), std::vector<float>{l, 0}), a);


		lines[0].B = std::vector<float>(vec1);
		lines[1].A = std::vector<float>(vec1);
		lines[1].B = std::vector<float>(vec2);


}


void draw(Line *lines, sf::RenderWindow &window){
	sf::VertexArray line1(sf::Lines, 2);
	sf::VertexArray line2(sf::Lines, 2);

		line1[0].position = sf::Vector2f(lines[0].A[0], lines[0].A[1]);
		line1[1].position = sf::Vector2f(lines[0].B[0], lines[0].B[1]);
		line2[0].position = sf::Vector2f(lines[1].A[0], lines[1].A[1]);
		line2[1].position = sf::Vector2f(lines[1].B[0], lines[1].B[1]);

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


	Line *lines = new Line[2];

	while (window.isOpen()){
		sf::Event event;
		while(window.pollEvent(event)) if (event.type == sf::Event::Closed)
				window.close();

		window.clear(sf::Color::Black);
			process(lines, time);
			draw(lines, window);
			window.display();


		sf::sleep(sf::milliseconds(5));

		time += 0.01;
	}

	return 0;
}
