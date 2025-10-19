# canvas
tkinter Canvas classes and functions

## DEPENDENCIES

- **PIL**: Python Image Library; the current version is called Pillow. This is only
  needed for the functions in **canvas_ui.py**.
- **tkinter**, may need to be installed, on some linux distributions.

## CLASSES

**canvas_classes.py** defines several classes.

- **MyCanvas**: a base class which is a tkinter Canvas, with some default attributes
  and basic functionality for reading the cursor.
- **DrawCanvas**: a subclass of MyCanvas which provides methods for tracking cursor
  movement while defining sets of line segments.
- **ShapeCanvas**: a subclass of MyCanvas which provides methods for adding pre-defined
  shapes to the canvas, such as ovals, rectangles and curves, and for storing properties
  of these shapes. Shape properties (e.g. line color, center coordinates) are used to
  identify shapes and move or delete them, or change their attribute(s). Because
  properties are frequently needed, a small Shape class is implemented to hold
  object properties.

## FUNCTIONS

**canvas_ui.py** defines functions for setting the attributes of tkinter Canvas objects
in any program (not necessarily the classes described above.) This includes, especially,
the arrangement of several Canvas objects within a tkinter Frame.