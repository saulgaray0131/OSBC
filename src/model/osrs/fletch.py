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


class OSRSFletching(OSRSBot):
    def __init__(self):
        bot_title = "Fletching bot (Black Atlass)"
        description = "bows"
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
        
        scraper = SpriteScraper()
        search_string = "Magic shortbow (u)"
        image_type = ImageType.ALL
        destination = scraper.DEFAULT_DESTINATION.joinpath("imgs")

        self.path = str(scraper.search_and_download(
            search_string=search_string,
            image_type=image_type,
            destination=destination,
            notify_callback=self.log_msg)) + "\\"
        
        self.log_msg(self.path)

        while time.time() - start_time < end_time:
            # -- Perform bot actions here --
            # Code within this block will LOOP until the bot is stopped.

            self.update_progress((time.time() - start_time) / end_time)

            self.openBank()
            self.getItems()           
            self.closeBank()
            self.fletchItems()
            self.waitFletch()
            self.openBank()
            self.emptyInv()
            
            
                         

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def openBank(self):
        if len(self.api_m.get_inv_item_indices(ids.BOW_STRING)) == 14 and len(self.api_m.get_inv_item_indices(ids.MAGIC_SHORTBOW_U)) == 14:
            self.log_msg("Items already in inv, bank")
            return
        
        bank_tag = self.get_nearest_tag(clr.BLUE)

        if bank_tag == None:
            self.log_msg("Bank tag not found")
            return
        
        self.mouse.move_to(bank_tag.random_point())
        time.sleep(rd.fancy_normal_sample(.1, .2))
        #count = 0
        #while self.mouseover_text(["Bank", "booth", "BankBankbooth"], clr.OFF_CYAN) == False:
        #    if count >= 20:
        #        self.log_msg("Bad bank mouse move to: " + self.mouseover_text())
        #        return
        #    time.sleep(.05)
        #    count += 1
        self.mouse.click()

        time.sleep(rd.fancy_normal_sample(.1, .2))

        count = 0
        while ocr.find_text(["Rearrange", "Withdraw", "Quantity"], self.win.game_view, ocr.PLAIN_12, clr.ORANGE) == None:
            if count >= 20:
                self.log_msg("Bank open search timed out...")
                return
            time.sleep(.05)
            count += 1

        self.log_msg("Bank open")
        time.sleep(rd.fancy_normal_sample(.2, .4))

    def getItems(self):

        if len(self.api_m.get_inv_item_indices(ids.BOW_STRING)) == 14 and len(self.api_m.get_inv_item_indices(ids.MAGIC_SHORTBOW_U)) == 14:
            self.log_msg("Items already in inv")
            return

        if not self.api_m.get_is_inv_empty():
            self.log_msg("Inventory is not empty")
            self.emptyInv()

        bow_img = self.searchImg("bowu.png", self.win.game_view)
        string_img = self.searchImg("string.png", self.win.game_view)

        if bow_img == None:
            self.log_msg("Get bow img not found")
            return
        
        if string_img == None:
            self.log_msg("Get bow string img not found")
            return

        self.mouse.move_to(bow_img.random_point(), mouseSpeed="fastest")
        if self.mouseover_text(["Magic", "shortbow", "short", "bow", "(u)"], clr.OFF_ORANGE) == False:
            self.log_msg("Bad bow move to: " + self.mouseover_text())
            return
        self.mouse.click()
        count = 0
        while not len(self.api_m.get_inv_item_indices(ids.MAGIC_SHORTBOW_U)) == 14:
            if count >= 20:
                self.log_msg("Bow click timed out")
                return
            time.sleep(.025)
            count += 1

        self.mouse.move_to(string_img.random_point(), mouseSpeed="fastest")
        if self.mouseover_text(["Bow", "string"], clr.OFF_ORANGE) == False:
            self.log_msg("Bad bow string move to: " + self.mouseover_text())
            return
        self.mouse.click()
        count = 0
        while not len(self.api_m.get_inv_item_indices(ids.BOW_STRING)) == 14:
            if count >= 20:
                self.log_msg("Bow string click timed out")
                return
            time.sleep(.025)
            count += 1
        time.sleep(rd.fancy_normal_sample(.1, .2))


    def fletchItems(self):
        if self.api_m.get_is_inv_empty():
            self.log_msg("Inventory is empty")
            return
        
        if len(self.api_m.get_inv_item_indices(ids.MAGIC_SHORTBOW_U)) != 14:
            self.log_msg("Invalid amount of bows u")
            return
        
        if len(self.api_m.get_inv_item_indices(ids.BOW_STRING)) != 14:
            self.log_msg("Invalid amount of bow string")
            return
        
        #bow_img = self.getInvItem(ids.MAGIC_SHORTBOW_U)
        #string_img = self.getInvItem(ids.BOW_STRING)

        inv_slots = rand.choice([(12,16),(16,13), (13,14)])

        bow_img = self.win.inventory_slots[inv_slots[0]]
        string_img = self.win.inventory_slots[inv_slots[1]]

        self.mouse.move_to(bow_img.random_point(), mouseSpeed="fastest")
        #if self.mouseover_text(["Magic", "shortbow", "short", "bow", "(u)"], clr.OFF_ORANGE) == False:
        #    self.log_msg("Bad bow move to: " + self.mouseover_text())
        #    return
        self.mouse.click()
        time.sleep(rd.fancy_normal_sample(.1, .3))

        self.mouse.move_to(string_img.random_point(), mouseSpeed="fastest")
        #if self.mouseover_text(["Bow", "string"], clr.OFF_ORANGE) == False:
        #    self.log_msg("Bad bow string move to: " + self.mouseover_text())
        #    return
        self.mouse.click()
        time.sleep(rd.fancy_normal_sample(.2, .4))

        fletch_start = self.searchImg("bow_chat.png", self.win.chat)
        if fletch_start == None:
            self.log_msg("Fletch box search timed out...")
            return
        time.sleep(rd.fancy_normal_sample(.5, .7))
        self.pressKey("space")
        time.sleep(rd.fancy_normal_sample(.6, .8))

    def waitFletch(self):
        if not self.api_m.get_if_item_in_inv(ids.MAGIC_SHORTBOW_U):
            self.log_msg("Bows not found in inv")
            return
        
        if not self.api_m.get_if_item_in_inv(ids.BOW_STRING):
            self.log_msg("Bowstring not found in inv")
            return
        
        count = 0
        while len(self.api_m.get_inv_item_indices(ids.MAGIC_SHORTBOW)) != 14:
            if count > 20:
                self.log_msg("Fletch wait timed out")
                return
            count += 1
            time.sleep(1)

        time.sleep(rd.fancy_normal_sample(.5, .8))


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

    def closeBank(self):     

        if len(self.api_m.get_inv_item_indices(ids.BOW_STRING)) == 14 and len(self.api_m.get_inv_item_indices(ids.MAGIC_SHORTBOW_U)) == 14:
            self.log_msg("Items already in inv, bank")
            return

        count = 0
        while ocr.find_text(["Rearrange", "Withdraw", "Quantity"], self.win.game_view, ocr.PLAIN_12, clr.ORANGE) == None:
            if count >= 20:
                self.log_msg("Bank open search timed out (close)...")
                return
            time.sleep(.05)
            count += 1

        self.pressKey("esc")

        if ocr.find_text(["Rearrange", "Withdraw", "Quantity"], self.win.game_view, ocr.PLAIN_12, clr.ORANGE):
            self.log_msg("Bank was not closed")
            self.closeBank()
            return
        
        count = 0
        while self.get_nearest_tag(clr.BLACK) == None:
            if count >= 20:
                self.log_msg("Could not find bank tag after close")
                return
            
        self.log_msg("Bank closed")
        time.sleep(rd.fancy_normal_sample(.1, .2))

    def emptyInv(self):    

        if self.api_m.get_is_inv_empty():
            self.log_msg("Inv is already empty")
            return

        count = 0
        while ocr.find_text(["Rearrange", "Withdraw", "Quantity"], self.win.game_view, ocr.PLAIN_12, clr.ORANGE) == None:
            if count >= 20:
                self.log_msg("Bank open search timed out (empty inv)...")
                return
            time.sleep(.05)
            count += 1
        
        deposit = self.searchImg("depost_inv.png", self.win.game_view)
        if deposit == None:
            self.log_msg("Deposit button not found")
            return
        self.mouse.move_to(deposit.random_point())
        self.mouse.click()

        count = 0
        while not self.api_m.get_is_inv_empty():
            if count >= 20:
                self.log_msg("Empty inv timed out")
                return
            time.sleep(.05)
            count += 1
            
        self.log_msg("Inv empty")
        time.sleep(rd.fancy_normal_sample(.05, .1))
        
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

    