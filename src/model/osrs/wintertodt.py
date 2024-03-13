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


class OSRSWintertodt(OSRSBot):
    def __init__(self):
        bot_title = "Wintertodt bot (Black Atlass)"
        description = "Wintertodt"
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
        self.api_s = StatusSocket()
        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60

        scraper = SpriteScraper()
        search_string = "Magic shortorb (u)"
        image_type = ImageType.ALL
        destination = scraper.DEFAULT_DESTINATION.joinpath("imgs")

        self.path = str(scraper.search_and_download(
            search_string=search_string,
            image_type=image_type,
            destination=destination,
            notify_callback=self.log_msg)) + "\\"
        
        self.prevPos = None
        self.xp = self.api_m.get_skill_xp("Firemaking")
        self.xp_time = time.time()
        self.xp_timeout = 30
        self.focus_timeout = 15
        self.focus_time = time.time()

        self.rootCount = 0

        while time.time() - start_time < end_time:
            # -- Perform bot actions here --
            # Code within this block will LOOP until the bot is stopped.

            self.update_progress((time.time() - start_time) / end_time)

            while False:
                time.sleep(.5)
                self.log_msg(str(self.api_m.get_is_player_idle())) 
                self.log_msg(str(self.api_m.get_animation()))
                self.log_msg(str(self.api_m.get_animation_id()))
            #self.log_msg(str(self.api_m.get_player_position()))

            self.bankAndGear()
            self.moveToGame()
            self.waitGameStart()

            while not self.isGameDone():
                self.chopRoots()

                if self.isGameDone():
                    break

                if self.rootCount <= 30:
                    self.fletchBatch()

                self.burnRoots()
                

            self.endGame()
            self.rootCount = 0

            #self.stop()
            xp = self.api_m.get_skill_xp("Firemaking")

            self.log_msg("Current xp: " + str(xp))
            if self.api_m.get_skill_xp("Firemaking") > 13030000:
                self.stop()
            
        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def waitGameStart(self):
        b_tag = None

        while not b_tag:
            b_tag = self.get_nearest_tag(clr.GREEN)
            time.sleep(.2)


    def isGameDone(self):
        end_img = self.searchImg("endimg.png", self.win.game_view, tries=5)
        return (end_img and len(self.get_all_tagged_in_rect(self.win.game_view, clr.YELLOW)) == 2)  or self.countItems(ids.SUPPLY_CRATE) == 1
    
    def endGame(self):
        tp_tag = self.getInvItem(ids.CONSTRUCT_CAPET)

        if not tp_tag:
            self.log_msg("TP cape not found")
            return
            
        self.mouse.move_to(tp_tag.random_point())
        self.mouse.click()
        time.sleep(5)

        pool_tag = None
        while not pool_tag:
                pool_tag = self.get_nearest_tag(clr.RED)

                if  pool_tag:
                    break

                time.sleep(.5)
            
        self.mouse.move_to(pool_tag.random_point())
        time.sleep(.5)
        self.mouse.click()
        time.sleep(2)
        self.waitForMovement()

        games_tag = None
        while not games_tag:
                games_tag = self.get_nearest_tag(clr.BLUE)

                if  games_tag:
                    break

                time.sleep(.5)
            
        self.mouse.move_to(games_tag.random_point())
        self.mouse.click()
        time.sleep(8)

    def checkHealth(self):

        hp = self.api_m.get_hitpoints()[0]
        if hp < 18 and self.countItems(ids.COOKED_KARAMBWAN) == 0:
            tp_tag = self.getInvItem(ids.CONSTRUCT_CAPET)

            if not tp_tag:
                self.log_msg("TP cape not found")
                return
            
            self.mouse.move_to(tp_tag.random_point())
            self.mouse.click()
            time.sleep(.5)

        if hp < 55:
            food_tag = self.getInvItem(ids.COOKED_KARAMBWAN, random=True)

            if not food_tag:
                self.log_msg("Out of food...")
                return
            
            self.mouse.move_to(food_tag.random_point())
            self.mouse.click()
            time.sleep(1)

    def fletchBatch(self):

        while self.countItems(ids.BRUMA_KINDLING) < 20:

            knife_tag = self.getInvItem(ids.KNIFE)
            log_tag = self.getInvItem(ids.BRUMA_ROOT, random=True)

            self.mouse.move_to(knife_tag.random_point())
            self.mouse.click()
            time.sleep(.3)

            self.mouse.move_to(log_tag.random_point())
            self.mouse.click()

            time.sleep(1)
            self.waitForIdleFletch()
              

    def burnRoots(self):

        first = True

        while self.countItems(ids.BRUMA_ROOT) + self.countItems(ids.BRUMA_KINDLING) > 0:
            brazier_tag = None
            count = 0
            broken = False

            while not brazier_tag:
                brazier_tag = self.get_nearest_tag(clr.GREEN)

                if  brazier_tag:
                    break

                brazier_tag = self.get_nearest_tag(clr.YELLOW)

                if  brazier_tag and self.rootCount < 50:
                    broken = True
                    break

                time.sleep(.1)           
                count += 1

                if count > 10:
                    self.log_msg("Brazier tag not found...")
                    return

                
            self.mouse.move_to(brazier_tag.random_point())
            self.mouse.click()

            first = False

            if first:
                time.sleep(2)

            self.waitForIdleBurn()

            self.checkHealth()

    def chopRoots(self):
        safespot = (1638, 3988, 0)

        count = 0
        while not self.api_m.get_is_inv_full() and self.rootCount + self.countItems(ids.BRUMA_ROOT) < 45 and self.countItems(ids.SUPPLY_CRATE) != 1:
            
            if self.api_m.get_player_position() != safespot:
                location_blue = self.get_nearest_tag(clr.BLUE)

                if location_blue:   
                    self.mouse.move_to(location_blue.random_point())
                    pag.keyDown("shift")
                    self.mouse.click()

                    pag.keyUp("shift")
                    self.checkHealth()
                    self.waitForIdle()

            if self.api_m.get_is_player_idle():
                root_tag = self.get_nearest_tag(clr.RED)

                if not root_tag:
                    self.log_msg("Root tag not found...")
                    return
                    
                self.mouse.move_to(root_tag.random_point())
                self.mouse.click()

            time.sleep(.3)
            self.checkHealth()
            count = self.countItems(ids.BRUMA_ROOT)
        
        # Inv full or enough for 500 points
        self.rootCount += count
        self.log_msg("Root count: " + str(self.rootCount))
        time.sleep(.2)       

    def moveToGame(self):
        location_blue = self.get_nearest_tag(clr.BLUE)

        if not location_blue:
            self.log_msg("Location blue not found...")
            return
        
        self.mouse.move_to(location_blue.random_point())
        self.mouse.click()

        time.sleep(2)
        self.waitForMovement()

        door_tag = self.get_nearest_tag(clr.YELLOW)
        
        if not door_tag:
            self.log_msg("Door tag not found...")
            return
        
        self.mouse.move_to(door_tag.random_point())
        self.mouse.click()

        self.waitForMovement()

        self.log_msg("Move to game P1 complete")
        time.sleep(7)

        location_blue = None
        while not location_blue:
            location_blue = self.get_nearest_tag(clr.BLUE)

            if not location_blue:
                self.log_msg("Location blue not found...")
            
            time.sleep(.2)
        
        self.mouse.move_to(location_blue.random_point())
        self.mouse.click()

        time.sleep(2)
        self.waitForMovement()

        self.log_msg("Move to game P2 complete")

    def bankAndGear(self):

        if self.countItems(ids.COOKED_KARAMBWAN) == 4 and self.countItems(ids.SUPPLY_CRATE) == 0:
            return

        bank_tag = self.get_nearest_tag(clr.RED)

        if not bank_tag:
            self.log_msg("Bank tag not found")
            time.sleep(2)
            bank_tag = self.get_nearest_tag(clr.RED)

        self.mouse.move_to(bank_tag.random_point())
        self.mouse.click()
        time.sleep(4)

        deposit_button = self.searchImg("depost_inv.png", self.win.game_view, tries=100)

        if not deposit_button:
            self.log_msg("Bank open timeout...")
            return
        
        # TODO open correct tab if

        crate_tag = self.getInvItem(ids.SUPPLY_CRATE)
        
        if crate_tag:
            self.mouse.move_to(crate_tag.random_point())
            self.mouse.click()

        food_tag = self.searchImg("karambwan.png", self.win.game_view)

        if not food_tag:
            self.log_msg("Could not find food...")
            return
        
        foodCount = self.countItems(ids.COOKED_KARAMBWAN)

        self.mouse.move_to(food_tag.random_point())
        for i in range(foodCount, 4):
            self.mouse.click()
            time.sleep(rd.truncated_normal_sample(.05, 1.2, .1))
        
        self.pressKey("ESC")
        time.sleep(rd.truncated_normal_sample(.3, 2, .8))
        self.log_msg("Banking complete")
            

    def checkBreak(self):
        if rd.random_chance(.001):
            self.log_msg("Taking break...")
            time.sleep(rd.truncated_normal_sample(4, 20, 12) * 60)
            self.xp_time = time.time()

    def waitForMovement(self):
        count = 0
        while self.api_m.get_animation_id() != 808:
            time.sleep(.2)
            count += 1

            if count > 20:
                break

    def waitForIdle(self):
        count = 0

        while self.api_m.get_is_player_idle() and count < 10:
            count += 1
            time.sleep(.05)

        count = 0

        while count < 50:
            time.sleep(.1)
            count += 1

            if self.api_m.get_is_player_idle():
                break

    def waitForIdleFletch(self):
        timeout = 2

        lastCount = self.countItems(ids.BRUMA_KINDLING)

        while lastCount < 20:
            time.sleep(timeout)
            currentCount = self.countItems(ids.BRUMA_KINDLING)
            if lastCount == currentCount and self.api_m.get_is_player_idle():
                return
            
            lastCount = currentCount

    def waitForIdleBurn(self):
        timeout = 2

        lastCount = self.countItems(ids.BRUMA_ROOT) + self.countItems(ids.BRUMA_KINDLING)

        while lastCount > 0:
            time.sleep(timeout)
            currentCount = self.countItems(ids.BRUMA_ROOT) + self.countItems(ids.BRUMA_KINDLING)
            if lastCount == currentCount and self.api_m.get_is_player_idle():
                return
            
            lastCount = currentCount
        

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
        self.isFocused()

    def isFocused(self):
        if time.time() - self.focus_time > self.focus_timeout:
            self.focus_time = time.time()
            self.log_msg("Not focused")
            return False

        self.focus_time = time.time()
        self.log_msg("Is focused")
        return True
    
    def hasMouseMoved(self):
        p = pag.position()
        
        if not self.prevPos or self.prevPos.x != p.x or self.prevPos.y != p.y or rd.random_chance(.15):
            self.prevPos = p
            return True
        
        return False


    def getInvItem(self, id, random=False) -> RuneLiteObject | None:
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
            time.sleep(.1)
        
        return img
    
    def countItems(self, item_id):
        return len(self.api_m.get_inv_item_indices(item_id))
        

    def pressKey(self, key):
        #self.log_msg("key press down" + key)
        pag.keyDown(key)
        LOWER_BOUND_CLICK = 0.08  # Milliseconds
        UPPER_BOUND_CLICK = 0.3  # Milliseconds
        AVERAGE_CLICK = 0.1  # Milliseconds
        time.sleep(rd.truncated_normal_sample(LOWER_BOUND_CLICK, UPPER_BOUND_CLICK, AVERAGE_CLICK))
        pag.keyUp(key)
        #self.log_msg("key press up" + key)

    