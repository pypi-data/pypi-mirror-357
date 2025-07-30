# Canvas

Canvas is a small Python graphics library written in SFML.  
In the future, Canvas will be bigger and maybe even a famous library, but we can only hope.

## Syntax

### Setup

First of all, you need to import it.  
In your selected terminal, run:

```bash
pip install canvas
```
Then in your Python script (e.g. script.py):
```python
import canvas
```
### Functions

- canvas.init() 
  Initializes the drawing canvas/window.

- canvas.load_fonts()  
  Loads the default fonts included in the package. You should call this before drawing text.

- canvas.draw_circle(radius, fill_color, outline_color, outline_thickness, x, y)  
  Draw a circle with:  
  - radius (int)  
  - fill_color (str) — red, green, blue, yellow, cyan, or white (default)  
  - outline_color (str)  
  - outline_thickness (int)  
  - x, y (float) — position coordinates  

- canvas.draw_rectangle(height, length, fill_color, outline_color, outline_thickness, x, y)  
  Draw a rectangle with similar parameters to draw_circle.

- canvas.draw_text(text, font_name, size, color, x, y)  
  Draw text string with:  
  - text (str) — the string to draw  
  - font_name (str) — one of "roboto", "cursive", "figtree", or "lucky"  
  - size (int) — font size  
  - color (str)  
  - x, y (float) — position coordinates

- canvas.draw_line(x1, y1, x2, y2, color)  
  Draw a line between (x1, y1) and (x2, y2) with specified color.

- canvas.get_mouse_pos()  
  Returns the current mouse position relative to the window as an (x, y) tuple.

- canvas.run()  
  Opens the window and starts rendering your shapes and text. This blocks until you close the window.

- canvas.clear()  
  Clears the window content (fill with black). You can call this between frames.

## Example
```python
import canvas

canvas.init()
canvas.load_fonts()

canvas.draw_circle(50, "red", "white", 3, 100, 100)
canvas.draw_rectangle(80, 120, "blue", "yellow", 5, 200, 150)
canvas.draw_text("Hello Canvas!", "roboto", 24, "cyan", 50, 30)

canvas.run()
```
---

Happy drawing! 🎨✨  
If you find bugs or want features, feel free to open an issue or pull request on GitHub.

---

Canvas is a community project and is still growing.  
Thanks for checking it out!