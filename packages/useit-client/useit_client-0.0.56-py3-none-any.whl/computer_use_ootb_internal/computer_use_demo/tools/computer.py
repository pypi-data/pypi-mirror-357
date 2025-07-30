import subprocess
import platform
import pyautogui
import asyncio
import base64
import os
import time
if platform.system() == "Darwin":
    import Quartz  # uncomment this line if you are on macOS
if platform.system() == "Windows":
    import ctypes
    from ctypes import wintypes
from enum import StrEnum
from pathlib import Path
from typing import Literal, TypedDict
from uuid import uuid4
from screeninfo import get_monitors

from PIL import ImageGrab, Image
from functools import partial

from anthropic.types.beta import BetaToolComputerUse20241022Param

from computer_use_ootb_internal.computer_use_demo.tools.base import BaseAnthropicTool, ToolError, ToolResult
from computer_use_ootb_internal.computer_use_demo.tools.run import run
from computer_use_ootb_internal.computer_use_demo.tools.screen_capture import get_screenshot as capture_screenshot_1920
from computer_use_ootb_internal.computer_use_demo.tools.computer_marbot import MarbotAutoGUI
from computer_use_ootb_internal.computer_use_demo.animation.click_animation import show_click, show_move_to


OUTPUT_DIR = "./tmp/outputs"

TYPING_DELAY_MS = 12
TYPING_GROUP_SIZE = 50

Action = Literal[
    "key",
    "type",
    "mouse_move",
    "left_click",
    "left_click_drag",
    "right_click",
    "middle_click",
    "double_click",
    "triple_click",
    "left_press",
    "key_down",
    "key_up",
    "scroll_down",
    "scroll_up",
    "screenshot",
    "cursor_position",
    "sr_scroll_down",
    "sr_scroll_up",
    "wait",
    # starrail browser mode
    "left_click_windll",
    "mouse_move_windll",
    "right_click_windll",
    "key_down_windll",
    "key_up_windll",
    # webrdp testing
    "test_webrdp_click",
]


class Resolution(TypedDict):
    width: int
    height: int


MAX_SCALING_TARGETS: dict[str, Resolution] = {
    "XGA": Resolution(width=1024, height=768),  # 4:3
    "WXGA": Resolution(width=1280, height=800),  # 16:10
    "FWXGA": Resolution(width=1366, height=768),  # ~16:9
}


class ScalingSource(StrEnum):
    COMPUTER = "computer"
    API = "api"


class ComputerToolOptions(TypedDict):
    display_height_px: int
    display_width_px: int
    display_number: int | None


def chunks(s: str, chunk_size: int) -> list[str]:
    return [s[i : i + chunk_size] for i in range(0, len(s), chunk_size)]


def get_screen_details():
    screens = get_monitors()
    screen_details = []

    # Sort screens by x position to arrange from left to right
    sorted_screens = sorted(screens, key=lambda s: s.x)

    # Loop through sorted screens and assign positions
    primary_index = 0
    for i, screen in enumerate(sorted_screens):
        if i == 0:
            layout = "Left"
        elif i == len(sorted_screens) - 1:
            layout = "Right"
        else:
            layout = "Center"
        
        if screen.is_primary:
            position = "Primary" 
            primary_index = i
        else:
            position = "Secondary"
        screen_info = f"Screen {i + 1}: {screen.width}x{screen.height}, {layout}, {position}"
        screen_details.append(screen_info)

    return screen_details, primary_index


class ComputerTool(BaseAnthropicTool):
    """
    A tool that allows the agent to interact with the screen, keyboard, and mouse of the current computer.
    Adapted for Windows using 'pyautogui'.
    """

    name: Literal["computer"] = "computer"
    api_type: Literal["computer_20241022"] = "computer_20241022"
    width: int
    height: int
    display_num: int | None

    _screenshot_delay = 2.0
    _scaling_enabled = True

    @property
    def options(self) -> ComputerToolOptions:
        width, height = self.scale_coordinates(
            ScalingSource.COMPUTER, self.width, self.height
        )
        return {
            "display_width_px": width,
            "display_height_px": height,
            "display_number": self.display_num,
        }

    def to_params(self) -> BetaToolComputerUse20241022Param:
        return {"name": self.name, "type": self.api_type, **self.options}

    def __init__(self, selected_screen: int = 0, is_scaling: bool = True):
        super().__init__()

        # Get screen width and height using Windows command
        self.display_num = None
        self.offset_x = 0
        self.offset_y = 0
        self.selected_screen = selected_screen   
        # Scaling is disabled to ensure 1:1 coordinate mapping
        self.is_scaling = False # is_scaling
        self.width, self.height = self.get_screen_size()     

        # Configure PyAutoGUI for WebRDP environment
        pyautogui.FAILSAFE = False  # Disable fail-safe for WebRDP
        pyautogui.PAUSE = 0.01  # Small pause between operations
        print(f"[DEBUG] PyAutoGUI configured for WebRDP - FAILSAFE: {pyautogui.FAILSAFE}, PAUSE: {pyautogui.PAUSE}")
        
        # Force windll method for RDP environments since PyAutoGUI sends events to host
        self.use_windll_for_mouse = True
        print(f"[DEBUG] Forcing windll method for mouse operations in RDP environment")
        
        # Test coordinate system for WebRDP
        current_pos = pyautogui.position()
        screen_size = pyautogui.size()
        print(f"[DEBUG] Current mouse position: {current_pos}")
        print(f"[DEBUG] Detected screen size: {screen_size}")
        print(f"[DEBUG] Tool screen size: {self.width}x{self.height}")
        print(f"[DEBUG] WebRDP working area: 1920x1080")

        # Path to cliclick
        self.cliclick = "cliclick"
        self.key_conversion = {"Page_Down": "pagedown",
                               "Page_Up": "pageup",
                               "Super_L": "win",
                               "Escape": "esc"}
        
        system = platform.system()        # Detect platform
        if system == "Windows":
            screens = get_monitors()
            sorted_screens = sorted(screens, key=lambda s: s.x)
            if self.selected_screen < 0 or self.selected_screen >= len(screens):
                raise IndexError("Invalid screen index.")
            screen = sorted_screens[self.selected_screen]
            bbox = (screen.x, screen.y, screen.x + screen.width, screen.y + screen.height)

        elif system == "Darwin":  # macOS
            max_displays = 32  # Maximum number of displays to handle
            active_displays = Quartz.CGGetActiveDisplayList(max_displays, None, None)[1]
            screens = []
            for display_id in active_displays:
                bounds = Quartz.CGDisplayBounds(display_id)
                screens.append({
                    'id': display_id, 'x': int(bounds.origin.x), 'y': int(bounds.origin.y),
                    'width': int(bounds.size.width), 'height': int(bounds.size.height),
                    'is_primary': Quartz.CGDisplayIsMain(display_id)  # Check if this is the primary display
                })
            sorted_screens = sorted(screens, key=lambda s: s['x'])
            if self.selected_screen < 0 or self.selected_screen >= len(screens):
                raise IndexError("Invalid screen index.")
            screen = sorted_screens[self.selected_screen]
            bbox = (screen['x'], screen['y'], screen['x'] + screen['width'], screen['y'] + screen['height'])
        else:  # Linux or other OS
            cmd = "xrandr | grep ' primary' | awk '{print $4}'"
            try:
                output = subprocess.check_output(cmd, shell=True).decode()
                resolution = output.strip().split()[0]
                width, height = map(int, resolution.split('x'))
                bbox = (0, 0, width, height)  # Assuming single primary screen for simplicity
            except subprocess.CalledProcessError:
                raise RuntimeError("Failed to get screen resolution on Linux.")
            
        self.offset_x = screen['x'] if system == "Darwin" else screen.x
        self.offset_y = screen['y'] if system == "Darwin" else screen.y
        self.bbox = bbox

        self.marbot_auto_gui = MarbotAutoGUI()
        
    
    def __call__(
        self,
        *,
        action: Action,
        text: str | None = None,
        coordinate: tuple[int, int] | None = None,
        **kwargs,
    ):
        print(f"action: {action}, text: {text}, coordinate: {coordinate}")
        print(f"[DEBUG] ComputerTool - Screen bbox: {self.bbox}")
        print(f"[DEBUG] ComputerTool - Offset: x_offset={self.offset_x}, y_offset={self.offset_y}")
        print(f"[DEBUG] ComputerTool - Scaling enabled: {self.is_scaling}")
       
        # Action Type 1: Required coordinates
        # Actions: mouse_move, left_click_drag

        if action in ("mouse_move", "left_click_drag"):
            if coordinate is None:
                raise ToolError(output=f"coordinate is required for {action}", action_base_type="error")
            if text is not None:
                raise ToolError(output=f"text is not accepted for {action}", action_base_type="error")
            if not isinstance(coordinate, (list, tuple)) or len(coordinate) != 2:
                raise ToolError(output=f"{coordinate} must be a tuple of length 2", action_base_type="error")
            if not all(isinstance(i, int) for i in coordinate):
                raise ToolError(output=f"{coordinate} must be a tuple of non-negative ints", action_base_type="error")
            
            print(f"[DEBUG] Original coordinates: {coordinate}")
            
            if self.is_scaling:
                x, y = self.scale_coordinates(
                    ScalingSource.API, coordinate[0], coordinate[1]
                )
                print(f"[DEBUG] After scaling: ({x}, {y})")
            else:
                x, y = coordinate
                print(f"[DEBUG] No scaling applied: ({x}, {y})")
            
            # The offset is removed to handle WebRDP environment correctly
            # x += self.offset_x
            # y += self.offset_y
            print(f"[DEBUG] Final coordinates (no offset applied): ({x}, {y})")

            if action == "mouse_move":
                if self.use_windll_for_mouse:
                    print(f"[DEBUG] Using windll method for mouse move in RDP")
                    self.marbot_auto_gui.moveTo(x, y)
                else:
                    pyautogui.moveTo(x, y)
                    # Verify the mouse position after moving
                    actual_x, actual_y = pyautogui.position()
                    print(f"[DEBUG] Mouse move - Target: ({x}, {y}), Actual: ({actual_x}, {actual_y})")
                return ToolResult(output=f"Mouse move to ({x}, {y})", action_base_type="move")
            
            elif action == "left_click_drag":
                current_x, current_y = pyautogui.position()
                pyautogui.dragTo(x, y, duration=0.5)  # Adjust duration as needed
                return ToolResult(output=f"Mouse drag", action_base_type="move")

        # Action Type 2: Required text (keynames)
        # Actions: key, type, key_down, key_up
        if action in ("key", "type", "key_down", "key_up"):
            if text is None:
                raise ToolError(output=f"text is required for {action}", action_base_type="error")
            if coordinate is not None:
                raise ToolError(output=f"coordinate is not accepted for {action}", action_base_type="error")
            if not isinstance(text, str):
                raise ToolError(output=f"{text} must be a string", action_base_type="error")

            if action == "key":
                # Handle key combinations
                keys = text.split('+')
                for key in keys:
                    key = self.key_conversion.get(key.strip(), key.strip())
                    key = key.lower()
                    pyautogui.keyDown(key)  # Press down each key
                for key in reversed(keys):
                    key = self.key_conversion.get(key.strip(), key.strip())
                    key = key.lower()
                    pyautogui.keyUp(key)    # Release each key in reverse order
                return ToolResult(output=f"Press key '{text}'", action_base_type="key")
            
            elif action == "key_down":
                pyautogui.keyDown(text)
                return ToolResult(output=f"Press key '{text}'", action_base_type="key")
            elif action == "key_up":
                pyautogui.keyUp(text)
                return ToolResult(output=f"Release key '{text}'", action_base_type="key")

            elif action == "type":
                pyautogui.typewrite(text, interval=TYPING_DELAY_MS / 1000)  # Convert ms to seconds
                # screenshot_base64 = (self.screenshot()).base64_image
                return ToolResult(output=f"Type '{text}'", action_base_type="type") #  base64_image=screenshot_base64)

        # Action Type 3: No required text or coordinates
        # Actions: left_click, right_click, double_click, middle_click, left_press, scroll_down, scroll_up
        if action in (
            "left_click",
            "right_click",
            "double_click",
            "triple_click",
            "middle_click",
            "left_press",
            "scroll_down",
            "scroll_up",
            "wait",
        ):
            if text is not None:
                raise ToolError(output=f"text is not accepted for {action}", action_base_type="error")
            # if coordinate is not None:
            #     raise ToolError(output=f"coordinate is not accepted for {action}", action_base_type="error")

            if coordinate is not None:
                print(f"[DEBUG] Click action with coordinates: {coordinate}")
                x, y = coordinate
                # The offset is removed to handle WebRDP environment correctly
                # x += self.offset_x
                # y += self.offset_y
                print(f"[DEBUG] Final click coordinates (no offset applied): ({x}, {y})")
            else:
                x, y = pyautogui.position()
                print(f"[DEBUG] Click action using current mouse position: ({x}, {y})")

            if action == "left_click":
                # Ensure window focus for WebRDP environments
                self.ensure_window_focus()
                
                print(f"[DEBUG] Left click - Target: ({x}, {y})")
                show_click(x, y)
                
                # Use windll method for RDP environments (PyAutoGUI sends events to host computer)
                if self.use_windll_for_mouse:
                    print(f"[DEBUG] Using windll method for RDP environment")
                    self.marbot_auto_gui.click(x=x, y=y)
                else:
                    # Fallback to PyAutoGUI for non-RDP environments
                    pyautogui.moveTo(x, y)
                    time.sleep(0.1)
                    pyautogui.click(x=x, y=y)
                
                print(f"[DEBUG] Left click executed at ({x}, {y})")
                return ToolResult(output="Left click", action_base_type="click")
            elif action == "right_click":
                show_click(x, y)
                if self.use_windll_for_mouse:
                    print(f"[DEBUG] Using windll method for right click in RDP")
                    # Note: Right click not implemented in marbot_auto_gui, using left click for now
                    # TODO: Implement right click in MarbotAutoGUI
                    self.marbot_auto_gui.click(x=x, y=y)
                else:
                    pyautogui.moveTo(x, y)
                    time.sleep(0.1)
                    pyautogui.rightClick(x=x, y=y)
                print(f"[DEBUG] Right click executed at ({x}, {y})")
                return ToolResult(output="Right click", action_base_type="click")
            elif action == "middle_click":
                show_click(x, y)
                if self.use_windll_for_mouse:
                    print(f"[DEBUG] Using windll method for middle click in RDP")
                    # Note: Middle click not implemented in marbot_auto_gui, using left click for now
                    self.marbot_auto_gui.click(x=x, y=y)
                else:
                    pyautogui.moveTo(x, y)
                    time.sleep(0.1)
                    pyautogui.middleClick(x=x, y=y)
                print(f"[DEBUG] Middle click executed at ({x}, {y})")
                return ToolResult(output="Middle click", action_base_type="click")
            elif action == "double_click":
                show_click(x, y)
                if self.use_windll_for_mouse:
                    print(f"[DEBUG] Using windll method for double click in RDP")
                    self.marbot_auto_gui.doubleClick(x=x, y=y)
                else:
                    pyautogui.moveTo(x, y)
                    time.sleep(0.1)
                    pyautogui.doubleClick(x=x, y=y)
                print(f"[DEBUG] Double click executed at ({x}, {y})")
                return ToolResult(output="Double click", action_base_type="click")
            elif action == "triple_click":
                show_click(x, y)
                if self.use_windll_for_mouse:
                    print(f"[DEBUG] Using windll method for triple click in RDP")
                    # Triple click using windll method
                    self.marbot_auto_gui.click(x=x, y=y)
                    time.sleep(0.1)
                    self.marbot_auto_gui.click(x=x, y=y)
                    time.sleep(0.1)
                    self.marbot_auto_gui.click(x=x, y=y)
                else:
                    pyautogui.moveTo(x, y)
                    time.sleep(0.1)
                    pyautogui.click(x=x, y=y, clicks=3, interval=0.1)
                print(f"[DEBUG] Triple click executed at ({x}, {y})")
                return ToolResult(output="Triple click", action_base_type="click")
            elif action == "left_press":
                show_click(x, y)
                if self.use_windll_for_mouse:
                    print(f"[DEBUG] Using windll method for left press in RDP")
                    # Note: Left press (mouse down/up) not directly implemented, using click
                    self.marbot_auto_gui.click(x=x, y=y)
                else:
                    pyautogui.moveTo(x, y)
                    time.sleep(0.1)
                    pyautogui.mouseDown(x=x, y=y)
                    time.sleep(1)
                    pyautogui.mouseUp(x=x, y=y)
                print(f"[DEBUG] Left press executed at ({x}, {y})")
                return ToolResult(output="Left press", action_base_type="click")

            elif action == "scroll_down":
                pyautogui.scroll(-200)  # Adjust scroll amount as needed
                return ToolResult(output="Scrolled down", action_base_type="scroll")
            
            elif action == "scroll_up":
                pyautogui.scroll(200)   # Adjust scroll amount as needed
                return ToolResult(output="Scrolled up", action_base_type="scroll")
            
            elif action == "wait":
                time.sleep(15)
                return ToolResult(output="Wait for next event", action_base_type="wait")
            
            return ToolResult(output=f"Performed {action}", action_base_type="unknown")
        
        # Action Type 4: Miscs. No required text or coordinates
        # Actions: screenshot, cursor_position
        if action in ("screenshot", "cursor_position"):
            if text is not None:
                raise ToolError(output=f"text is not accepted for {action}", action_base_type="error")
            if coordinate is not None:
                raise ToolError(output=f"coordinate is not accepted for {action}", action_base_type="error")
            
            if action == "screenshot":
                return self.screenshot()
            elif action == "cursor_position":
                if self.use_windll_for_mouse:
                    # For RDP, we can't reliably get cursor position since PyAutoGUI reports host position
                    return ToolResult(output="Cursor position unavailable in RDP mode", action_base_type="unknown")
                else:
                    x, y = pyautogui.position()
                    return ToolResult(output=f"Cursor position ({x},{y})", action_base_type="unknown")

        # Action Type 5: StarRail Mode
        # Actions: sr_scroll_down, sr_scroll_up
        if action in ("sr_scroll_down", "sr_scroll_up"):
            if text is not None:
                raise ToolError(output=f"text is not accepted for {action}", action_base_type="error")

            if action == "sr_scroll_down":
                for _ in range(20):
                    pyautogui.scroll(-100)  # Adjust scroll amount as needed
                    time.sleep(0.001)
                return ToolResult(output="Scroll down", action_base_type="scroll")
            elif action == "sr_scroll_up":
                for _ in range(20):
                    pyautogui.scroll(100)   # Adjust scroll amount as needed
                    time.sleep(0.001)
                return ToolResult(output="Scroll up", action_base_type="scroll")

        # starrail browser mode
        if action in ("left_click_windll", "mouse_move_windll", "right_click_windll", "key_down_windll", "key_up_windll"):
            if action == "left_click_windll":
                if coordinate is None:
                    time.sleep(0.25)
                    x, y = pyautogui.position()
                    show_click(x, y)
                    self.marbot_auto_gui.click()
                else:
                    # The offset is removed to handle WebRDP environment correctly
                    x, y = coordinate
                    # x = coordinate[0]+self.offset_x
                    # y = coordinate[1]+self.offset_y
                    show_click(x, y)
                    time.sleep(0.25)
                    self.marbot_auto_gui.click(x=x, y=y)
                    # self.marbot_auto_gui.click(x=x, y=y)
                return ToolResult(output=f"Left click", action_base_type="click")

            elif action == "mouse_move_windll":
                if coordinate is None:
                    raise ToolError(output=f"coordinate is required for {action}", action_base_type="error")
                
                x0, y0 = pyautogui.position()
                # x0, y0 = self.scale_coordinates(ScalingSource.COMPUTER, x0, y0)
                # The offset is removed to handle WebRDP environment correctly
                x1, y1 = coordinate
                # x1 = coordinate[0]+self.offset_x
                # y1 = coordinate[1]+self.offset_y

                show_move_to(x0, y0, x1, y1)
                self.marbot_auto_gui.moveTo(x=x1, y=y1)
                time.sleep(0.25)
            
                return ToolResult(output=f"Mouse move", action_base_type="move")
            
            # elif action == "right_click_windll":
            #     self.marbot_auto_gui.rightClick(x=coordinate[0], y=coordinate[1])
            elif action == "key_down_windll":
                self.marbot_auto_gui.keyDown(text)
                time.sleep(0.25)
                return ToolResult(output=f"Key down '{text}'", type="hidden", action_base_type="key")
            
            elif action == "key_up_windll":
                time.sleep(0.25)
                self.marbot_auto_gui.keyUp(text)
                return ToolResult(output=f"Key up '{text}'", type="hidden", action_base_type="key")
            
            return ToolResult(output=f"Performed dll action:{action}", action_base_type="unknown")

        # WebRDP Testing
        if action == "test_webrdp_click":
            if coordinate is not None:
                test_result = self.test_webrdp_clicking(coordinate[0], coordinate[1])
            else:
                test_result = self.test_webrdp_clicking()
            return ToolResult(output=f"WebRDP click test completed: {test_result}", action_base_type="test")

        raise ToolError(output=f"Invalid action: {action}", type="hidden", action_base_type="error")


    def screenshot(self):
        """
        Take a screenshot of the hardcoded 1920x1080 area and return a ToolResult with the base64 encoded image.
        This ensures consistency with the /get_screenshot endpoint.
        """
        try:
            screenshot_pil, screenshot_path = capture_screenshot_1920(
                selected_screen=self.selected_screen,
                resize=False, # We want the raw 1920x1080 capture
            )
            
            with open(screenshot_path, "rb") as image_file:
                screenshot_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Clean up the temporary file
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)

            return ToolResult(base64_image=screenshot_base64, action_base_type="screenshot")

        except Exception as e:
            print(f"[ERROR] Screenshot failed in ComputerTool: {e}")
            raise ToolError(output=f"Failed to take screenshot: {e}", action_base_type="error")

    def get_screen_size(self):
        if platform.system() == "Windows":
            # Use screeninfo to get primary monitor on Windows
            screens = get_monitors()

            # Sort screens by x position to arrange from left to right
            sorted_screens = sorted(screens, key=lambda s: s.x)
            
            if self.selected_screen is None:
                primary_monitor = next((m for m in get_monitors() if m.is_primary), None)
                return primary_monitor.width, primary_monitor.height
            elif self.selected_screen < 0 or self.selected_screen >= len(screens):
                raise IndexError("Invalid screen index.")
            else:
                screen = sorted_screens[self.selected_screen]
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

            if self.selected_screen is None:
                # Find the primary monitor
                primary_monitor = next((screen for screen in screens if screen['is_primary']), None)
                if primary_monitor:
                    return primary_monitor['width'], primary_monitor['height']
                else:
                    raise RuntimeError("No primary monitor found.")
            elif self.selected_screen < 0 or self.selected_screen >= len(screens):
                raise IndexError("Invalid screen index.")
            else:
                # Return the resolution of the selected screen
                screen = sorted_screens[self.selected_screen]
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
    
    def get_mouse_position(self):
        # Use pyautogui for cross-platform compatibility
        return pyautogui.position()
    
    def ensure_window_focus(self):
        """
        Ensure the current window has focus, critical for WebRDP environments
        """
        if platform.system() == "Windows":
            try:
                # Get the foreground window
                hwnd = ctypes.windll.user32.GetForegroundWindow()
                if hwnd:
                    # Set foreground window to ensure it's active
                    ctypes.windll.user32.SetForegroundWindow(hwnd)
                    print(f"[DEBUG] Ensured window focus for WebRDP")
                    return True
            except Exception as e:
                print(f"[DEBUG] Could not ensure window focus: {e}")
        return False
    
    def test_webrdp_clicking(self, test_x=100, test_y=100):
        """
        Test method to validate WebRDP clicking functionality
        """
        print(f"[DEBUG] Testing WebRDP clicking at ({test_x}, {test_y})")
        
        if self.use_windll_for_mouse:
            print(f"[DEBUG] Testing windll method (RDP mode)")
            
            # Test animation
            show_click(test_x, test_y)
            
            # Test windll click
            self.marbot_auto_gui.click(x=test_x, y=test_y)
            
            # Test windll move
            self.marbot_auto_gui.moveTo(x=test_x + 50, y=test_y + 50)
            time.sleep(0.5)
            
            # Test another click
            show_click(test_x + 50, test_y + 50)
            self.marbot_auto_gui.click(x=test_x + 50, y=test_y + 50)
            
            return {
                "method_used": "windll",
                "rdp_mode": True,
                "test_completed": True
            }
        else:
            print(f"[DEBUG] Testing PyAutoGUI method (non-RDP mode)")
            
            # Record initial position
            initial_pos = pyautogui.position()
            print(f"[DEBUG] Initial mouse position: {initial_pos}")
            
            # Move to test position
            pyautogui.moveTo(test_x, test_y)
            time.sleep(0.1)
            
            # Check if move was successful
            moved_pos = pyautogui.position()
            print(f"[DEBUG] Position after move: {moved_pos}")
            
            # Test animation
            show_click(test_x, test_y)
            
            # Test click
            pyautogui.click(x=test_x, y=test_y)
            
            # Check final position
            final_pos = pyautogui.position()
            print(f"[DEBUG] Position after click: {final_pos}")
            
            # Return to initial position
            pyautogui.moveTo(initial_pos[0], initial_pos[1])
            
            return {
                "method_used": "pyautogui",
                "initial_pos": initial_pos,
                "moved_pos": moved_pos,
                "final_pos": final_pos,
                "move_successful": abs(moved_pos[0] - test_x) < 5 and abs(moved_pos[1] - test_y) < 5
            }



if __name__ == "__main__":
    computer = ComputerTool()
    # test left_click_windll
    # asyncio.run(computer(action="left_click_windll", coordinate=(500, 500)))
    asyncio.run(computer(action="mouse_move_windll", coordinate=(500, 500)))
    asyncio.run(computer(action="left_click_windll", coordinate=(500, 500)))