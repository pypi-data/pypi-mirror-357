#include <pybind11/pybind11.h>
#include <SFML/Graphics.hpp>
#include <string>
#include <vector>
#include <algorithm>
namespace py = pybind11;

std::string to_lower(const std::string& s) {
    std::string result = s;
    std::transform(result.begin(), result.end(), result.begin(), ::tolower);
    return result;
}
struct TextItem {
    sf::Text text;
    TextItem(const std::string& str, sf::Font& font, unsigned int size, sf::Color fillColor, float x, float y) {
    text = text = sf::Text(sf::String(str), font, size);
    text.setFillColor(fillColor);
    text.setPosition(x, y);
}
};
std::vector<TextItem> texts;

sf::RenderWindow window;
std::vector<sf::CircleShape> circles;
std::vector<sf::RectangleShape> rectangles;
sf::Font robotoFont, cursiveFont, figtreeFont, luckyFont;

sf::Color parse_color(std::string color) {
    color = to_lower(color);
    if(color == "red") return sf::Color::Red;
    else if(color == "green") return sf::Color::Green;
    else if(color == "blue") return sf::Color::Blue;
    else if(color == "yellow") return sf::Color::Yellow;
    else if(color == "cyan") return sf::Color::Cyan;
    return sf::Color::White;
}
sf::Vector2i get_mouse_pos(){
    return sf::Mouse::getPosition(window);
}
void init() {
    window.create(sf::VideoMode(400, 300), "Canvas");
}

void draw_circle(unsigned int radius, std::string color, std::string outlineColor, int outlineThickness, float pos_x, float pos_y) {
    sf::CircleShape circle(radius);
    circle.setFillColor(parse_color(color));
    circle.setOutlineColor(parse_color(outlineColor));
    circle.setOutlineThickness(outlineThickness);
    circle.setPosition(pos_x, pos_y); 
    circles.push_back(circle);
}

void draw_rectangle(unsigned int height, unsigned int length, std::string color, std::string outlineColor, unsigned int outlineThickness, float pos_x, float pos_y) {
    sf::RectangleShape rect(sf::Vector2f(length, height));
    rect.setFillColor(parse_color(color));
    rect.setOutlineColor(parse_color(outlineColor));
    rect.setOutlineThickness(outlineThickness);
    rect.setPosition(pos_x, pos_y);
    rectangles.push_back(rect);
}

void draw_text(const std::string& str, const std::string& font_name, unsigned int size, std::string color, float x, float y) {
    sf::Font* selectedFont = nullptr;
    if (font_name == "roboto") selectedFont = &robotoFont;
    else if (font_name == "cursive") selectedFont = &cursiveFont;
    else if (font_name == "figtree") selectedFont = &figtreeFont;
    else if (font_name == "lucky") selectedFont = &luckyFont;
    else selectedFont = &robotoFont; 
    texts.emplace_back(str, *selectedFont, size, parse_color(color), x, y);
}

void load_fonts() {
    if (!robotoFont.loadFromFile("fonts/Roboto-VariableFont_wdth,wght.ttf"))
        throw std::runtime_error("Failed to load Roboto font");
    if (!cursiveFont.loadFromFile("fonts/CedarvilleCursive-Regular.ttf"))
        throw std::runtime_error("Failed to load Cedarville Cursive font");
    if (!figtreeFont.loadFromFile("fonts/Figtree-VariableFont_wght.ttf"))
        throw std::runtime_error("Failed to load Figtree font");
    if (!luckyFont.loadFromFile("fonts/LuckiestGuy-Regular.ttf"))
        throw std::runtime_error("Failed to load Luckiest Guy font");
}
py::function update_callback;
void run() {
    if (!window.isOpen()) return;

    while (window.isOpen()) {
        sf::Event event;
        while (window.pollEvent(event)) {
            if (event.type == sf::Event::Closed)
                window.close();
        }
        window.clear(sf::Color::Black);
        if (!update_callback.is_none()) {
            update_callback();
        }
        for (auto& circle : circles) window.draw(circle);
        for (auto& rect : rectangles) window.draw(rect);
        for (auto& textItem : texts) window.draw(textItem.text);

        window.display();
    }
}

void draw_line(float x1, float y1, float x2, float y2, std::string color) {
    sf::Vertex line[] = {
        sf::Vertex(sf::Vector2f(x1, y1), parse_color(color)),
        sf::Vertex(sf::Vector2f(x2, y2), parse_color(color))
    };
    window.draw(line, 2, sf::Lines);
}
bool is_mouse_button_pressed(std::string button){
    button = to_lower(button);
    if(button == "left"){
        return sf::Mouse::isButtonPressed(sf::Mouse::Left);
    } else if (button == "right"){
        return sf::Mouse::isButtonPressed(sf::Mouse::Right);
    } else if (button == "middle"){
        return sf::Mouse::isButtonPressed(sf::Mouse::Middle);
    }
    return false;
}
void set_update_callback(py::function fn){
    update_callback = fn;
}
bool is_key_pressed(std::string key_name) {
    std::string key = to_lower(key_name);

    if (key == "a") return sf::Keyboard::isKeyPressed(sf::Keyboard::A);
    if (key == "b") return sf::Keyboard::isKeyPressed(sf::Keyboard::B);
    if (key == "c") return sf::Keyboard::isKeyPressed(sf::Keyboard::C);
    if (key == "d") return sf::Keyboard::isKeyPressed(sf::Keyboard::D);
    if (key == "e") return sf::Keyboard::isKeyPressed(sf::Keyboard::E);
    if (key == "f") return sf::Keyboard::isKeyPressed(sf::Keyboard::F);
    if (key == "g") return sf::Keyboard::isKeyPressed(sf::Keyboard::G);
    if (key == "h") return sf::Keyboard::isKeyPressed(sf::Keyboard::H);
    if (key == "i") return sf::Keyboard::isKeyPressed(sf::Keyboard::I);
    if (key == "j") return sf::Keyboard::isKeyPressed(sf::Keyboard::J);
    if (key == "k") return sf::Keyboard::isKeyPressed(sf::Keyboard::K);
    if (key == "l") return sf::Keyboard::isKeyPressed(sf::Keyboard::L);
    if (key == "m") return sf::Keyboard::isKeyPressed(sf::Keyboard::M);
    if (key == "n") return sf::Keyboard::isKeyPressed(sf::Keyboard::N);
    if (key == "o") return sf::Keyboard::isKeyPressed(sf::Keyboard::O);
    if (key == "p") return sf::Keyboard::isKeyPressed(sf::Keyboard::P);
    if (key == "q") return sf::Keyboard::isKeyPressed(sf::Keyboard::Q);
    if (key == "r") return sf::Keyboard::isKeyPressed(sf::Keyboard::R);
    if (key == "s") return sf::Keyboard::isKeyPressed(sf::Keyboard::S);
    if (key == "t") return sf::Keyboard::isKeyPressed(sf::Keyboard::T);
    if (key == "u") return sf::Keyboard::isKeyPressed(sf::Keyboard::U);
    if (key == "v") return sf::Keyboard::isKeyPressed(sf::Keyboard::V);
    if (key == "w") return sf::Keyboard::isKeyPressed(sf::Keyboard::W);
    if (key == "x") return sf::Keyboard::isKeyPressed(sf::Keyboard::X);
    if (key == "y") return sf::Keyboard::isKeyPressed(sf::Keyboard::Y);
    if (key == "z") return sf::Keyboard::isKeyPressed(sf::Keyboard::Z);

    if (key == "space") return sf::Keyboard::isKeyPressed(sf::Keyboard::Space);
    if (key == "enter") return sf::Keyboard::isKeyPressed(sf::Keyboard::Enter);
    if (key == "tab") return sf::Keyboard::isKeyPressed(sf::Keyboard::Tab);
    if (key == "escape") return sf::Keyboard::isKeyPressed(sf::Keyboard::Escape);
    if (key == "backspace") return sf::Keyboard::isKeyPressed(sf::Keyboard::Backspace);
    if (key == "delete") return sf::Keyboard::isKeyPressed(sf::Keyboard::Delete);
    if (key == "left") return sf::Keyboard::isKeyPressed(sf::Keyboard::Left);
    if (key == "right") return sf::Keyboard::isKeyPressed(sf::Keyboard::Right);
    if (key == "up") return sf::Keyboard::isKeyPressed(sf::Keyboard::Up);
    if (key == "down") return sf::Keyboard::isKeyPressed(sf::Keyboard::Down);

    if (key == "lctrl" || key == "leftctrl") return sf::Keyboard::isKeyPressed(sf::Keyboard::LControl);
    if (key == "rctrl" || key == "rightctrl") return sf::Keyboard::isKeyPressed(sf::Keyboard::RControl);
    if (key == "lshift") return sf::Keyboard::isKeyPressed(sf::Keyboard::LShift);
    if (key == "rshift") return sf::Keyboard::isKeyPressed(sf::Keyboard::RShift);
    if (key == "lalt") return sf::Keyboard::isKeyPressed(sf::Keyboard::LAlt);
    if (key == "ralt") return sf::Keyboard::isKeyPressed(sf::Keyboard::RAlt);

    if (key == "f1") return sf::Keyboard::isKeyPressed(sf::Keyboard::F1);
    if (key == "f2") return sf::Keyboard::isKeyPressed(sf::Keyboard::F2);
    if (key == "f3") return sf::Keyboard::isKeyPressed(sf::Keyboard::F3);
    if (key == "f4") return sf::Keyboard::isKeyPressed(sf::Keyboard::F4);
    if (key == "f5") return sf::Keyboard::isKeyPressed(sf::Keyboard::F5);
    if (key == "f6") return sf::Keyboard::isKeyPressed(sf::Keyboard::F6);
    if (key == "f7") return sf::Keyboard::isKeyPressed(sf::Keyboard::F7);
    if (key == "f8") return sf::Keyboard::isKeyPressed(sf::Keyboard::F8);
    if (key == "f9") return sf::Keyboard::isKeyPressed(sf::Keyboard::F9);
    if (key == "f10") return sf::Keyboard::isKeyPressed(sf::Keyboard::F10);
    if (key == "f11") return sf::Keyboard::isKeyPressed(sf::Keyboard::F11);
    if (key == "f12") return sf::Keyboard::isKeyPressed(sf::Keyboard::F12);

    if (key == "0") return sf::Keyboard::isKeyPressed(sf::Keyboard::Num0);
    if (key == "1") return sf::Keyboard::isKeyPressed(sf::Keyboard::Num1);
    if (key == "2") return sf::Keyboard::isKeyPressed(sf::Keyboard::Num2);
    if (key == "3") return sf::Keyboard::isKeyPressed(sf::Keyboard::Num3);
    if (key == "4") return sf::Keyboard::isKeyPressed(sf::Keyboard::Num4);
    if (key == "5") return sf::Keyboard::isKeyPressed(sf::Keyboard::Num5);
    if (key == "6") return sf::Keyboard::isKeyPressed(sf::Keyboard::Num6);
    if (key == "7") return sf::Keyboard::isKeyPressed(sf::Keyboard::Num7);
    if (key == "8") return sf::Keyboard::isKeyPressed(sf::Keyboard::Num8);
    if (key == "9") return sf::Keyboard::isKeyPressed(sf::Keyboard::Num9);

    return false;
}
void clear(){
    texts.clear();
    circles.clear();
    rectangles.clear();
}
PYBIND11_MODULE(canvas_painter, m) {
    m.def("init", &init);
    m.def("draw_circle", &draw_circle);
    m.def("draw_rectangle", &draw_rectangle);
    m.def("draw_text", &draw_text);
    m.def("load_fonts", &load_fonts);
    m.def("run", &run);
    m.def("get_mouse_pos", &get_mouse_pos);
    m.def("draw_line", &draw_line);
    m.def("is_mouse_button_pressed", &is_mouse_button_pressed);
    m.def("is_key_pressed", &is_key_pressed);
    m.def("clear", &clear);
    m.def("set_update_callback", &set_update_callback);
}
