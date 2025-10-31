"""
module: canvas_classes.py

purpose: Defines child classes of tkinter Canvas.

comments:

author: Russell Folks

history:
-------

02-26-2025  creation
03-01-2025  Add function calc_location to calculate x,y position for the next
            instance of each shape. Add default rectangle and arc sizes.
            Standardize class docstring format.
            New commit.
03-04-2025  Review all docstrings and edit for clarity and consistency.
03-24-2025  ShapeCanvas binds 'Key' event, to be first used for deleting the
            current shape. Add delete_shape(). Add 'objlist' to keep track of
            shapes, to replace shape_tags, shape_centers and shape_linecolors.
03-29-2025  Finish replacing use cases for shape_centers and shape_linecolors.
            Add bind for Control-Button-3, and stub multi_select().
03-31-2025  Remove references to shape_centers and shape_linecolors, and old
            comments and debug statements.
04-02-2025  Enable execution of this script, for feature testing. Add option to
            revert color of the selected shape to default (black).
10-14-2025  Detect if user is deleting the only shape. Add ShapeCanvas
            list attribute: multi_select.
10-18-2025  Implement delete-last for 'lines' mode and 'freehand' mode, using
            Ctrl-F or -L. Add handle_key() to DrawCanvas.
10-21-2025  Add function return types.
10-23-2025  In line mode, shape (set of lines) to be ended without connecting
            to the first point.
10-25-2025  Implement delete-all for either mode, using Ctrl-Shift-F or -L.
10-30-2025  Add drag to the options for multi-selected shapes.
10-31-2025  Add resize to the options for multi-selected shapes.
"""
"""
TODO
    ShapeCanvas
      1. re-order the methods
      2. document event-detection that uses .bind vs .master.bind vs handle_key()
      3. for ShapeCanvas, multi-select shapes:
         - currently: Control + R-mouse
         - ? Shift + Control + R-mouse (state=5)
         - ? should this use .bind or be in the handle_key method
    General 
      1. Set defaults (highlight color, default shape color...)
         - ? signal these to the user / allow user to set
"""
import tkinter as tk


class MyCanvas(tk.Canvas):
    """
    MyCanvas : Defines a tk Canvas with some default attributes.

    Extends: tk.Canvas

    Attributes:
        firstx (int): x location of initial L-click
        firsty (int): y location of initial L-click

        startx (int): x location of L-click
        starty (int): y location of L-click

        previousx (int): x location of prevoius L-click
        previousy (int): y location of prevoius L-click

        points (list of int): list of x,y locations

    Methods:
        report_cursor_posn: display x,y cursor location as text
        clear_cursor_posn: delete cursor location text
        set_start: upon L-mouse click, store x,y cursor location
    """
    def __init__(self, parent,
                 # mode='',
                 width=320,
                 height=320,
                 background='#ffa'
                 ):
        """
        Creates an instance of the MyCanvas class.

        Args:
            width (int): Width of the canvas in pixels
            height (int): Height of the canvas in pixels
            background (str): Canvas background color
        """
        self.width = width
        self.height = height
        self.background = background

        super().__init__(parent, width=self.width, height=self.height, background=self.background)

        self.firstx = 0
        self.firsty = 0
        self.startx = 0
        self.starty = 0
        self.previousx = 0
        self.previousy = 0
        self.points = []

        self.bind("<Motion>", self.report_cursor_posn)
        self.bind("<Leave>", self.clear_cursor_posn)

        def point_init(thispoint, xval: int, yval: int):
            thispoint.xval = xval
            thispoint.yval = yval
        self.Point = type('Point', (), {"__init__": point_init})

    def report_cursor_posn(self, event) -> None:
        """Display x,y cursor position at lower right of the canvas."""
        self.delete('text1')
        self.update()
        width = self.winfo_width()
        height = self.winfo_height()

        # print(f'w,h: {self.width}, {self.height}, ---- {self.winfo_width()}, {self.winfo_height()}')
        self.create_text(width - 28,
                         height - 10,
                         fill='blue',
                         text=str(event.x) + ',' + str(event.y),
                         tags='text1')

    def clear_cursor_posn(self, event) -> None:
        """Remove displayed cursor position from the canvas."""
        self.delete('text1')

    def set_start(self, event) -> None:
        """Sets the coordinates of first, previous and start cursor locations.

        Args:
            event (event): L-mouse click

        The following instance attributes are set:
        - firstx, firsty: clicked at the beginning of an interactive session.
        - startx, starty: the last location clicked.
        - previousx, previousy: the next-to-last location clicked.
        """
        if self.firstx == 0 and self.firsty == 0:
            self.firstx, self.firsty = event.x, event.y
            self.previousx, self.previousy = event.x, event.y
        else:
            self.previousx, self.previousy = self.startx, self.starty

        self.startx, self.starty = event.x, event.y

        self.points.append(self.Point(event.x, event.y))


class DrawCanvas(MyCanvas):
    """
    DrawCanvas : a tk Canvas for interactive drawing.

    Extends: MyCanvas

    Attributes:
        linecolor (str): color of line created on the canvas
        line_count (int): number of lines created
        linetags (list of str): list of tags for each line object

    Methods:
        draw_line: create a line from previous to current point
        double_click: create a line from current to starting point
        undo_line: remove last-drawn line
        draw_path: create a series of lines following the cursor
    """
    def __init__(self, parent,
                 mode='lines',
                 # linewidth=1,
                 **kwargs
                 ):
        """
        Creates an instance of the DrawCanvas class.

        Args:
            mode (str): Type of interaction with canvas, e.g. drawing lines
            linewidth (int): Width of line for creating lines and shapes
            width (int): Width of the canvas in pixels
            height (int): Height of the canvas in pixels
            background (str): Canvas background color
        """
        self.mode = mode
        self.linewidth = kwargs.get('linewidth')
        self.width = kwargs.get('width')
        if 'height' in kwargs.keys():
            self.height = kwargs.get('height')
        else:
            self.height = 200
        self.background = kwargs.get('background')

        super().__init__(parent, width=self.width, height=self.height, background=self.background)

        self.linecolor = 'black'
        self.line_count = 0
        self.linetags = []
        self.last_line = []
        self.last_shape = []

        match self.mode:
            case 'freehand':
                self.bind('<Button-1>', self.set_start)
                self.bind('<Button1-Motion>', self.draw_line)
                self.bind('<ButtonRelease-1>', self.reset_line)
                # works:
                # self.master.bind('<Control-Delete>', self.erase_drawing)
            case 'lines':
                self.bind('<Button-1>', self.draw_line)
                self.bind('<Double-1>', self.connect_lines)
                self.bind('<Button-3>', self.undo_line)

                # works:
                # self.master.bind('<Key>', self.handle_key)
        # works for both modes,
        # if erase_drawing finds the matching DrawCanvas instance:
        self.master.bind('<Key>', self.handle_key)

    def draw_line(self, event) -> None:
        """If past starting posn, draw a line from previous to current posn."""
        if self.firstx == 0 and self.firsty == 0:
            self.set_start(event)
            return

        print(f'in draw_line:  {event.state=}')
        self.line_count += 1
        tagname = 'line' + str(self.line_count)
        self.create_line(self.startx, self.starty,
                         event.x, event.y,
                         fill=self.linecolor,
                         width=self.linewidth,
                         tags=tagname)

        self.linetags.append(tagname)
        # remember the tag so the line can be deleted
        self.last_line.append(tagname)
        # print(f'{self.last_line[:3]=}, {self.last_line[-3:]=}')

        self.set_start(event)

        # If Control, end the line(s) without closing.
        # The unclosed "shape" can still be deleted
        if event.state == 4:
            self.firstx, self.firsty = 0, 0
            self.last_shape = self.linetags.copy()
            self.points = []
            self.linetags = []

    def connect_lines(self, event) -> None:
        """In lines mode, handle double-L click: draw lines to close a shape.

        First, the single-click handler draws a line from the current position
        to the start posn. Then, this handler draws a line from the current to
        the previous position.
        """
        self.line_count += 1
        tagname = 'line' + str(self.line_count)
        self.create_line(event.x, event.y,
                         self.firstx, self.firsty,
                         fill=self.linecolor,
                         width=self.linewidth,
                         tags=tagname)
        self.linetags.append(tagname)

        self.firstx, self.firsty = 0, 0

        # remember the tags so the shape (set of lines) can be deleted
        self.last_shape = self.linetags.copy()

        # the current shape is closed, re-initialize lists
        self.points = []
        self.linetags = []

    def undo_line(self, event) -> None:
        """Remove last line and make previous cursor posn the current posn."""
        if (self.firstx, self.firsty) == (0, 0):
            return

        if len(self.linetags) > 0:
            self.delete(self.linetags[-1])
            self.linetags.pop()
        if len(self.points) > 0:
            self.points.pop()
            if len(self.points) >= 1:
                self.startx, self.starty = self.points[-1].xval, self.points[-1].yval

    def reset_line(self, event) -> None:
        """In freehand mode, handle mouseup: complete a line."""
        print('in reset_line...')
        # print(f'{self=}')

        self.last_line = self.linetags.copy()
        self.linetags = []
        print(f'    {self.last_line[:3]=}')

    def erase_drawing(self,
                      event,
                      drawtype='freehand') -> None:
        """Delete the last line or set of lines, depending on mode."""
        ch = self.master.winfo_children()
        ch_canv = [c for c in ch if c.__class__ == DrawCanvas]
        # print(f'{ch_canv=}')

        if drawtype == 'freehand':
            for m, cnv in enumerate(ch_canv):
                # print(f'{cnv.mode=}, {cnv.last_line=}')
                if cnv.mode == 'freehand':
                    for n, item in enumerate(cnv.last_line):
                        cnv.delete(item)
                    cnv.last_line = []

        else:
            for m, cnv in enumerate(ch_canv):
                # print(f'{cnv.mode=}, {cnv.last_shape=}')
                if cnv.mode == 'lines':
                    for n, item in enumerate(cnv.last_shape):
                        cnv.delete(item)
                    cnv.last_shape = []

    def erase_all(self,
                  event,
                  drawtype='freehand') -> None:
        """Delete all lines or sets of lines, depending on mode."""
        ch = self.master.winfo_children()
        ch_canv = [c for c in ch if c.__class__ == DrawCanvas]

        for m, cnv in enumerate(ch_canv):
            # print(f'{cnv.mode=}, {cnv.last_line=}')
            if cnv.mode == drawtype:
                drawings = cnv.find_all()
                # print(f'{drawings=}')
                for item in drawings:
                    cnv.delete(item)

                cnv.last_line = []

    def handle_key(self, event) -> None:
        """Handle keypress with optional modifier.

        states: Shift is 1, Control is 4, Alt is 8
        This version does not differentiate between L and R modifier keys.
        """
        # print('in handle_key:')
        # print(f'    {event.keysym=}')
        match event.state:
            case 4:
                # Control
                # print(f'Control ({event.state}), {event.keysym}')
                match event.keysym:
                    case 'l' | 'L':
                        print(f'    Ctrl-L')
                        self.erase_drawing(event, 'lines')
                    case 'f' | 'F':
                        print(f'    Ctrl-F')
                        self.erase_drawing(event, 'freehand')
                    case _:
                        print(f'    not handled: Ctrl + {event.keysym}')
            case 5:
                # print(f'{event.state=}, {event.keysym=}')
                match event.keysym:
                    case 'f' | 'F':
                        print(f'    Ctrl-Shift-F')
                        self.erase_all(event, 'freehand')
                    case 'l' | 'L':
                        print(f'    Ctrl-Shift-L')
                        self.erase_all(event, 'lines')


class Shape():
    def __init__(self, id, center=[0, 0], lc='black'):
        self.id = id
        self.center = center
        self.linecolor = lc


class ShapeCanvas(MyCanvas):
    """
    ShapeCanvas : a tk Canvas for creating shapes.

    Extends: MyCanvas

    Attributes:
        linecolor (str): color of line created on the canvas
        shapetags (list of str): list of the tags for each shape object
        shape_centers (list of tuple): list of x,y locations for the center of each shape
        next_shape (str): name of the next shape to be added
        selected (int): id of the current shape object

    Methods:
        calc_location: determine size and location for next object to be defined
        create_shape: define and create a new shape object
        set_shape: setup for create_shape, manage shape attributes
        drag_shape: interactively move shape with the mouse
        nudge_shape: move shape 1 pixel with arrow key
        resize_shape: interactively change shape size
        toggle_selection: call function to set the 'current' shape object
        get_and_report_center:
        select_shape: make the shape nearest the cursor the current
        unselect_shape: reset current to the last-created shape
        get_and_report_center: display current shape's center x,y
    """
    def __init__(self, parent,
                 **kwargs
                 ):
        # self.__dict__.update(kwargs)
        """
        Creates an instance of the ShapeCanvas object.

        Args:
            linewidth (int): Width of line for creating lines and shapes
            width (int): Width of the canvas in pixels
            height (int): Height of the canvas in pixels
            background (str): Canvas background color
        """
        self.linewidth = kwargs.get('linewidth')
        self.width = kwargs.get('width')
        self.height = kwargs.get('height')
        self.background = kwargs.get('background')
        self.motionx = 0
        self.motiony = 0

        super().__init__(parent, width=self.width, height=self.height, background=self.background)

        self.linecolor = 'black'
        self.shapetags = []
        self.next_shape = 'oval'
        self.selected = None
        self.multi_selected = []

        self.objlist = []

        self.oval_width = 20
        self.oval_height = 25

        self.rect_width = 25
        self.rect_height = 20

        self.arc_width = 30
        self.arc_height = 25

        self.bind('<Button-1>', self.setup_shape)
        self.bind('<Shift-Motion>', self.drag_shape)
        self.bind('<Alt-Motion>', lambda ev, c=True: self.drag_shape(ev, c))
        self.bind('<Control-Motion>', self.resize_shape)
        # works:
        # self.bind('<Button-3>', lambda ev: self.toggle_selection(ev))
        # works:
        self.bind('<Button-3>', self.toggle_selection)
        # self.bind('<Control-Button-3>', self.multi_select)
        self.bind('<Control-Button-3>', self.toggle_multi_select)
        self.master.master.bind('<Key>', self.handle_key)

        # With a Frame added to the object heirarchy, we have to bind to
        # the top-level object.
        self.master.master.bind('<Shift-Up>',
                                lambda ev,
                                       h=0,
                                       v=-1: self.nudge_shape(ev, h, v))
        self.master.master.bind('<Shift-Down>',
                                lambda ev,
                                       h=0,
                                       v=1: self.nudge_shape(ev, h, v))
        self.master.master.bind('<Shift-Left>',
                                lambda ev,
                                       h=-1,
                                       v=0: self.nudge_shape(ev, h, v))
        self.master.master.bind('<Shift-Right>',
                                lambda ev,
                                       h=1,
                                       v=0: self.nudge_shape(ev, h, v))

    def toggle_multi_select(self, event) -> None:
        # print(f'in multi_select: {event.state=}')

        self.toggle_selection(event)
        # print(f'    {self.selected=}')
        the_id = self.selected

        # set selection indicator
        self.itemconfigure(the_id, outline='grey')

        # print(f'    start: {self.multi_selected=}')
        if the_id in self.multi_selected:
            self.multi_selected.remove(the_id)
            # reset linecolor to original
            lc = ''
            for n, shape in enumerate(self.objlist):
                if shape.id == the_id:
                    lc = self.objlist[n].linecolor
            # print(f'    {lc=}')
            if lc != '':
                self.itemconfigure(the_id, outline=lc)
        else:
            self.multi_selected.append(the_id)
            self.selected = self.multi_selected[-1]

    def calc_location(self, shape) -> tuple:
        """Calculate size and location of the next shape to be defined.

        Args:
            shape (str): name description of the shape
        Return:
            (tuple): starting location x,y
        """
        start, end = 0, 0

        match shape:
            case 'oval':
                xwidth, ywidth = self.oval_width, self.oval_height
                start = self.startx - xwidth, self.starty - ywidth
                end = self.startx + xwidth, self.starty + ywidth
            case 'rectangle':
                xwidth, ywidth = self.rect_width, self.rect_height
                start = self.startx - xwidth, self.starty - ywidth
                end = self.startx + xwidth, self.starty + ywidth
            case 'arc':
                xwidth, ywidth = self.arc_width, self.arc_height
                start = self.startx - xwidth, self.starty - ywidth
                end = self.startx + xwidth, self.starty + ywidth

        return start, end

    def create_shape(self,
                     shape='oval',
                     linecolor='black',
                     width=1,
                     tag='oval'):
        """Create a new shape object on the canvas.

        Args:
            shape (str): name description of the shape
            linecolor (str): color for drawing
            width (int): width of the line drawn
            tag (str): tag assigned to the object, indicating its type
        """
        id1 = None

        match shape:
            case 'oval':
                taglist = ['oval', tag]
                s, e = self.calc_location('oval')
                id1 = self.create_oval(s,
                                       e,
                                       outline=linecolor,
                                       width=width,
                                       tags=taglist)
            case 'rectangle':
                taglist = ['rectangle', tag]
                s, e = self.calc_location('rectangle')
                id1 = self.create_rectangle(s,
                                            e,
                                            outline=linecolor,
                                            width=width,
                                            tags=taglist)
            case 'arc':
                taglist = ['arc', tag]
                s, e = self.calc_location('arc')
                id1 = self.create_arc(s,
                                      e,
                                      outline=linecolor,
                                      width=width,
                                      start=90,
                                      extent=90,
                                      tags=taglist)
            case _:
                pass

        return id1

    def set_next_tag(self, current_tag) -> int:
        # find the number of tags that include the string current_tag
        # print(f'{current_tag=}')
        found_list = [t for t in self.shapetags if current_tag in t]

        return len(found_list)

    def setup_shape(self, event) -> None:
        """Set up parameters for creating a new shape on the canvas.

        Args:
            event (event): L-mouse button

        Gather parameters from instance attributes, call create_shape(),
        manage the list of existing shape objects and their basic attributes.
        """
        self.set_start(event)

        this_tag = self.next_shape + str(len(self.shapetags) + 1)

        id1 = self.create_shape(shape=self.next_shape,
                                linecolor=self.linecolor,
                                width=self.linewidth,
                                tag=this_tag)
        if id1 is not None:
            self.shapetags.append(this_tag)
            this_center = [self.startx, self.starty]

            # print(f'set center: {this_center}')
            self.report_center(this_center, self.linecolor)
            self.selected = id1
            print(f'{self.shapetags=}')
            tags = self.itemcget(id1, 'tags')
            print(f'new shape {tags=}')

            self.motionx, self.motiony = self.startx, self.starty

            newshape = Shape(id1, [self.startx, self.starty], self.linecolor)
            self.objlist.append(newshape)
            next_tag = self.set_next_tag(self.next_shape)
            print(f'{next_tag=}')

    def handle_key(self, event) -> None:
        """Handle keypress with optional modifier.

        states: Shift is 1, Control is 4, Alt is 8
        This version does not differentiate between L and R modifier keys.
        """
        match event.state:
            case 1:
                # Shift
                print(f'Shift ({event.state}), {event.keysym}')
                match event.keysym:
                    case 'x' | 'X':
                        print(f'    x')
                    case _:
                        print(f'    not handled: {event.keysym}')
            case 4:
                # Control
                print(f'Control ({event.state}), {event.keysym}')
                match event.keysym:
                    case 'd':
                        print(f'    d: duplicate selected shape')
                        the_id = self.selected
                    case 'x':
                        # Delete selected shape
                        print(f'    x: delete selected shape')

                        # ? don't need this unless we are deleting all shapes
                        # (a future option, perhaps with a different key)
                        idlist = [i.id for i in self.objlist]

                        the_id = self.selected
                        self.delete(the_id)
                        whichone = next((n for n in self.objlist if n.id == the_id), None)
                        self.objlist.remove(whichone)

                        # reset selected to the last-created object, if any
                        if len(self.objlist) > 0:
                            self.selected = self.objlist[-1].id
                            idlist = [i.id for i in self.objlist]
                    case _:
                        print(f'    not handled: {event.keysym}')
            case 8:
                # Alt
                print(f'Alt ({event.state}), {event.keysym}')
                match event.keysym:
                    case 'x':
                        print(f'    x')
                        self.set_to_black('black')
                    case _:
                        print(f'    not handled: {event.keysym}')
            case 3 | 6 | 10:
                # Caps Lock has a state value of 2, so this case reflects
                # Caps Lock plus the modifier
                print('is Caps Lock on?')
            case _:
                pass

    def drag_shape(self, event, constrain=False):
        """Interactively moves a shape object on the canvas.

        Args:
            event (event): L-mouse + motion
            constrain (boolean): coerces motion to vertical or horizontal by
                ignoring 1-pixel shifts in x or y, respectively.
        """
        dx = 0
        dy = 0
        shift = 1
        self.report_cursor_posn(event)

        # ? not needed
        # this_tag = self.gettags(self.selected)[1]

        # this_index = self.shapetags.index(this_tag)
        # center_posn = self.shape_centers[this_index]
        whichone = next(n for n in self.objlist if n.id == self.selected)
        center_posn = whichone.center

        if constrain:
            x_difference = abs(event.x - self.previousx)
            y_difference = abs(event.y - self.previousy)
            if x_difference > (y_difference + 1):
                if event.x > self.previousx: dx = shift
                if event.x < self.previousx: dx = -shift
            if y_difference > (x_difference + 1):
                if event.y > self.previousy: dy = shift
                if event.y < self.previousy: dy = -shift
        else:
            if event.x > self.previousx: dx = shift
            if event.x < self.previousx: dx = -shift
            if event.y > self.previousy: dy = shift
            if event.y < self.previousy: dy = -shift

        self.previousx = event.x
        self.previousy = event.y

        if len(self.multi_selected) > 0:
            for n, item in enumerate(self.multi_selected):
                self.move(item, dx, dy)
            theshape = self.multi_selected[-1]
        else:
            theshape = self.selected
            self.move(theshape, dx, dy)

        coords_float = self.coords(theshape)
        coords = [int(n) for n in coords_float]
        # center_posn['x'] = coords[0] + 20
        # center_posn['y'] = coords[1] + 20
        center_posn[0] = coords[0] + 20
        center_posn[1] = coords[1] + 20

        t = self.gettags(self.selected)[1]

        outline = self.itemcget(self.selected, 'outline')
        self.report_center(center_posn, outline)

    def nudge_shape(self, event, dx, dy) -> None:
        """Move the selected shape object by one pixel, in one of 4 directions.

        Args:
            event (event): Shift key + arrow key
            dx (int): number of pixels to move horizontally
            dy (int): number of pixels to move vertically
        """
        # mydrawcanvas.focus_set()
        theshape = self.selected
        self.move(theshape, dx, dy)

        # tags = self.gettags(theshape)[1]
        # whichone = self.shapetags.index(tags)
        # c = self.shape_centers[whichone]
        # c['x'] += dx
        # c['y'] += dy

        whichone = next(n for n in self.objlist if n.id == self.selected)
        whichone.center = list(sum(n) for n in zip(whichone.center, (dx, dy)))

        outline = whichone.linecolor
        self.report_center(whichone.center, outline)

    def resize_shape(self, event):
        """Interactively enlarge the selected shape.

        Args:
            event (event): L-mouse button + Control key
        """
        print('in resize_shape...')
        if self.selected is None: return
        theshape = self.selected
        this_tag = self.gettags(theshape)[1]
        # ? don't need this
        this_index = self.shapetags.index(this_tag)
        # center_posn = self.shape_centers[this_index]
        whichone = next(n for n in self.objlist if n.id == self.selected)
        center_posn = whichone.center

        print(f'    {center_posn=}')

        if theshape in self.multi_selected:
            group = [n for n in self.objlist if n.id in self.multi_selected]

            for n, item in enumerate(group):
                if event.y < self.motiony:
                    self.scale(item.id, item.center[0], item.center[1], 1.01, 1.01)

                if event.y > self.motiony:
                    self.scale(item.id, item.center[0], item.center[1], 0.99, 0.99)
        else:
            if event.y < self.motiony:
                # self.scale(theshape, center_posn['x'], center_posn['y'], 1.01, 1.01)
                self.scale(theshape, center_posn[0], center_posn[1], 1.01, 1.01)

            if event.y > self.motiony:
                # self.scale(theshape, center_posn['x'], center_posn['y'], 0.99, 0.99)
                self.scale(theshape, center_posn[0], center_posn[1], 0.99, 0.99)

        self.motionx, self.motiony = event.x, event.y

    def get_and_report_center(self) -> None:
        """Get center of current shape and call a class method to report it."""

        whichone = next(n for n in self.objlist if n.id == self.selected)
        center = whichone.center
        outline = whichone.linecolor

        self.report_center(center, outline)

    def set_to_black(self, color) -> None:
        self.itemconfig(self.selected, outline=color)

        whichone = next(n for n in self.objlist if n.id == self.selected)
        whichone.linecolor = color

    def toggle_selection(self, event) -> None:
        """Assign one shape to be the currently selected shape."""
        if event.state == 1:
            # Shift key pressed
            # print(f'toggle_selection:    {event.state=}, unselecting...')
            self.unselect_shape(event)
        else:
            # print(f'toggle_selection:    {event.state=}, selecting...')
            self.select_shape(event)

        return

    def unselect_shape(self, event) -> None:
        """Revert selected shape to the last one created, or None.

        Args:
            event (event): Shift key + R-mouse click
        """
        # TODO: handle the case of the last shape deleted (after delete is implemented)
        for n, item in enumerate(self.shapetags):
            self.itemconfigure(item, fill='')

        # set selected item to be the last created
        lastid = self.find_withtag(self.shapetags[-1])[0]
        self.itemconfigure(lastid, fill='#ffa')
        self.after(500, lambda: self.itemconfigure(lastid, fill=''))
        self.selected = lastid

        self.get_and_report_center()

    def select_shape(self, event) -> None:
        """Sets the shape nearest the cursor as the 'selected' shape.

        Args:
            event (event): R-mouse click

        A class attribute keeps track of the currently selected shape, by its id. The
        shape is highlighted with a color fill.
        """
        print(f'{event.state=}')

        # remove lighlight from all shapes
        for item in enumerate(self.shapetags):
            self.itemconfigure(item[1], fill='')

        found = self.find_closest(event.x, event.y, halo=25)
        print(f'{found=}')
        if len(found) > 0:
            self.selected = found[0]
            print(f'{self.selected=}')

            # highlight the seleced shape
            self.itemconfigure(self.selected, fill='#ffa')
            self.after(500, lambda: self.itemconfigure(self.selected, fill=''))
            self.get_and_report_center()
        else:
            print('no object found')
        print('returning from select_shape...')

        return

    def report_center(self,
                      center: dict,
                      color: str) -> None:
        """Report center x,y coordinates for a shape.

        Args:
            center (dict): coordinates as Int
            color (str): color for the text report
        """
        self.delete('center_text')
        textstr = f'{center[0]}, {center[1]}'

        self.create_text(10,
                         12,
                         fill=color,
                         text=textstr,
                         anchor='w',
                         tags='center_text')

    # NOT CURRENTLY USED
    def set_shape_parameter(self, p, val):
        self.__dict__[p] = val


if __name__ == '__main__':
    root = tk.Tk()
    canvas_frame = tk.Frame(root)
    mydrawcanvas = DrawCanvas(canvas_frame,
                              width=400,
                              height=500,
                              mode='freehand',
                              background='cyan'
                              )
    mydrawcanvas.grid(column=0, row=0)
    myshapecanvas = ShapeCanvas(canvas_frame,
                                width=400,
                                height=500,
                                background='cyan'
                                )
    myshapecanvas.grid(column=1, row=0)
    canvas_frame.grid(column=0, row=0)
    root.mainloop()
