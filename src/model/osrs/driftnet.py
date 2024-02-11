import time

import utilities.api.item_ids as ids
import utilities.color as clr
from utilities.geometry import RuneLiteObject
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
import pyautogui as pag
from utilities.sprite_scraper import SpriteScraper, ImageType
import utilities.ocr as ocr
import utilities.imagesearch as imsearch
import random as rand


class OSRSDriftNet(OSRSBot):
    def __init__(self):
        bot_title = "DriftNet bot (Black Atlass)"
        description = "DriftNet"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 60 * 5.21
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
        
        #scraper = SpriteScraper()
        #search_string = "Magic shortorb (u)"
        #image_type = ImageType.ALL
        #destination = scraper.DEFAULT_DESTINATION.joinpath("imgs")

        #self.path = str(scraper.search_and_download(
        #    search_string=search_string,
        #    image_type=image_type,
        #    destination=destination,
         #   notify_callback=self.log_msg)) + "\\"
        
        #self.log_msg(self.path)

        self.prevPos = None
        self.xp = self.api_m.get_skill_xp("Fishing")
        self.xp_time = time.time()
        self.xp_timeout = 30
        self.focus_timeout = 10
        self.focus_time = time.time()

        while time.time() - start_time < end_time:
            # -- Perform bot actions here --
            # Code within this block will LOOP until the bot is stopped.

            self.update_progress((time.time() - start_time) / end_time)

            self.clickSpot()
            self.sleepMouse()
            self.checkBreak()

            self.waitFish()
            self.checkBreak()

            self.checkInventory()
            self.checkBreak()
            
            xp = self.api_m.get_skill_xp("Fishing")

            if xp == self.xp and (time.time() - self.xp_time > self.xp_timeout):
                self.log_msg("XP timeout...")
                self.stop()

            self.xp = xp
            self.xp_time = time.time()

            self.log_msg("Current xp: " + str(xp))
            if self.api_m.get_skill_xp("Fishing") > 13030000:
                self.stop()
            
        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def checkBreak(self):
        if rd.random_chance(.002):
            self.log_msg("Taking break...")
            time.sleep(rd.truncated_normal_sample(4, 20, 12) * 60)

    def clickSpot(self):

        if not self.isFocused():
            time.sleep(rd.truncated_normal_sample(2, 30, 4))

        spot_tag = self.get_nearest_tag(clr.RED)

        if spot_tag == None:
            self.log_msg("No fishing spots found")
            return 1
        
        self.mouse.move_to(spot_tag.random_point())
        time.sleep(rd.truncated_normal_sample(.05, 1.2, .1))
        self.mouse.click()

        time.sleep(4)

    def waitFish(self):
        count = 0
        while count < 500:
            if(self.api_m.get_is_inv_full()):
                self.log_msg("Inventory Full")
                return 2
            
            if(self.api_m.get_is_player_idle()):
                self.log_msg("Player Idle")
                return 3
            
            time.sleep(.5)
            count += 1

    def sleepMouse(self):
        sleep_view = rd.random.choice([self.win.chat, self.win.control_panel, rd.random.choice(self.win.spellbook_normal), None, None, None])
        time.sleep(rd.truncated_normal_sample(1, 6, 3.2))

        if sleep_view == None:
            return
        
        self.mouse.move_to(sleep_view.random_point(), mouseSpeed="medium", knotsCount=1)

    def checkInventory(self):
        if(self.api_m.get_is_inv_full() == False):
                self.log_msg("Inventory Not Full")
                return 2
        

        self.log_msg("Dropping items...")
        if not self.isFocused():
            time.sleep(rd.truncated_normal_sample(2, 60, 4))
        else:
            time.sleep(1)

        skip_slots = [0, 1]
        skip_slots[0] = self.api_m.get_first_occurrence(ids.BARBARIAN_ROD)
        skip_slots[1] = self.api_m.get_first_occurrence(ids.FEATHER)

        self.drop_all(skip_slots=skip_slots)
        time.sleep(rd.truncated_normal_sample(.5, 3, .6))

    def isFocused(self):
        if time.time() - self.focus_time > self.focus_timeout:
            self.focus_time = time()
            return True

        self.focus_time = time()
        return False 
    
    def hasMouseMoved(self):
        p = pag.position()
        
        if not self.prevPos or self.prevPos.x != p.x or self.prevPos.y != p.y or rd.random_chance(.15):
            self.prevPos = p
            return True
        
        return False


    def getInvItem(self, id, random=False):
        index = -1
        if not random:
            index = self.api_m.get_first_occurrence(id)
        
        else:
            index = rand.choice(self.api_m.get_inv_item_indices(id))

        if index == -1:
            return None
        
        self.log_msg(str(id) + " found at index: " + str(index))
        return self.win.inventory_slots[index]
    
        
    def searchImg(self, imgpath, view, tries = 20):
        img = imsearch.search_img_in_rect(self.path + imgpath, view)

        count = 0
        while img == None:
            if count >= tries:
                self.log_msg(imgpath + " not found")
                return None
            img = imsearch.search_img_in_rect(self.path + imgpath, view)
            count += 1
            time.sleep(.05)
        
        return img
        

    def pressKey(self, key):
        #self.log_msg("key press down" + key)
        pag.keyDown(key)
        LOWER_BOUND_CLICK = 0.08  # Milliseconds
        UPPER_BOUND_CLICK = 0.3  # Milliseconds
        AVERAGE_CLICK = 0.1  # Milliseconds
        time.sleep(rd.truncated_normal_sample(LOWER_BOUND_CLICK, UPPER_BOUND_CLICK, AVERAGE_CLICK))
        pag.keyUp(key)
        #self.log_msg("key press up" + key)

    