"""
module: canvas_classes.py

purpose: Defines child classes of tkinter Canvas.

comments: No Artificial Intelligence was used in production of this code.

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
10-30-2025  Add drag to the options for multi-selected shapes.d
10-31-2025  Add resize to the options for multi-selected shapes.
11-12-2025  For ShapeCanvas, Control+x now deletes all multi-selected shapes.
11-14-2025  For ShapeCanvas, nudge now moves all selected shapes.
11-24-2025  Rename nudge_shape to nudge_location. Add callbacks to delete,
            duplicate, select single or reveal selected shape.
11-30-2025  Trial implementation: bind to nudge_location with no arguments,
            and let the fxn move the object based on keysym=Up/Down/Left/Right.
            Add nudge_size function.
12-03-2025  For ShapeCanvas, Refactor nudge_size() to be more efficient.
            Combine "Key" event with modifiers, for handle_key().
12-11-2025  Handle modifier keys with handle_key(). Refactor drag_shape().
02-06-2025  For ShapeCanvas, add guard statements to shape manipulation functions.
02-11-2026  In ShapeCanvas, reorder some methods; set_to_color now sets outline
            for the closest shape, not the selected one.
02-12-2026  Remove old code, update inline docs.
02-16-2026  Remove Alt-S to select shape. Add set_focus to report_cursor_posn
            so key-bound functions can read the event in the ShapeCanvas.
02-17-2026  For ShapeCanvas, in toggle_multi_select, remove highlight for
            selected shape. (May not happen in select_shape, due to timing.)
02-19-2026  For ShapeCanvas, handle the arrow shape.
02-20-2026  For ShapeCanvas, debug set_to_color() to require canvas focus.
02-23-2026  For ShapeCanvas, replace get_and_report_center() wih report_shape().
            report_size() now assumes the selected object. Remove redundant
            print statements in handle_key().
03-05-2026  Refactor handle_key().
03-09-2026  Update most class docstrings, add docstrings for some methods,
            remove some old code.
03-16-2026  set_to_black() is now set_to_color(). Refactor DrawCanvas
            handle_key method. Move docstring notes to a scratch file.
"""
import tkinter as tk


class MyCanvas(tk.Canvas):
    """
    MyCanvas : Defines a tk Canvas with some default attributes.

    Extends: tk.Canvas

    Attributes:
        firstx, firsty (int): First location L-clicked at the beginning of
            an interactive session.
        startx, starty (int): last location clicked.
        previousx, previousy (int): next-to-last location clicked, enables shapes
            to be automatically closed.

        Point (class): object with x (int) and y (int) attributes
        points (list of int): list of Points

    Methods:
        report_cursor_posn: display x,y cursor location as text
        clear_cursor_posn: delete cursor location text
        set_start: upon L-mouse click, store x,y cursor location
    """
    def __init__(self, parent,
                 width=320,
                 height=320,
                 background='#ffa'
                 ):
        """
        Creates an instance of the MyCanvas class.

        Args:
            width (int, optional): Width of the canvas in pixels.
                Defaults to 320.
            height (int, optional): Height of the canvas in pixels.
                Defaults to 320.
            background (str, optional): Canvas background color.
                Defaults to "#ffa".
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
        self.focus_set()
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
        self.master.focus_set()

    def set_start(self, event) -> None:
        """Sets the coordinates of first, previous and start cursor locations.

        Args:
            event (event): L-mouse click
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
                 **kwargs
                 ):

        """
        Creates an instance of the DrawCanvas class.

        Args:
            mode (str, optional): Type of interaction with canvas.
                Defaults to "lines".
            **kwargs: Arbitrary keyword arguments.
                linewidth (int): Width of line for creating lines and shapes
                width (int): Width of the canvas in pixels
                height (int, optional): Height of the canvas in pixels.
                    Defaults to 200.
                background (str, optional): Canvas background color.
                    Defaults to "white".
        """
        self.mode = mode
        self.linewidth = kwargs.get('linewidth', 2)
        self.width = kwargs.get('width', 300)
        self.height = kwargs.get('height', 300)
        self.background = kwargs.get('background', 'white')

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
                # works, direct bind for a key combination:
                # self.master.bind('<Control-Delete>', self.erase_drawing)
            case 'lines':
                self.bind('<Button-1>', self.draw_line)
                self.bind('<Double-1>', self.connect_lines)
                self.bind('<Button-3>', self.undo_line)

                # works, direct bind for a single key:
                # self.master.bind('<Key>', self.handle_key)
        # works for both modes,
        # if erase_drawing finds the matching DrawCanvas instance:
        self.master.bind('<Key>', self.handle_key)

    def handle_key(self, event) -> None:
        """Handle keypress with optional modifier key.

        states: Shift is 1, Control is 4, Alt is 8
        This version does not differentiate between L and R modifier keys.
        """
        modifiers = {0: 'None', 1: 'Shift', 4: 'control', 8: 'Alt'}
        print(f'keys pressed: {modifiers[event.state]} + {event.keysym}')

        match event.state:
            case 4:
                # Control
                match event.keysym:
                    case 'f' | 'F':
                        print(f'    erase freeehand drawing')
                        self.erase_drawing(event, 'freehand')
                    case 'l' | 'L':
                        print(f'    erase line drawing')
                        self.erase_drawing(event, 'lines')
                    case _:
                        print(f'    not handled')
            case 5:
                # Control + Shift ??
                match event.keysym:
                    case 'f' | 'F':
                        print(f'    erase all freehand')
                        self.erase_all(event, 'freehand')
                    case 'l' | 'L':
                        print(f'    erase all lines')
                        self.erase_all(event, 'lines')
            case _:
                # No Modifier Key
                print(f'...other key...{event.keysym}, {event.state=}')
                # print(f'    Alt + {event.keysym}, {event.state=}, ')

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

        After the single-click handler has drawn a line from the current
        position to the start posn, this handler draws a line from the current
        to the previous position.
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

        # Remember tags so the shape (most recent set of lines) can be deleted.
        self.last_shape = self.linetags.copy()

        # The current shape is completed.
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

        self.last_line = self.linetags.copy()
        self.linetags = []
        print(f'    {self.last_line[:3]=}')

    def erase_drawing(self,
                      event,
                      drawtype='freehand') -> None:
        """Delete the last line or set of lines, depending on mode."""
        ch = self.master.winfo_children()
        ch_canv = [c for c in ch if c.__class__ == DrawCanvas]

        if drawtype == 'freehand':
            for m, cnv in enumerate(ch_canv):
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
            if cnv.mode == drawtype:
                drawings = cnv.find_all()
                for item in drawings:
                    cnv.delete(item)

                cnv.last_line = []


class Shape():
    def __init__(self, id, center=[0, 0], lc='black'):
        self.id = id
        self.center = center
        self.linecolor = lc


class ShapeCanvas(MyCanvas):
    """
    ShapeCanvas : a tk.Canvas for creating shapes.

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
        nudge_location: move shape 1 pixel with arrow key
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
        """
        Creates an instance of the ShapeCanvas object.

        Args:
            **kwargs: Arbitrary list of keyword arguments.
                linewidth (int): Width of line for creating lines and shapes
                width (int): Width of the canvas in pixels
                height (int): Height of the canvas in pixels
                background (str): Canvas background color
        """
        self.linewidth = kwargs.get('linewidth', 2)
        self.width = kwargs.get('width', 300)
        self.height = kwargs.get('height', 300)
        self.background = kwargs.get('background', 'white')

        super().__init__(parent, width=self.width, height=self.height, background=self.background)

        self.motionx = 0
        self.motiony = 0
        self.linecolor = 'black'
        self.shapetags = []
        self.next_shape = 'oval'
        self.selected = None

        self.multi_selected: [int] = []
        self.objlist: [Shape] = []

        self.oval_width = 20
        self.oval_height = 20

        self.rect_width = 20
        self.rect_height = 20

        self.arrow_width = 20
        self.arrow_height = 20

        self.bind('<Button-1>', self.setup_shape)
        self.bind('<Shift-Motion>', self.drag_shape)
        # constrain to horizontal/vertical. Responds slowly...
        # self.bind('<Alt-Motion>', lambda ev, c=True: self.drag_shape(ev, c))
        self.bind('<Control-Motion>', self.resize_shape)
        self.bind('<Button-3>', self.toggle_selection)
        self.bind('<Control-Button-3>', self.toggle_multi_select)

        # If the Canvas is contained in a Frame, need another layer:
        # self.master.master.bind...
        self.master.bind('<Shift-Key>', self.handle_key)
        self.master.bind('<Control-Key>', self.handle_key)
        self.master.bind('<Alt-Key>', self.handle_key)

        self.master.bind('<Control-Up>', self.nudge_size)
        self.master.bind('<Control-Down>', self.nudge_size)

        # Any key without modifier
        # self.master.bind('<Key>', self.handle_key)


    def handle_key(self, event) -> None:
        """Handle keypress with optional modifier key.

        states: Shift is 1, Control is 4, Alt is 8
        This version does not differentiate between L and R modifier keys.
        """
        # works: alternate way to get the modifier key
        # if event.state & 0x1:
        #     print('    Shift')
        # if event.state & 0x4:
        #     print('    Control')
        # if event.state & 0x8:
        #     print('    Alt')
        # print(f'{type(event.state)=}')
        modifiers = {1: 'Shift', 4: 'control', 8: 'Alt'}
        print(f'keys pressed: {modifiers[event.state]} + {event.keysym}')
        # , {event.x}, {event.y}

        match event.state:
            case 1:
                # Shift
                match event.keysym:
                    case 'x' | 'X':
                        print(f'    not handled')
                    case 'h' | 'H':
                        print(f'    not handled')
                    case 'Left' | 'Right' | 'Up' | 'Down':
                        self.nudge_location(event)
                    case _:
                        print(f'    {event.keysym} not handled')
            case 4:
                # Control
                match event.keysym:
                    case 'd':
                        print('    duplicate selected shape')
                        the_id = self.selected
                        prev_shape = self.itemcget(the_id, 'tags').split(' ')[0]
                        prev_obj = next((obj for obj in self.objlist if obj.id == the_id), None)

                        newid = self.create_shape(prev_shape, prev_obj.linecolor, self.linewidth, 'oval2')
                        coords = self.coords(the_id)

                        # Is this check necessary if we are using .coords?
                        # is there an object of this type at this location?
                        if len(self.objlist) > 1:
                            # print(f'{self.objlist[-2].id=}')
                            t = self.gettags(self.objlist[-2].id)

                        coords_new = [n + 20 for n in coords]

                        lastid = self.objlist[-1].id
                        lastcoords = self.coords(lastid)
                        newsize = [prev_obj.center[0] + 20, prev_obj.center[1] + 20]

                        # If already an object at this location, offset again.
                        if lastcoords == coords_new:
                            coords_new = [n + 20 for n in coords_new]
                            newsize = [newsize[0] + 20, newsize[1] + 20]

                        self.coords(newid, coords_new)

                        # newsize = [prev_obj.center[0] + 20, prev_obj.center[1] + 20]
                        newshape = Shape(newid, newsize, self.linecolor)
                        self.objlist.append(newshape)

                    case 'r':
                        print('    release multi-selection')
                        self.release_multi_selection(event)
                        self.show_selected()
                    case 'x':
                        # Delete selected shape
                        print(f'    delete selected shape')

                        # ? don't need this unless we are deleting all shapes
                        all_ids = [i.id for i in self.objlist]
                        # print(f'    {all_ids=}')

                        if len(self.multi_selected) > 0:
                            idlist = [i for i in self.multi_selected]
                            print(f'    {idlist=}')
                            print(f'    {self.objlist=}')
                            for n, item in enumerate(idlist):
                                self.delete(item)
                                whichone = next((obj for obj in self.objlist if obj.id == item), None)
                                print(f'    remove obj: {whichone=}')
                                self.objlist.remove(whichone)
                        else:
                            the_id = self.selected
                            self.delete(the_id)
                            whichone = next((n for n in self.objlist if n.id == the_id), None)
                            self.objlist.remove(whichone)

                        # reset selected to the last-created object, if any
                        if len(self.objlist) > 0:
                            self.selected = self.objlist[-1].id
                            idlist = [i.id for i in self.objlist]
                    case _:
                        print(f'    not handled')
            case 8:
                # Alt
                print(f'Alt + {event.keysym}, {event.state=}, ')
                match event.keysym:
                    case 'r':
                        print(f'    reveal selected shape at: {event.x}, {event.y}')
                        self.show_selected()
                    # case 's':
                    #     print(f'    select shape {event.x}, {event.y}')
                    #     self.select_shape(event)
                    case 'b':
                        print(f'    set linecolor to black at: {event.x}, {event.y}')
                        self.set_to_color(event, 'black')
                    case 'c':
                        print(f'    set linecolor to current color at: {event.x}, {event.y}')
                        self.set_to_color(event, self.linecolor)
                    case _:
                        print(f'    not handled')
            case 3 | 6 | 10:
                # Caps Lock has a state value of 2, so this case reflects
                # Caps Lock plus the modifier
                print('is Caps Lock on?')
            case _:
                # No Modifier Key
                print(f'...other key...{event.keysym}, {event.state=}')

    def calc_location(self, shape) -> tuple:
        """Calculate size and location of the next shape to be defined.

        Args:
            shape (str): name description of the shape
        Return:
            (tuple of int): starting x,y location
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
            case 'arrow':
                xwidth, ywidth = self.arrow_width, self.arrow_height
                start = self.startx, self.starty
                end = self.startx + (xwidth + 20), self.starty + (ywidth + 20)
            # add this back in when we begin the structured_draw app
            # case 'arc':
            #     xwidth, ywidth = self.arc_width, self.arrow_height
            #     start = self.startx - xwidth, self.starty - ywidth
            #     end = self.startx + xwidth, self.starty + ywidth

        return start, end

    def set_next_tag(self, current_tag) -> int:
        """Find the number of tags that include the string `current_tag`."""
        found_list = [t for t in self.shapetags if current_tag in t]

        return len(found_list)

    def setup_shape(self, event) -> None:
        self.set_start(event)
        """Set up parameters for creating a new shape on the canvas.

        Gather parameters from attributes of the ShapeCanvas instance, and call 
        create_shape(). Manage the list of existing shape objects and their

        Args:
            event (event): L-mouse click
        attributes.
        """

        this_tag = self.next_shape + str(len(self.shapetags) + 1)

        id1 = self.create_shape(shape=self.next_shape,
                                linecolor=self.linecolor,
                                width=self.linewidth,
                                tag=this_tag)

        if id1 is not None:
            self.bind('<B1-Motion>', lambda ev=event, id=id1: self.drag_to_size(ev, id))

            self.shapetags.append(this_tag)
            this_center = [self.startx, self.starty]

            # self.report_center(this_center, self.linecolor)
            self.selected = id1
            self.multi_selected = []

            self.motionx, self.motiony = self.startx, self.starty

            newshape = Shape(id1, [self.startx, self.starty], self.linecolor)
            self.objlist.append(newshape)
            # self.report_size(self.linecolor)
            self.report_shape()

            # enable set_to_color via the focus
            self.focus_set()

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
            case 'arrow':
                taglist = ['arrow', tag]
                s, e = self.calc_location('arrow')
                id1 = self.create_line(s,
                                       e,
                                       fill=linecolor,
                                       width=width,
                                       arrow='first',
                                       arrowshape=(10, 12, 5),
                                       tags=taglist)
            case _:
                pass

        return id1

    def drag_to_size(self, ev, id):
        """While creating a shape, drag it to the desired initial size."""
        loc = self.coords(id)
        newloc = (loc[0], loc[1], ev.x, ev.y)
        self.coords(id, newloc)

    def drag_shape(self, event, constrain=False):
        """Interactively moves a shape object on the canvas.

        Args:
            event (event): L-mouse + motion
            constrain (boolean): coerces motion to vertical or horizontal by
                ignoring 1-pixel shifts in x or y, respectively.
        """
        if self.selected is None: return
        dx = 0
        dy = 0
        shift = 1
        self.report_cursor_posn(event)

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

        # Is there any need for this?
        # t = self.gettags(self.selected)[1]

        whichone = next(n for n in self.objlist if n.id == self.selected)
        whichone.center = list(sum(n) for n in zip(whichone.center, (dx, dy)))
        outline = whichone.linecolor

        self.report_center(whichone.center, outline)

    def nudge_location(self, event) -> None:
        """Move the selected shape object by one pixel, in one of 4 directions.

        Args:
            event (event): Shift key + arrow key
        """
        if self.selected is None: return
        match event.keysym:
            case 'Up':
                dx = 0
                dy = -1
            case 'Down':
                dx = 0
                dy = 1
            case 'Left':
                dx = -1
                dy = 0
            case 'Right':
                dx = 1
                dy = 0
            case _:
                return

        if len(self.multi_selected) > 0:
            # multi-selected shape(s)
            for n, item in enumerate(self.multi_selected):
                self.move(item, dx, dy)
                self.objlist[n].center[0] += dx
                self.objlist[n].center[1] += dy
        else:
            theshape = self.selected
            self.move(theshape, dx, dy)

        whichone = next(n for n in self.objlist if n.id == self.selected)
        whichone.center = list(sum(n) for n in zip(whichone.center, (dx, dy)))
        outline = whichone.linecolor

        self.report_center(whichone.center, outline)

    def resize_shape(self, event):
        """Interactively resize the selected shape.

        Args:
            event: L Control key + mouse button
        """
        if self.selected is None: return
        theshape = self.selected
        dx = 0
        dy = 0
        whichone = next(n for n in self.objlist if n.id == self.selected)
        center_posn = whichone.center

        if len(self.multi_selected) > 0:
            group = [n for n in self.objlist if n.id in self.multi_selected]

            for n, item in enumerate(group):
                if event.y < self.motiony:
                    self.scale(item.id, item.center[0], item.center[1], 1.01, 1.01)

                if event.y > self.motiony:
                    self.scale(item.id, item.center[0], item.center[1], 0.99, 0.99)
        else:
            if event.y < self.motiony:
                # might be clearer if center_posn was a dict like this...
                # self.scale(theshape, center_posn['x'], center_posn['y'], 1.01, 1.01)
                self.scale(theshape, center_posn[0], center_posn[1], 1.01, 1.01)
            if event.y > self.motiony:
                self.scale(theshape, center_posn[0], center_posn[1], 0.99, 0.99)
        self.report_size(whichone.linecolor)

        self.motionx, self.motiony = event.x, event.y

        # outline = whichone.linecolor
        # self.report_size(self.linecolor)

    def nudge_size(self, event):
        """Interactively adjust the size of the current shape by 1 pixel."""
        if self.selected is None: return
        if len(self.multi_selected) > 0:
            objlist = self.multi_selected
        else:
            objlist = [self.selected]

        if event.keysym == "Up":
            x1 = -1
            y1 = -1
            x2 = 1
            y2 = 1
        else:
            if event.keysym == "Down":
                x1 = 1
                y1 = 1
                x2 = -1
                y2 = -1

        for n, item in enumerate(objlist):
            loc = self.coords(item)
            start_coords = list(loc)
            new_coords = (
                start_coords[0] + x1, start_coords[1] + y1, start_coords[2] + x2, start_coords[3] + y2
            )
            self.coords(item, new_coords)

        whichone = next(n for n in self.objlist if n.id == self.selected)
        self.report_size(whichone.linecolor)

    def set_to_color(self, event, color) -> None:
        """Set closest shape to a black outline."""
        # If canvas doesn't have focus, find_closest gives wrong x,y
        if self.focus_get() != self:
            print('exiting set_to_color...')
            return

        if len(self.objlist) == 0: return
        found = self.find_closest(event.x, event.y, halo=25)
        taglist = self.itemcget(found, 'tags')
        print(f'{taglist=}')
        if 'image' in self.gettags(found[0]):
            print('found image, returning...')

            return

        else:
            if 'arrow' in taglist:
                self.itemconfig(found, fill=color)
            else:
                self.itemconfig(found, outline=color)

        whichone = next(n for n in self.objlist if n.id == found[0])
        whichone.linecolor = color

    def toggle_selection(self, event) -> None:
        """Assign a shape to be the currently selected shape."""
        if event.state == 1:
            self.unselect_shape(event)
        else:
            self.select_shape(event)

        return

    def unselect_shape(self, event) -> None:
        """Revert selected shape to the last one created.

        Args:
            event (event): Shift key + R-mouse click
        """
        # TODO: handle the case of the last shape deleted.
        mark_return = False
        for n, item in enumerate(self.shapetags):
            self.itemconfigure(item, fill='')

        lastid = self.find_withtag(self.shapetags[-1])[0]
        print('unselect...')

        self.itemconfigure(lastid, fill='#ffa')

        if 'arrow' in self.gettags(lastid):
            whichone = next(n for n in self.objlist if n.id == lastid)
            self.after(500, lambda: self.itemconfigure(lastid, fill=whichone.linecolor))
        else:
            self.after(500, lambda: self.itemconfigure(lastid, fill=''))

        self.selected = lastid

        # self.get_and_report_center()
        self.report_shape()
        mark_return = True
        if mark_return: return

    def select_shape(self, event) -> None:
        """Sets the shape nearest the cursor as the 'selected' shape.

        Args:
            event: R-mouse click

        A class attribute keeps track of the currently selected shape, by its id. The
        shape is highlighted with a color fill.
        """
        # remove highlight from all shapes
        for item in enumerate(self.shapetags):
            if not 'arrow' in item[1]:
                self.itemconfigure(item[1], fill='')

        found = self.find_closest(event.x, event.y, halo=25)
        if len(found) > 0:
            # Exclude the image object, if the cursor is outside the halo.
            if 'image' in self.gettags(found[0]):
                return

            self.selected = found[0]
            print(f'    {self.selected=}')
            print(f'    {self.gettags(self.selected)=}')

            # highlight the seleced shape
            self.itemconfigure(self.selected, fill='#ffa')
            if 'arrow' in self.gettags(self.selected):
                whichone = next(n for n in self.objlist if n.id == self.selected)
                self.after(500, lambda: self.itemconfigure(self.selected, fill=whichone.linecolor))
            else:
                self.after(500, lambda: self.itemconfigure(self.selected, fill=''))
            # self.get_and_report_center()
            self.report_shape()
        else:
            print('no object found to select')

        return

    def toggle_multi_select(self, event) -> None:
        """Include or exclude the clicked shape from the list `multi_selected`."""
        if self.selected is None: return

        original_selected = self.selected
        self.select_shape(event)
        the_id = self.selected

        # set linecolor as a multi-selection indicator
        if not 'arrow' in self.gettags(the_id):
            self.itemconfigure(the_id, outline='grey')
        else:
            self.itemconfigure(the_id, fill='grey')

        if the_id in self.multi_selected:
            # print(f'    removing {the_id}')
            self.multi_selected.remove(the_id)
            # revert to the original linecolor
            lc = ''
            for n, shape in enumerate(self.objlist):
                if shape.id == the_id:
                    lc = self.objlist[n].linecolor
            if lc != '':
                if 'arrow' in self.gettags(the_id):
                    self.itemconfigure(the_id, fill=lc)
                else:
                    self.itemconfigure(the_id, outline=lc)

            # self.selected = original_selected
        else:
            # print(f'adding {the_id} to multi-selection:')
            self.multi_selected.append(the_id)
            # print(f'{self.multi_selected=}')
            # self.selected = self.multi_selected[-1]
            # self.selected = original_selected
        self.selected = original_selected

        if 'arrow' in self.gettags(self.selected):
            whichone = next(n for n in self.objlist if n.id == original_selected)
            self.after(500, lambda: self.itemconfigure(the_id, fill=whichone.linecolor))
        else:
            self.after(500, lambda: self.itemconfigure(the_id, fill=''))

    def release_multi_selection(self, event):
        """Exclude all shapes from the list `multi_selected`."""
        if self.selected is None: return

        # Restore original linecolors.
        for the_id in self.multi_selected:
            for n, shape in enumerate(self.objlist):
                if shape.id == the_id:
                    lc = self.objlist[n].linecolor
                    self.itemconfigure(the_id, outline=lc)

        self.multi_selected = []
        self.selected = self.objlist[-1].id

    def show_selected(self):
        """Momentarily highlight the selected shape."""
        # print('show_selected')
        if self.selected is None: return
        self.itemconfigure(self.selected, fill='#ffa')
        if not 'arrow' in self.gettags(self.selected):
            self.after(500, lambda: self.itemconfigure(self.selected, fill=''))
        else:
            whichone = next(n for n in self.objlist if n.id == self.selected)
            self.after(500, lambda: self.itemconfigure(self.selected, fill=whichone.linecolor))

    # def get_and_report_center(self) -> None:
    #     """Get center of current shape and call a class method to report it."""
    #     print(f'in get_and_report_center')
    #     whichone = next(n for n in self.objlist if n.id == self.selected)
    #     # print(f'    {whichone.id=}, {self.selected=}')
    #     center = whichone.center
    #     outline = whichone.linecolor
    #
    #     self.report_center(center, outline)

    # Will replace get_and_report_center
    def report_shape(self) -> None:
        """Get center of current shape and call a class method to report it."""
        whichone = next(n for n in self.objlist if n.id == self.selected)
        center = whichone.center
        outline = whichone.linecolor

        self.report_center(center, outline)
        self.report_size(outline)

    def report_center(self,
                      center: dict,
                      color: str) -> None:
        """Report center x,y coordinates for a shape.

        Args:
            center: x,y coordinates
            color: color for the text report
        """
        self.delete('center_text')
        textstr = f'{center[0]}, {center[1]}'
        self.create_text(10,
                         12,
                         fill=color,
                         text=textstr,
                         anchor='w',
                         tags='center_text')

    def report_size(self, color: str) -> None:
        """Report size of the current object, in pixels."""
        self.delete('size_text')

        sc = self.coords(self.selected)
        wid = int((sc[2] - sc[0]) / 2)
        ht = int((sc[3] - sc[1]) / 2)
        textstr = f'{wid}, {ht}'

        self.create_text(10,
                         26,
                         fill=color,
                         text=textstr,
                         anchor='w',
                         tags='size_text')


    # NOT CURRENTLY USED
    # def set_shape_parameter(self, p, val):
    #     self.__dict__[p] = val


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
