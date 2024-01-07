import time

import utilities.api.item_ids as ids
import utilities.color as clr
from utilities.geometry import RuneLiteObject
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
import pyautogui as pag


class OSRSConstruction(OSRSBot):
    def __init__(self):
        bot_title = "Construction bot (Black Atlass)"
        description = "Tables"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 60
        self.options_set = True

    def create_options(self):
        """
        Use the OptionsBuilder to define the options for the bot. For each function call below,
        we define the type of option we want to create, its key, a label for the option that the user will
        see, and the possible values the user can select. The key is used in the save_options function to
        unpack the dictionary of options after the user has selected them.
        """
        pass

    def save_options(self, options: dict):
        """
        For each option in the dictionary, if it is an expected option, save the value as a property of the bot.
        If any unexpected options are found, log a warning. If an option is missing, set the options_set flag to
        False.
        """
        pass


    def main_loop(self):
        """
        When implementing this function, you have the following responsibilities:
        1. If you need to halt the bot from within this function, call `self.stop()`. You'll want to do this
           when the bot has made a mistake, gets stuck, or a condition is met that requires the bot to stop.
        2. Frequently call self.update_progress() and self.log_msg() to send information to the UI.
        3. At the end of the main loop, make sure to call `self.stop()`.

        Additional notes:
        - Make use of Bot/RuneLiteBot member functions. There are many functions to simplify various actions.
          Visit the Wiki for more.
        - Using the available APIs is highly recommended. Some of all of the API tools may be unavailable for
          select private servers. For usage, uncomment the `api_m` and/or `api_s` lines below, and use the `.`
          operator to access their functions.
        """
        # Setup APIs
        api_m = MorgHTTPSocket()
        # api_s = StatusSocket()
        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            # -- Perform bot actions here --
            # Code within this block will LOOP until the bot is stopped.

            self.update_progress((time.time() - start_time) / end_time)
            self.buildTable()
            time.sleep(1)
            self.buildTable()
            time.sleep(1)
            self.buildTable()
            time.sleep(1)
            self.callServant()
            time.sleep(.4)
            self.buildTable()
            time.sleep(1)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def callServant(self):
        servant = self.get_nearest_tagged_NPC()
        self.mouse.move_to(servant.random_point())
        self.mouse.click(force_delay=True)
        time.sleep(.5)
        self.mouse.click(force_delay=True)
        time.sleep(.5)
        self.pressKey("1")

    def buildTable2(self, move=True):
        markers = self.get_all_tagged_in_rect(self.win.game_view, clr.GREEN)
        
        if move == True:
            self.mouse.move_to(markers[0].random_point())
            time.sleep(.1)

        self.mouse.click(button="right", force_delay=True)
        time.sleep(.5)
        self.mouse.click(force_delay=True)
        time.sleep(.8)
        self.pressKey("6")
        time.sleep(1)
        self.mouse.click(button="right",force_delay=True)
        time.sleep(.5)
        self.mouse.click(force_delay=True)
        time.sleep(.6)
        self.pressKey("1")

    def buildTable(self):
        marker = self.get_all_tagged_in_rect(self.win.game_view, clr.GREEN)[0]
        tabletag = self.get_nearest_tag(clr.RED)

        if tabletag != None:
            self.removeTable()

        if not self.isWithinRect(marker):
            self.mouse.move_to(marker.random_point())

        # Left click then right click build
        self.mouse.click(button="right", force_delay=True)
        time.sleep(rd.fancy_normal_sample(.2, .4))
        self.mouse.click(force_delay=True)
        time.sleep(rd.fancy_normal_sample(.6, .9))
        self.pressKey("6")
        # Wait until table is built
        while self.get_nearest_tag(clr.RED) == None:
            time.sleep(.1)

        # Remove table
        self.removeTable()

    def removeTable(self):
        marker = self.get_all_tagged_in_rect(self.win.game_view, clr.GREEN)[0]
        tabletag = self.get_nearest_tag(clr.RED)

        if tabletag == None:
            return False

        if not self.isWithinRect(marker):
            self.mouse.move_to(marker.random_point())


        self.mouse.click(button="right",force_delay=True)
        time.sleep(rd.fancy_normal_sample(.4, .6))
        self.mouse.click(force_delay=True)
        time.sleep(rd.fancy_normal_sample(.4, .6))
        self.pressKey("1")

    def isWithinRect(self, rect: RuneLiteObject):
        return rect.__point_exists(pag.position())

    def pressKey(self, key):
        pag.keyDown(key)
        LOWER_BOUND_CLICK = 0.2  # Milliseconds
        UPPER_BOUND_CLICK = 0.6  # Milliseconds
        AVERAGE_CLICK = 0.4  # Milliseconds
        time.sleep(rd.truncated_normal_sample(LOWER_BOUND_CLICK, UPPER_BOUND_CLICK, AVERAGE_CLICK))
        pag.keyUp(key)

    