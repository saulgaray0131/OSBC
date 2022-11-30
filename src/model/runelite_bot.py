'''
The RuneLiteBot class contains properties and functions that are common across all RuneLite-based clients. This class
can be inherited by additional abstract classes representing all bots for a specific game (E.g., OSNRBot, AloraBot, etc.).

To determine Thresholds for finding contours: https://pinetools.com/threshold-image
For converting RGB to HSV:
    https://stackoverflow.com/questions/10948589/choosing-the-correct-upper-and-lower-hsv-boundaries-for-color-detection-withcv/48367205#48367205
'''
from abc import ABCMeta
from deprecated import deprecated
from model.bot import Bot, BotStatus
from model.window import Window
from typing import List
from utilities.geometry import Rectangle, Point, RuneLiteObject
import pyautogui as pag
import time
import utilities.bot_cv as bcv
import utilities.runelite_cv as rcv

class RuneLiteWindow(Window):

    current_action: Rectangle = None  # https://i.imgur.com/fKXuIyO.png
    hp_bar: Rectangle = None  # https://i.imgur.com/2lCovGV.png
    prayer_bar: Rectangle = None

    def __init__(self, window_title: str) -> None:
        '''
        RuneLiteWindow is an extensions of the Window class, which allows for locating and interacting with key
        UI elements on screen.
        '''
        super().__init__(window_title, padding_top=26, padding_left=0)
    
    def initialize(self) -> bool:
        '''
        Overrirde of Window.initialize(). This function is called when the bot is started.
        '''
        if not super().initialize():
            return False
        self.__locate_hp_prayer_bars()
        self.current_action = Rectangle(left=10 + self.game_view.left, top=24 + self.game_view.top, width=128, height=18)
        return True
    
    def __locate_hp_prayer_bars(self) -> None:
        '''
        Creates Rectangles for the HP and Prayer bars on either side of the control panel, storing it in the 
        class property.
        '''
        bar_w, bar_h = 18, 250  # dimensions of the bars
        self.hp_bar = Rectangle(left=self.control_panel.left + 7, top=self.control_panel.top + 42, width=bar_w, height=bar_h)
        self.prayer_bar = Rectangle(left=self.control_panel.left + 217, top=self.control_panel.top + 42, width=bar_w, height=bar_h)
    
    # Override
    def resize(self, width: int = 773, height: int = 534) -> None:
        '''
        Resizes the client window. Default size is 773x534 (minsize of fixed layout).
        Args:
            width: The width to resize the window to.
            height: The height to resize the window to.
        '''
        if client := self.window:
            client.size = (width, height)

class RuneLiteBot(Bot, metaclass=ABCMeta):

    win: RuneLiteWindow = None

    # --- Notable Colors [R, G, B] ---
    BLUE = [0, 255, 255]
    PURPLE = [255, 170, 0]
    PINK = [255, 0, 231]

    def __init__(self, title, description, window: Window = RuneLiteWindow("RuneLite")) -> None:
        super().__init__(title, description, window)

    @deprecated(reason="The OCR this function uses may be innacurate. Consider using an API function to check if player is idle.")
    def is_in_combat(self) -> bool:
        '''
        Returns whether the player is in combat. This is achieved by checking if text exists in the RuneLite opponent info
        section in the game view, and if that text indicates an NPC is out of HP.
        '''
        result = bcv.get_text_in_rect(self.win.current_action)
        return result.strip() != ""
    
    @deprecated(reason="The OCR this function uses may be innacurate. Consider using an API function to check if player is idle.")
    def is_player_doing_action(self, action: str):
        '''
        Returns whether the player is doing the given action.
        Args:
            action: The action to check for.
        Returns:
            True if the player is doing the given action, False otherwise.
        Example:
            if self.is_player_doing_action("Woodcutting"):
                print("Player is woodcutting!")
        '''
        return bcv.search_text_in_rect(self.win.current_action, [action], ["not", "nof", "nol"])

    # --- NPC/Object Detection ---
    def get_nearest_tagged_NPC(self, include_in_combat: bool = False) -> RuneLiteObject:
        # sourcery skip: use-next
        '''
        Locates the nearest tagged NPC, optionally including those in combat.
        Args:
            include_in_combat: Whether to include NPCs that are already in combat.
        Returns:
            A RuneLiteObject object or None if no tagged NPCs are found.
        '''
        game_view = self.win.game_view
        img_game_view = bcv.screenshot(game_view)
        # Isolate colors in image
        img_npcs = bcv.isolate_colors(img_game_view, [self.BLUE])
        img_hp_bars = bcv.isolate_colors(img_game_view, [self.GREEN, self.RED])
        # Locate potential NPCs in image by determining contours
        objs = rcv.extract_objects(img_npcs)
        if not objs:
            print("No tagged NPCs found.")
            return None
        for obj in objs:
            obj.set_rectangle_reference(self.win.game_view)
        # Sort shapes by distance from player
        objs = sorted(objs, key=RuneLiteObject.distance_from_rect_center)
        if include_in_combat:
            return objs[0]
        for obj in objs:
            if not rcv.is_point_obstructed(obj._center, img_hp_bars):
                return obj
        return None

    def get_all_tagged_in_rect(self, rect: Rectangle, color: List[int]) -> List[RuneLiteObject]:
        '''
        Finds all contours on screen of a particular color and returns a list of Shapes.
        Args:
            rect: A reference to the Rectangle that this shape belongs in (E.g., Bot.win.control_panel).
            color: The color to search for in [R, G, B] format.
        Returns:
            A list of RuneLiteObjects or empty list if none found.
        '''
        img_rect = bcv.screenshot(rect)
        bcv.save_image("get_all_tagged_in_rect.png", img_rect)
        isolated_colors = bcv.isolate_colors(img_rect, [color])
        objs = rcv.extract_objects(isolated_colors)
        for obj in objs:
            obj.set_rectangle_reference(rect)
        return objs
    
    def get_nearest_tag(self, color: List[int]) -> RuneLiteObject:
        '''
        Finds the nearest Shape of a particular color within the game view and returns its center Point.
        Args:
            color: The color to search for in [R, G, B] format.
        Returns:
            The nearest Shape to the character, or None if none found.
        '''
        if shapes := self.get_all_tagged_in_rect(self.win.game_view, color):
            shapes_sorted = sorted(shapes, key=RuneLiteObject.distance_from_rect_center)
            return shapes_sorted[0]
        else:
            return None

    # --- Client Settings ---
    @deprecated(reason="This method is no longer needed for RuneLite games that can launch with arguments through the OSBC client.")
    def logout_runelite(self):
        '''
        Identifies the RuneLite logout button and clicks it.
        '''
        self.log_msg("Logging out of RuneLite...")
        rl_login_icon = bcv.search_img_in_rect(f"{bcv.BOT_IMAGES}/runelite_logout.png", self.win.rectangle(), confidence=0.9)
        if rl_login_icon is not None:
            self.mouse.move_to(rl_login_icon.random_point())
            pag.click()
            time.sleep(0.2)
            pag.press('enter')
            time.sleep(1)
