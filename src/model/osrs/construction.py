import time

import utilities.api.item_ids as ids
import utilities.color as clr
from utilities.geometry import RuneLiteObject
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
import pyautogui as pag
import utilities.ocr as ocr


class OSRSConstruction(OSRSBot):
    def __init__(self):
        bot_title = "Construction bot (Black Atlass)"
        description = "Tables"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 60 * 3.85
        self.options_set = True
        self.onTableMarker = False

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
        self.api_m = MorgHTTPSocket()
        # api_s = StatusSocket()
        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        self.servant_away = False
        self.mouse.click_delay = True
        while time.time() - start_time < end_time:
            # -- Perform bot actions here --
            # Code within this block will LOOP until the bot is stopped.

            self.update_progress((time.time() - start_time) / end_time)
            self.buildTable()
            if not self.servant_away and len(self.api_m.get_inv_item_indices(ids.MAHOGANY_PLANK)) <= 7:
                self.callServant()
                         

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def callServant(self):
        servant = self.get_nearest_tagged_NPC()
        self.onTableMarker = False
        self.mouse.move_to(servant.random_point())
        self.mouse.click(force_delay=True)
        # Check if popup is ready then press 1
        while ocr.find_text("last", self.win.chat, ocr.QUILL_8, [clr.RED, clr.BLACK]) == None:
            self.log_msg("Looking for last")
            time.sleep(.05)
        time.sleep(rd.fancy_normal_sample(.6, .7))   
        self.pressKey("1")
        time.sleep(rd.fancy_normal_sample(.4, .5))
        self.servant_away = True   

    def buildTable(self):
        marker = self.get_all_tagged_in_rect(self.win.game_view, clr.GREEN)[0]
        tabletag = self.get_nearest_tag(clr.RED)
        
        if tabletag != None:
            self.log_msg("Table not found")
            self.removeTable()
            
        # Wait for servant
        if len(self.api_m.get_inv_item_indices(ids.MAHOGANY_PLANK)) < 6:
            s_count = 0
            while len(self.api_m.get_inv_item_indices(ids.MAHOGANY_PLANK)) <= 24:
                # Stuck servant
                if self.get_nearest_tagged_NPC() != None:
                    self.log_msg("servant idle: " + str(s_count))
                    s_count += 1

                if s_count >= 20:
                    self.callServant()
                    return

                self.log_msg("Waiting for servant")
                time.sleep(.1)
                
            self.servant_away = False
            time.sleep(rd.fancy_normal_sample(.2, .4))


        if not self.onTableMarker:
            self.mouse.move_to(marker.random_point())
            self.onTableMarker = True
        self.log_msg("8")

        self.log_msg("9")
        # Left click then right click build
        self.mouse.click(button="right", force_delay=True)
        while ocr.find_text("Build", self.win.game_view, ocr.BOLD_12, [clr.WHITE, clr.YELLOW]) == None:
            self.log_msg("Finding build")
            time.sleep(.05)
        self.log_msg("10")
        time.sleep(rd.fancy_normal_sample(.1, .3))
        self.mouse.click()
        
        while ocr.find_text("Creation", self.win.game_view, ocr.BOLD_12, [clr.ORANGE, clr.YELLOW]) == None:
            self.log_msg("Finding creation")
            time.sleep(.05)
        time.sleep(rd.fancy_normal_sample(.5, .6))
        self.pressKey("6")
        time.sleep(rd.fancy_normal_sample(.3, .4))
        self.log_msg("12")
        # Wait until table is built
        while self.get_nearest_tag(clr.RED) == None:
            self.log_msg("Looking for table tag")
            time.sleep(.05)

        self.log_msg("1")
        # Remove table
        self.removeTable()

    def removeTable(self):
        marker = self.get_all_tagged_in_rect(self.win.game_view, clr.GREEN)[0]
        tabletag = self.get_nearest_tag(clr.RED)

        if tabletag == None:
            self.buildTable()

        if not self.onTableMarker:
            self.mouse.move_to(marker.random_point())

        self.log_msg("2")
        self.mouse.click(button="right",force_delay=True)
        while ocr.find_text("Remove", self.win.game_view, ocr.BOLD_12, [clr.WHITE, clr.YELLOW]) == None:
            self.log_msg("Finding remove")
            time.sleep(.05)

        time.sleep(rd.fancy_normal_sample(.1, .3))
        self.mouse.click(force_delay=True)
        self.log_msg("3")
        # Check if popup is ready then press 6
        while ocr.find_text("remove", self.win.chat, ocr.QUILL_8, [clr.RED, clr.BLACK]) == None:
            self.log_msg("Finding remove chat")
            time.sleep(.05)
        time.sleep(rd.fancy_normal_sample(.6, .7))
        self.pressKey("1")
        time.sleep(rd.fancy_normal_sample(.4, .5))
        self.log_msg("4")
        
    def pressKey(self, key):
        self.log_msg("key press down" + key)
        pag.keyDown(key)
        LOWER_BOUND_CLICK = 0.08  # Milliseconds
        UPPER_BOUND_CLICK = 0.3  # Milliseconds
        AVERAGE_CLICK = 0.1  # Milliseconds
        time.sleep(rd.truncated_normal_sample(LOWER_BOUND_CLICK, UPPER_BOUND_CLICK, AVERAGE_CLICK))
        pag.keyUp(key)
        self.log_msg("key press up" + key)

    