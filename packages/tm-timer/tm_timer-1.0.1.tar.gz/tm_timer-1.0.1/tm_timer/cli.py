import time
import threading
import sys
import termios
import tty
import re
import os
import atexit
import shutil
import argparse

original_term_settings = termios.tcgetattr(sys.stdin.fileno())

def restore_terminal():
    try:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, original_term_settings)
    except:
        pass

atexit.register(restore_terminal)

def with_raw_mode():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setraw(fd)
    return old_settings

def get_char():
    fd = sys.stdin.fileno()
    old_settings = with_raw_mode()
    try:
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def parse_time_input(user_input):
    pattern = r"(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?"
    match = re.fullmatch(pattern, user_input.strip().lower())
    if not match or not any(match.groups()):
        raise ValueError("Invalid time format. Use format like '1h30m45s'.")
    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0
    return hours * 3600 + minutes * 60 + seconds

def timer():
    global paused, running, seconds, target_seconds
    while running:
        if not paused:
            cols = shutil.get_terminal_size((80, 20)).columns
            mins, secs = divmod(seconds, 60)
            hours, mins = divmod(mins, 60)
            msg = f"Timer: {hours:02d}:{mins:02d}:{secs:02d} [Press 'p' to Pause/Resume, 'q' to Quit]"
            msg = msg[:cols - 1] if len(msg) >= cols else msg
            sys.stdout.write(f"\r\033[K{msg}")
            sys.stdout.flush()
            seconds += 1
            if seconds >= target_seconds:
                sys.stdout.write("\n\n⏰ Time's up! Target of {} reached.\n".format(target_input))
                sys.stdout.flush()
                running = False
                break
        time.sleep(1)

def input_listener():
    global paused, running
    while running:
        key = get_char()
        if key.lower() == 'p':
            paused = not paused
        elif key.lower() == 'q':
            running = False
            break

def entry():
    global paused, running, seconds, target_seconds, target_input

    parser = argparse.ArgumentParser(description="Terminal Timer with pause and alert.")
    parser.add_argument("duration", help="Timer duration (e.g., 4h, 25m, 1h30m45s)")
    args = parser.parse_args()

    try:
        target_input = args.duration
        target_seconds = parse_time_input(target_input)
    except ValueError as e:
        print(e)
        sys.exit(1)

    paused = False
    running = True
    seconds = 0

    input_thread = threading.Thread(target=input_listener, daemon=True)
    timer_thread = threading.Thread(target=timer)

    input_thread.start()
    timer_thread.start()

    timer_thread.join()
    restore_terminal()
    print("Timer stopped.")
