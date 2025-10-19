"""
module: canvas_ui.py

purpose: Types and functions for a canvas intended to contain images.

comments: To display images at their native size(s) when img dimensions
          are smaller than both the viewport height and width, EITHER: a new 
          routine should be written, to replace compare_ratios, OR:
          init_image_size wouldn't be needed in the calling
          module, and native sizes would be used directly. That approach is not
          transparent to the caller.
          Note: this hasn't been tested.

author: Russell Folks

history:
-------
03-04-2024  creation
03-14-2024  Add a section for utility functions.
07-28-2024  Update function docstrings.
08-03-2024  Added comments section to module header.
08-16-2024  Edit get_posn to handle 2 or 3 images.
08-19-2024  Add alignment options: vertical center, horizontal right.
08-24-2024  Add function handle_extra to calculate position for images if
            there are more than two of them. Add type hinting for functions
            that don't have it.
09-07-2024  Add get_1_posn(), to determine a single image position.
09-12-2024  Add get_positions() to determine up to four image positions.
            Remove handle_extra().
09-13-2024  Add type hinting to get_1_posn and get_positions.
10-23-2024  Add function set_canv_centered, to move all images toward the
            center of the canvas, allowing for the viewport gutter.
10-26-2024  Update set_canv_centered() to handle less than 4 images.
11-27-2024  Correct type-hinting for some functions.
11-28-2024  Adjust whitespace, remove commented-out code.
07-11-2025  Add resize_viewport() for dragging the window size.
07-25-2025  Delete old versions of some functions.
"""
"""
TODO:
    1. Try Posn as a class instead of a type.
"""
from PIL import ImageTk
import tkinter as tk


# -------
# utility
# -------
def compare_ratios(vp: float,
                   im: float,
                   w: int,
                   h: int) -> dict:
    """Set new image height and/or width based on viewport shape.

    Images will be scaled up or down to match viewport height or width.
    """
    if vp > im:
        ht_new = h
        wid_new = int(ht_new * im)
    else:
        wid_new = w
        ht_new = int(wid_new / im)

    return {"h": ht_new, "w": wid_new}


# -------------
# static canvas: canvas and contained objects are fixed size
# -------------
def posn_init(self, x: int, y: int):
    self.x = x
    self.y = y


Posn = type('Posn', (), {"__init__": posn_init})


def get_positions(vp: dict,
                  objects: list,
                  arrange: tuple) -> list:
    """Assign locations for all images in a Canvas."""
    pos_list = []

    # Special case: all images centered to the whole canvas.
    if arrange == ('cc', 'cc'):
        pos_list = set_canv_centered(vp, objects)
        return pos_list

    posn1 = get_1_posn(vp, objects[0], arrange)
    pos_list.append(posn1)

    if len(objects) >= 2:
        posn2 = get_1_posn(vp, objects[1], arrange, True)
        pos_list.append(posn2)

    if len(objects) >= 3:
        posn3 = get_1_posn(vp, objects[2], arrange, False, True)
        pos_list.append(posn3)

    if len(objects) == 4:
        posn4 = get_1_posn(vp, objects[3], arrange, True, True)
        pos_list.append(posn4)

    return pos_list


def get_1_posn(vp: dict,
               obj: object,
               arrange: tuple,
               shift_right: bool = False,
               shift_down: bool = False) -> Posn:
    """Assign location for one image in a Canvas."""
    imp = Posn(0, 0)

    match arrange[1]:
        case 'top':
            imp.y = 0
        case 'center':
            imp.y = (vp['h'] - obj.height) / 2
        case 'bottom':
            imp.y = vp['h'] - obj.height

    match arrange[0]:
        case 'left':
            imp.x = 0
        case 'center':
            imp.x = (vp['w'] - obj.width) / 2
        case 'right':
            imp.x = vp['w'] - obj.width

    # if shift_right is True:
    if shift_right:
        imp.x += (vp['w'] + vp['gutter'])
    # if shift_down is True:
    if shift_down:
        imp.y += (vp['h'] + vp['gutter'])

    return imp


def set_canv_centered(vp: dict, objs: list) -> list:
    positions = []
    imp1 = Posn(0, 0)
    imp2 = Posn(0, 0)
    imp3 = Posn(0, 0)
    imp4 = Posn(0, 0)

    imp1.x = vp['w'] - objs[0].width
    imp1.y = vp['h'] - objs[0].height
    positions.append(imp1)

    # report_center = True

    if len(objs) >= 2:
        imp2.x = vp['w'] + vp['gutter']
        imp2.y = vp['h'] - objs[1].height
        positions.append(imp2)

    if len(objs) >= 3:
        imp3.x = vp['w'] - objs[2].width
        imp3.y = vp['h'] + vp['gutter']
        positions.append(imp3)

    if len(objs) >= 4:
        imp4.x = vp['w'] + vp['gutter']
        imp4.y = vp['h'] + vp['gutter']
        positions.append(imp4)

    # if report_center:
    #     print(f'centering im 1 using: {objs[0].width=}, {objs[0].height=}')
    #     print(f'    moved to: {imp1.x}, {imp1.y}')
    #     print(f'centering im 2 using: {objs[1].width=}, {objs[1].height=}')
    #     print(f'    moved to: {imp2.x}, {imp2.y}')
    #     print(f'centering im 3 ing: {objs[2].width=}, {objs[2].height=}')
    #     print(f'    moved to: {imp3.x}, {imp3.y}')
    #     print(f'centering im 4 using: {objs[3].width=}, {objs[3].height=}')
    #     print(f'    moved to: {imp4.x}, {imp4.y}')

    return positions


def init_image_size(im: object,
                    vp: dict) -> dict:
    """Set image display size and shape, based on the defined viewport size."""
    vp_ratio = vp['w'] / vp['h']
    im_ratio = im.width / im.height

    newsize = compare_ratios(vp_ratio, im_ratio, vp['w'], vp['h'])

    return newsize


# --------------
# dynamic canvas: canvas and contained objects can be resized.
# --------------
def resize_images(ev: tk.Event,
                  im: object | list,
                  canv: object) -> None:
    """Create image object for display at a calculated size."""
    global im_tk_new1

    if isinstance(im, list):
        if len(im) == 0:
            print('returning...')
            return
        params1 = calc_resize(ev, im[0])
    else:
        params1 = calc_resize(ev, im)
    # print(f'params1: {params1}')
    # print(f"params1.im_resize_new w,h: {params1['im_resize_new'].width}, {params1['im_resize_new'].height}")
    # print(f"params1.im_resize_new size: {params1['im_resize_new'].size}")

    im_tk_new1 = ImageTk.PhotoImage(params1['im_resize_new'])
    canv.create_image(0, 0,
                      anchor=tk.NW,
                      image=im_tk_new1)


def calc_resize_to_vp(vp: dict, im: object) -> dict:
    canv_width = vp['w']
    canv_height = vp['h']

    canv_ratio = canv_width / canv_height
    im_ratio = im.width / im.height
    # print(f"ratios: canv, im, cw, ch: {canv_ratio}, {im_ratio}, {canv_width}, {canv_height}")

    newsize = compare_ratios(canv_ratio, im_ratio, canv_width, canv_height)

    params = {'im_resize_new': im.resize((newsize['w'], newsize['h'])),
              'wid_int': int(canv_width),
              'ht_int': int(canv_height)}

    return params


def resize_viewport(ev, vp, flag):
    canv = ev.widget
    canv.configure(width=ev.width, height=ev.height)

    vp['w'] = ev.width
    vp['h'] = ev.height

    flag = True
    # canv.configure(width=vp['w'], height=vp['h'])
    # canv.update()
    # print('in canvas_ui/resize_viewport')
    # print(f"    {vp['w']=}, {vp['h']=}")
    # print(f'    {canv.winfo_width()=}, {canv.winfo_height()=}')


def calc_resize(ev: tk.Event, im: object) -> dict:
    """Calculate new size for a dynamically resizable canvas."""
    this_canv = ev.widget
    canv_width = ev.width
    canv_height = ev.height

    canv_ratio = canv_width / canv_height
    im_ratio = im.width / im.height
    # print(f"ratios: canv, im, cw, ch: {canv_ratio}, {im_ratio}, {canv_width}, {canv_height}")

    newsize = compare_ratios(canv_ratio, im_ratio, canv_width, canv_height)

    this_canv.delete(1)

    params = {'im_resize_new': im.resize((newsize['w'], newsize['h'])),
              'im_wd_new': newsize['w'],
              'im_ht_new': newsize['h'],
              'canv_wd': int(canv_width),
              'canv_ht': int(canv_height)}

    return params
