import pygetwindow as gw
import pyautogui
import keyboard
import time
from datetime import datetime
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
import os
from dotenv import load_dotenv
import threading

load_dotenv()
SSIM_THRESHOLD = float(os.getenv("SSIM_THRESHOLD", "0.85"))

def capture_screen_gray_color():
    screenshot = pyautogui.screenshot()
    np_img = np.array(screenshot)
    gray = cv2.cvtColor(np_img, cv2.COLOR_RGB2GRAY)
    return gray, np_img

def calculate_ssim(img1, img2):
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    return ssim(img1, img2)

def save_screenshot(image, label, timestamp, screenshot_directory):
    filename = f"{label}_{timestamp}.png"
    save_path = os.path.join(screenshot_directory, filename)
    os.makedirs(screenshot_directory, exist_ok=True)  # Ensure directory exists
    cv2.imwrite(save_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    return save_path

def monitor_pos(pos_window_title, on_capture_callback, screenshot_directory, on_phone_captured=None, stop_event=None):
    digit_buffer = ""
    print("Monitoring started. Type 10-digit phone number. Press Esc to quit.")
    
    # Track pressed keys to avoid duplicate events
    pressed_keys = set()
    
    while True:
        # Check stop event first
        if stop_event and stop_event.is_set():
            print("Monitoring stopped by event.")
            break
            
        # Check for ESC key
        if keyboard.is_pressed('esc'):
            print("Exiting...")
            break
            
        # Check for digit keys (0-9)
        for digit in '0123456789':
            if keyboard.is_pressed(digit) and digit not in pressed_keys:
                pressed_keys.add(digit)
                active_window = gw.getActiveWindow()
                if active_window and pos_window_title.lower() in active_window.title.lower():
                    if len(digit_buffer) < 10:
                        digit_buffer += digit
                        print(f"Digit captured: {digit_buffer}")
                        
        # Check for backspace
        if keyboard.is_pressed('backspace') and 'backspace' not in pressed_keys:
            pressed_keys.add('backspace')
            if digit_buffer:
                digit_buffer = digit_buffer[:-1]
                print(f"Backspace pressed. Buffer: {digit_buffer}")
        
        # Clear pressed keys that are no longer pressed
        for key in list(pressed_keys):
            if not keyboard.is_pressed(key):
                pressed_keys.remove(key)
        
        # Check if we have a complete phone number
        if len(digit_buffer) == 10:
            print("10-digit phone number entered.")
            if on_phone_captured:
                on_phone_captured(digit_buffer)
            capture_and_monitor_changes(on_capture_callback, screenshot_directory, stop_event)
            digit_buffer = ""
        
        # Small delay to prevent high CPU usage
        time.sleep(0.1)

def capture_and_monitor_changes(on_capture_callback, screenshot_directory, stop_event=None):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    gray_initial, color_initial = capture_screen_gray_color()
    save_screenshot(color_initial, "input_entered", timestamp, screenshot_directory)
    buffer_seconds = 2
    frame_buffer = []
    last_before_change = None
    first_after_change = None
    print("Monitoring screen for changes...")
    while True:
        # Check stop event
        if stop_event and stop_event.is_set():
            print("Screen monitoring stopped by event.")
            return
            
        now = time.time()
        gray, color = capture_screen_gray_color()
        frame_buffer.append((now, gray, color))
        frame_buffer = [(t, g, c) for (t, g, c) in frame_buffer if now - t <= buffer_seconds + 1]
        if len(frame_buffer) >= 2:
            score = calculate_ssim(frame_buffer[-2][1], frame_buffer[-1][1])
            if score < SSIM_THRESHOLD:
                target_time = now - buffer_seconds
                before_frame = min(frame_buffer, key=lambda tup: abs(tup[0] - target_time))
                last_before_change = before_frame[2]
                first_after_change = frame_buffer[-1][2]
                break
        time.sleep(0.4)
    if last_before_change is not None and first_after_change is not None:
        before_path = save_screenshot(last_before_change, "before_change", timestamp, screenshot_directory)
        save_screenshot(first_after_change, "after_change", timestamp, screenshot_directory)
        on_capture_callback(before_path, timestamp)
    else:
        print("No significant screen change detected.")
