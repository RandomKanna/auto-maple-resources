"""A collection of all commands that Ark can use to interact with the game. 	"""

from src.common import config, settings, utils
import time
import math
from src.routine.components import Command
from src.common.vkeys import press, key_down, key_up


# List of key mappings
class Key:
    # Movement
    JUMP = 'space'
    FLASH_JUMP = 'space'

    # Buffs
    CONTROL_SPECTRAL = 'f3'
    CONTRACT_CARAVAN = 'f4'
    WEAPON_SOUL = 'f5'
    RETURN_HATRED = 'f6'
    CHARGE_SPELLAMP = 'f7'
    MAGIC_CIRCUIT = 'f8'
    INFINITY_SPELL = 'f9'
    LUCKY_DICE = 'end'
    GRANDIS_GODDESS = 'page up'
    OVERDRIVE = 'page down'

    # Buffs Toggle
    APPROACHING_DEATH = 'f10'

    # Skills
    PLAIN_DRIVE = 'q'
    NIGHTMARE = 'w'
    SCARLET_DRIVE = 'e'
    GUST_DRIVE = 't'
    ABYSS_DRIVE = 'a'
    CRAWLING_FEAR = 's'
    SEREN_CORE = '3'
    SPIDER_CORE = '4'
    ERDA_SHOWER = 'h'


#########################
#       Commands        #
#########################
def step(direction, target):
    """
    Performs one movement step in the given DIRECTION towards TARGET.
    Should not press any arrow keys, as those are handled by Auto Maple.
    """

    num_presses = 2
    if direction == 'up' or direction == 'down':
        num_presses = 1
    if config.stage_fright and direction != 'up' and utils.bernoulli(0.75):
        time.sleep(utils.rand_float(0.1, 0.3))
    d_y = target[1] - config.player_pos[1]
    if abs(d_y) > settings.move_tolerance * 1.5:
        if direction == 'down':
            press(Key.JUMP, 3)
        elif direction == 'up':
            press(Key.JUMP, 1)
    press(Key.FLASH_JUMP, num_presses)


class Adjust(Command):
    """Fine-tunes player position using small movements."""

    def __init__(self, x, y, max_steps=5):
        super().__init__(locals())
        self.target = (float(x), float(y))
        self.max_steps = settings.validate_nonnegative_int(max_steps)

    def main(self):
        counter = self.max_steps
        toggle = True
        error = utils.distance(config.player_pos, self.target)
        while config.enabled and counter > 0 and error > settings.adjust_tolerance:
            if toggle:
                d_x = self.target[0] - config.player_pos[0]
                threshold = settings.adjust_tolerance / math.sqrt(2)
                if abs(d_x) > threshold:
                    walk_counter = 0
                    if d_x < 0:
                        key_down('left')
                        while config.enabled and d_x < -1 * threshold and walk_counter < 60:
                            time.sleep(0.05)
                            walk_counter += 1
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('left')
                    else:
                        key_down('right')
                        while config.enabled and d_x > threshold and walk_counter < 60:
                            time.sleep(0.05)
                            walk_counter += 1
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('right')
                    counter -= 1
            else:
                d_y = self.target[1] - config.player_pos[1]
                if abs(d_y) > settings.adjust_tolerance / math.sqrt(2):
                    if d_y < 0:
                        FlashJump('up').main()
                    else:
                        key_down('down')
                        time.sleep(0.05)
                        press(Key.JUMP, 3, down_time=0.1)
                        key_up('down')
                        time.sleep(0.05)
                    counter -= 1
            error = utils.distance(config.player_pos, self.target)
            toggle = not toggle


class Buff(Command):
    """Uses each of ArK's buffs once."""

    def __init__(self):
        super().__init__(locals())
        self.cd65_buff_time = 0
        self.cd120_buff_time = 0
        self.cd240_buff_time = 0
        self.cd600_buff_time = 0

    def main(self):
        buffs = [Key.CHARGE_SPELLAMP, Key.OVERDRIVE, Key.INFINITY_SPELL,]
        now = time.time()

        if self.cd65_buff_time == 0 or now - self.cd65_buff_time > 65:
	        press(Key.OVERDRIVE, 2)
	        self.cd65_buff_time = now
        if self.cd120_buff_time == 0 or now - self.cd120_buff_time > 120:
	        press(Key.CHARGE_SPELLAMP, 2)
	        press(Key.INFINITY_SPELL, 2)
	        self.cd120_buff_time = now
        if self.cd240_buff_time == 0 or now - self.cd240_buff_time > 240:
	        press(Key.GRANDIS_GODDESS, 2)
	        self.cd240_buff_time = now
        if self.cd600_buff_time == 0 or now - self.cd600_buff_time > 600:
	        press(Key.CONTRACT_CARAVAN, 2)
	        self.cd600_buff_time = now


class FlashJump(Command):
    """Performs a flash jump in the given direction."""

    def __init__(self, direction):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)

    def main(self):
        key_down(self.direction)
        time.sleep(0.1)
        press(Key.FLASH_JUMP, 1)
        if self.direction == 'up':
            press(Key.FLASH_JUMP, 1)
        else:
            press(Key.FLASH_JUMP, 1)
        key_up(self.direction)
        time.sleep(0.5)

class PlainDrive(Command):
    """Attacks using 'Plain Drive' in a given direction."""

    def __init__(self, jump='False'):
        super().__init__(locals())
        self.jump = settings.validate_boolean(jump)

    def main(self):
        if self.jump:
            press(Key.JUMP, 1, down_time=0.1, up_time=0.15)
        press(Key.PLAIN_DRIVE, 2, up_time=0.05)


class Nightmare(Command):
    """Uses 'Nightmare' once."""

    def __init__(self, jump='False'):
        super().__init__(locals())
        self.jump = settings.validate_boolean(jump)

    def main(self):
        if self.jump:
            press(Key.JUMP, 1, down_time=0.1, up_time=0.15)
        press(Key.NIGHTMARE, 2, up_time=0.05)
		
class ScarletDrive(Command):
    """Uses 'Scarlet Drive' once."""

    def main(self):
        press(Key.SCARLET_DRIVE, 1, up_time=0.05)

class GustDrive(Command):
    """Uses 'Gust Drive' once."""

    def __init__(self, jump='False'):
        super().__init__(locals())
        self.jump = settings.validate_boolean(jump)

    def main(self):
        if self.jump:
            press(Key.JUMP, 1, down_time=0.1, up_time=0.15)
        press(Key.GUST_DRIVE, 2, up_time=0.05)

class AbyssDrive(Command):
    """Uses 'Abyss Drive' once."""

    def __init__(self, jump='False'):
        super().__init__(locals())
        self.jump = settings.validate_boolean(jump)

    def main(self):
        if self.jump:
            press(Key.JUMP, 1, down_time=0.1, up_time=0.15)
        press(Key.ABYSS_DRIVE, 2, up_time=0.05)


class CrawlingFear(Command):
    """Uses 'Crawling Fear' once."""

    def main(self):
        press(Key.CRAWLING_FEAR, 3)


class ControlSpectral(Command):
    """Uses 'Control Spectral' once."""

    def main(self):
        press(Key.CONTROL_SPECTRAL, 3)


class Seren Core(Command):
    """Uses 'Seren Core' once."""

    def main(self):
        press(Key.SEREN_CORE, 3)


class SPIDER_CORE(Command):
    """Uses 'Spider Core' once."""

    def main(self):
        press(Key.SPIDER_CORE, 3)


class ErdaShower(Command):
    """Uses 'Erda Shower' once."""

    def main(self):
        press(Key.ERDA_SHOWER, 2, down_time=0.1)
