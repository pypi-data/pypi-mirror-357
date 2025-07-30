import subprocess
import base64
from pathlib import Path
import pyautogui  # Replace PIL.ImageGrab with pyautogui
from uuid import uuid4
from screeninfo import get_monitors
import platform
from PIL import Image

if platform.system() == "Darwin":
    import Quartz  # uncomment this line if you are on macOS
    
from .base import BaseAnthropicTool, ToolError, ToolResult


OUTPUT_DIR = "./tmp/outputs"

def get_screenshot(selected_screen: int = 0, resize: bool = True, target_width: int = 1920, target_height: int = 1080):
    """
    Take a screenshot of the top-left corner of the screen.
    The captured area is at most target_width x target_height.
    If the screen is smaller than the target dimensions, the screenshot is padded with black.
    
    For WebRDP environment, this ensures consistent coordinate mapping by always 
    capturing exactly the 1920x1080 area that clicks will operate within.
    """
    
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"screenshot_{uuid4().hex}.png"

    try:
        actual_screen_width, actual_screen_height = _get_screen_size(selected_screen)
        print(f"[DEBUG] Actual screen size: {actual_screen_width}x{actual_screen_height}")
    except Exception as e:
        print(f"[DEBUG] Could not get actual screen size: {e}")
        # Fallback to target resolution if screen size detection fails
        actual_screen_width, actual_screen_height = target_width, target_height

    # For WebRDP: Always capture exactly the target dimensions from top-left (0,0)
    # This ensures 1:1 coordinate mapping with click operations
    capture_width = target_width
    capture_height = target_height
    capture_region = (0, 0, capture_width, capture_height)
    
    print(f"[DEBUG] WebRDP Screenshot - Capture region: {capture_region} (x, y, width, height)")
    print(f"[DEBUG] WebRDP Screenshot - Target area: {target_width}x{target_height}")

    try:
        # Take screenshot of the determined region
        screenshot = pyautogui.screenshot(region=capture_region)
        print(f"[DEBUG] Screenshot captured, size: {screenshot.size}")
    except Exception as e:
        raise ToolError(
            output=f"Failed to capture screenshot with region {capture_region}: {e}",
            action_base_type="screenshot"
        )

    if screenshot is None:
        raise ToolError(
            output="Screenshot capture returned None",
            action_base_type="screenshot"
        )
        
    # Ensure screenshot is exactly target dimensions for WebRDP coordinate consistency
    if screenshot.width != target_width or screenshot.height != target_height:
        print(f"[DEBUG] Screenshot size {screenshot.size} doesn't match target {target_width}x{target_height}")
        # Create a new image with exact target dimensions
        padded_screenshot = Image.new("RGB", (target_width, target_height), "black")
        # Paste the captured screenshot at top-left (0,0) to maintain coordinate mapping
        paste_width = min(screenshot.width, target_width)
        paste_height = min(screenshot.height, target_height)
        crop_region = (0, 0, paste_width, paste_height)
        cropped_screenshot = screenshot.crop(crop_region) if screenshot.size != (paste_width, paste_height) else screenshot
        padded_screenshot.paste(cropped_screenshot, (0, 0))
        screenshot = padded_screenshot
        print(f"[DEBUG] Adjusted screenshot to exact target size: {screenshot.size}")

    print(f"[DEBUG] Final WebRDP screenshot size: {screenshot.size}")
    
    # No additional resizing needed since we've already ensured exact dimensions
    if screenshot.size != (target_width, target_height):
        print(f"[ERROR] Screenshot size mismatch: {screenshot.size} vs expected {target_width}x{target_height}")
        screenshot = screenshot.resize((target_width, target_height))
        print(f"[DEBUG] Force-resized to: {screenshot.size}")

    # Save the screenshot
    screenshot.save(str(path))
    print(f"[DEBUG] Screenshot saved to: {path}")

    if path.exists():
        return screenshot, str(path)
    
    raise ToolError(
        output=f"Failed to take screenshot: {path} does not exist.",
        action_base_type="screenshot"
    )
    
    


def _get_screen_size(selected_screen: int = 0):
    if platform.system() == "Windows":
        # Use screeninfo to get primary monitor on Windows
        screens = get_monitors()

        # Sort screens by x position to arrange from left to right
        sorted_screens = sorted(screens, key=lambda s: s.x)
        if selected_screen is None:
            primary_monitor = next((m for m in get_monitors() if m.is_primary), None)
            return primary_monitor.width, primary_monitor.height
        elif selected_screen < 0 or selected_screen >= len(screens):
            raise IndexError("Invalid screen index.")
        else:
            screen = sorted_screens[selected_screen]
            return screen.width, screen.height
    elif platform.system() == "Darwin":
        # macOS part using Quartz to get screen information
        max_displays = 32  # Maximum number of displays to handle
        active_displays = Quartz.CGGetActiveDisplayList(max_displays, None, None)[1]

        # Get the display bounds (resolution) for each active display
        screens = []
        for display_id in active_displays:
            bounds = Quartz.CGDisplayBounds(display_id)
            screens.append({
                'id': display_id,
                'x': int(bounds.origin.x),
                'y': int(bounds.origin.y),
                'width': int(bounds.size.width),
                'height': int(bounds.size.height),
                'is_primary': Quartz.CGDisplayIsMain(display_id)  # Check if this is the primary display
            })

        # Sort screens by x position to arrange from left to right
        sorted_screens = sorted(screens, key=lambda s: s['x'])

        if selected_screen is None:
            # Find the primary monitor
            primary_monitor = next((screen for screen in screens if screen['is_primary']), None)
            if primary_monitor:
                return primary_monitor['width'], primary_monitor['height']
            else:
                raise RuntimeError("No primary monitor found.")
        elif selected_screen < 0 or selected_screen >= len(screens):
            raise IndexError("Invalid screen index.")
        else:
            # Return the resolution of the selected screen
            screen = sorted_screens[selected_screen]
            return screen['width'], screen['height']

    else:  # Linux or other OS
        cmd = "xrandr | grep ' primary' | awk '{print $4}'"
        try:
            output = subprocess.check_output(cmd, shell=True).decode()
            resolution = output.strip().split()[0]
            width, height = map(int, resolution.split('x'))
            return width, height
        except subprocess.CalledProcessError:
            raise RuntimeError("Failed to get screen resolution on Linux.")
