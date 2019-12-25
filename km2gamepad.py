#!/usr/bin/env python2
# -*- coding: utf-8 -*-

if __name__ != '__main__':
    print('Run this script standalone')
    exit(1)


def install_pip_and_modules(module_names):
    """
    Code from https://github.com/skazanyNaGlany/python_stub
    """
    import os
    import sys
    import importlib
    import shutil

    try:
        import urllib2
    except ModuleNotFoundError:
        import urllib.request

    def download_file(url):
        print('Downloading ' + url)

        if 'urllib2' in globals() or 'urllib2' in locals():
            remote_file = urllib2.urlopen(url)
        elif 'urllib' in globals() or 'urllib' in locals():
            remote_file = urllib.request.urlopen(url)

        with open(os.path.basename(url), 'wb') as local_file:
            local_file.write(remote_file.read())

    def pip_install_module(module_name, as_user):
        cmd = sys.executable + ' -m pip install ' + module_name

        if as_user:
            cmd += ' --user'

        print('Executing: ' + cmd)
        os.system(cmd)

    in_virtualenv = 'VIRTUAL_ENV' in os.environ
    is_root = os.geteuid() == 0
    install_as_user = not in_virtualenv and not is_root

    try:
        import pip
    except ImportError as x1:
        print(x1)

        download_file('https://bootstrap.pypa.io/get-pip.py')

        print('Installing: pip')

        if in_virtualenv:
            cmd = sys.executable + ' get-pip.py'
        else:
            cmd = sys.executable + ' get-pip.py --user'

        print('Executing: ' + cmd)

        os.system(cmd)
        os.remove('get-pip.py')

        try:
            import pip
        except ImportError:
            print('Unable to install pip')
            exit(1)

    module_names_list = module_names.keys()
    cwd = os.getcwd()

    # check if we need Dulwich - pure Python Git implementation
    need_dulwich = False
    for imodule_name2 in module_names:
        if module_names[imodule_name2].startswith('git+https://'):
            need_dulwich = True
            break

    if need_dulwich:
        try:
            import dulwich
        except ImportError as x4:
            print(x4)

            pip_install_module('dulwich', install_as_user)

    for imodule_name in module_names_list:
        try:
            globals()[imodule_name] = importlib.import_module(imodule_name)
        except ImportError as x2:
            print(x2)

            imodule_pip_name = module_names[imodule_name]

            print('Installing: {} ({})'.format(imodule_name, imodule_pip_name))

            if imodule_pip_name.startswith('git+https://'):
                import dulwich.porcelain

                # just remove git+ and install
                pkg_url = imodule_pip_name[4:]
                pkg_basename = os.path.basename(pkg_url)

                try:
                    shutil.rmtree(os.path.join(cwd, pkg_basename))
                except OSError:
                    pass

                dulwich.porcelain.clone(pkg_url)
                pip_install_module(pkg_basename, install_as_user)

                shutil.rmtree(os.path.join(cwd, pkg_basename))
            else:
                pip_install_module(imodule_pip_name, install_as_user)
            try:
                globals()[imodule_name] = importlib.import_module(imodule_name)
            except ImportError as x3:
                print(x3)

                print('Unable to install module ' + imodule_name)
                exit(1)


install_pip_and_modules({
    'pynput': 'pynput',
    'uinput': 'uinput'
})


import uinput
import time

from pynput.keyboard import Listener as KeyboardListener, Key
from pynput.mouse import Listener as MouseListener, Button


gamepad_stopped = False
gamepad_device = None
current_mouse_x = 0
current_mouse_y = 0
emitting_triangle = False
emitting_cross = False
emitting_triangle_time = 0
emitting_cross_time = 0
left_alt_pressed = 0


def on_mouse_move(x, y):
    global current_mouse_x, current_mouse_y

    current_mouse_x = x
    current_mouse_y = y


def on_mouse_click(x, y, button, pressed):
    global gamepad_device

    if button == Button.left:
        gamepad_device.emit(uinput.BTN_X, pressed)
    elif button == Button.right:
        gamepad_device.emit(uinput.BTN_B, pressed)
    elif button == Button.middle:
        gamepad_device.emit(uinput.BTN_Y, 0)
        gamepad_device.emit(uinput.BTN_A, 0)


def on_mouse_scroll(x, y, dx, dy):
    global gamepad_device, emitting_cross, emitting_triangle
    global emitting_cross_time, emitting_triangle_time

    scroll_direction = 1 if dy < 0 else -1
    current_time = time.time()

    if scroll_direction == -1 and current_time - emitting_cross_time > 0.2:
        gamepad_device.emit(uinput.BTN_Y, 0 if emitting_cross else 1)

        emitting_cross = not emitting_cross
        emitting_cross_time = current_time
    elif scroll_direction == 1 and current_time - emitting_triangle_time > 0.2:
        gamepad_device.emit(uinput.BTN_A, 0 if emitting_triangle else 1)

        emitting_triangle = not emitting_triangle
        emitting_triangle_time = current_time


def exec_key_event(key_str, pressed):
    global gamepad_device, gamepad_stopped, left_alt_pressed

    # print(type(key_str))
    # print(key_str)
    # print('=' + key_str + '=')

    # if key_str == 'u\'w\'' or key_str == u'W':
    if key_str == 'w' or key_str == 'W':
        # up arrow, y
        gamepad_device.emit(uinput.BTN_DPAD_UP, pressed)
    elif key_str == 'r' or key_str == 'R':
        # r1
        gamepad_device.emit(uinput.BTN_TR, pressed)
    elif key_str == 'a' or key_str == 'A':
        # l1
        gamepad_device.emit(uinput.BTN_TL, pressed)
    elif key_str == 's' or key_str == 'S':
        # down arrow, y
        gamepad_device.emit(uinput.BTN_DPAD_DOWN, pressed)
    elif key_str == 'd' or key_str == 'D':
        # r1
        gamepad_device.emit(uinput.BTN_TR, pressed)
    elif key_str == 'f' or key_str == 'F':
        # r2
        gamepad_device.emit(uinput.BTN_TR2, pressed)
    elif key_str == 'g' or key_str == 'G':
        # triangle
        gamepad_device.emit(uinput.BTN_Y, pressed)
    elif key_str == 'v' or key_str == 'V':
        # square
        gamepad_device.emit(uinput.BTN_X, pressed)
    elif key_str == 'b' or key_str == 'B':
        # circle
        gamepad_device.emit(uinput.BTN_B, pressed)
    elif key_str == 'Key.backspace':
        # select
        gamepad_device.emit(uinput.BTN_SELECT, pressed)
    elif key_str == 'Key.enter':
        # start
        gamepad_device.emit(uinput.BTN_START, pressed)
    elif key_str == 'Key.tab':
        # l1
        gamepad_device.emit(uinput.BTN_TL, pressed)
    elif key_str == 'Key.caps_lock':
        # l2
        gamepad_device.emit(uinput.BTN_TL2, pressed)
    elif key_str == 'Key.space':
        # cross
        gamepad_device.emit(uinput.BTN_A, pressed)
    elif key_str == 'Key.up':
        # up arrow, y
        # print('1111')
        gamepad_device.emit(uinput.BTN_DPAD_UP, pressed)
    elif key_str == 'Key.left':
        # left arrow, x
        gamepad_device.emit(uinput.BTN_DPAD_LEFT, pressed)
    elif key_str == 'Key.down':
        # down arrow, y
        gamepad_device.emit(uinput.BTN_DPAD_DOWN, pressed)
    elif key_str == 'Key.right':
        # right arrow, x
        gamepad_device.emit(uinput.BTN_DPAD_RIGHT, pressed)
    elif key_str == 'Key.alt':
        left_alt_pressed = pressed
    elif key_str == 'Key.esc':
        gamepad_stopped = left_alt_pressed and pressed


def on_key_press(key):
    if hasattr(key, 'char'):
        exec_key_event(key.char, 1)
    else:
        exec_key_event(str(key), 1)


def on_key_release(key):
    if hasattr(key, 'char'):
        exec_key_event(key.char, 0)
    else:
        exec_key_event(str(key), 0)


def direction_loop():
    global gamepad_stopped
    global current_mouse_x
    global current_mouse_y

    last_mouse_x = 0
    last_mouse_y = 0

    while not gamepad_stopped:
        x_direction = None
        y_direction = None

        if last_mouse_x != current_mouse_x:
            if last_mouse_x > current_mouse_x:
                x_direction = -1
            else:
                x_direction = 1

        if last_mouse_y != current_mouse_y:
            if last_mouse_y > current_mouse_y:
                y_direction = -1
            else:
                y_direction = 1

        if x_direction == None:
            gamepad_device.emit(uinput.BTN_DPAD_LEFT, 0)
            gamepad_device.emit(uinput.BTN_DPAD_RIGHT, 0)

        # if y_direction == None:
        #     gamepad_device.emit(uinput.BTN_DPAD_UP, 0)
        #     gamepad_device.emit(uinput.BTN_DPAD_DOWN, 0)

        # if not x_direction and not y_direction:
        # mouse_controller.position = (800, 600)

        # if not x_direction and not y_direction:
        #     autopy.mouse.smooth_move(800, 600)

        # if x_direction or y_direction:
        #     pyautogui.moveTo(800, 600)
        #     # print(current_mouse_x, current_mouse_y)

        if x_direction == -1:
            gamepad_device.emit(uinput.BTN_DPAD_LEFT, 1)
            gamepad_device.emit(uinput.BTN_DPAD_RIGHT, 0)
        elif x_direction == 1:
            gamepad_device.emit(uinput.BTN_DPAD_LEFT, 0)
            gamepad_device.emit(uinput.BTN_DPAD_RIGHT, 1)

        # if y_direction == -1:
        #     gamepad_device.emit(uinput.BTN_DPAD_UP, 1)
        #     gamepad_device.emit(uinput.BTN_DPAD_DOWN, 0)
        # elif y_direction == 1:
        #     gamepad_device.emit(uinput.BTN_DPAD_UP, 0)
        #     gamepad_device.emit(uinput.BTN_DPAD_DOWN, 1)

        last_mouse_x = current_mouse_x
        last_mouse_y = current_mouse_y

        time.sleep(0.01)


def main():
    global gamepad_device

    gamepad_buttons = (
        uinput.BTN_JOYSTICK,
        uinput.BTN_A,
        uinput.BTN_B,
        uinput.BTN_X,
        uinput.BTN_Y,
        uinput.BTN_TL,
        uinput.BTN_TR,
        uinput.BTN_TL2,
        uinput.BTN_TR2,
        uinput.BTN_START,
        uinput.BTN_SELECT,
        uinput.BTN_DPAD_UP,
        uinput.BTN_DPAD_DOWN,
        uinput.BTN_DPAD_LEFT,
        uinput.BTN_DPAD_RIGHT
    )

    gamepad_device = uinput.Device(gamepad_buttons)

    mouse_listener = MouseListener(
        on_move=on_mouse_move,
        on_click=on_mouse_click,
        on_scroll=on_mouse_scroll
    )
    keyboard_listener = KeyboardListener(
        on_press=on_key_press,
        on_release=on_key_release
    )

    mouse_listener.start()
    keyboard_listener.start()

    direction_loop()


main()
