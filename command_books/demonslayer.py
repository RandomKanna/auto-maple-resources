"""A collection of all commands that Adele can use to interact with the game. 	"""

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
    ORTHRUS = 'f1'
    DEMONIC_FORTITUDE = 'f2'
    AURA_WEAPON = 'f3'
    DEMON_AWAKENING = 'f4'
    CALL_MASTERMA = 'f5'
    GODNESS = 'f6'

    # Skills
    DEMON_THRASH = 'q'
    INFERNAL_CONCUSSION = 'w'
    DEMON_CRY = 'e'
    DEMON_IMPACT = 't'
    CERBURUS = 'a'
    ORIGIN = 'f'
    JORMUNGAND = 's'
    LUCID_SOUL = '3'
    SPIDER_CORE = '4'
    SEREN_CORE = '5'
    ROPE_CONNECT = 'u'
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
            press('up', 3)
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
                        press(Key.ROPE_CONNECT, 1)
                        time.sleep(2)
                    else:
                        key_down('down')
                        press(Key.JUMP, 2)
                        key_up('down')
                    counter -= 1
            error = utils.distance(config.player_pos, self.target)
            toggle = not toggle


class Buff(Command):
    """Uses each of DemonSlayer's buffs once."""

    def __init__(self):
        super().__init__(locals())
        self.buff1_time = 0
        self.buff2_time = 0
        self.origin_time = 0

    def main(self):
        buffs = {
            "buff1": [Key.DEMON_AWAKENING, Key.AURA_WEAPON, Key.DEMONIC_FORTITUDE],
            "buff2": [Key.ORTHRUS, Key.AURA_WEAPON, Key.CALL_MASTERMA, Key.GODNESS],  # Change this to your second set of buffs
            "origin": [Key.ORIGIN]
        }
        now = time.time()

        # Check and activate buff1 if it's not currently active and its cooldown has passed
        if (self.buff1_time == 0 or now - self.buff1_time > 180) and (self.buff2_time == 0 or now - self.buff2_time > 60):
            for key in buffs["buff1"]:
                press(key, 3, up_time=0.3)
            self.buff1_time = now

        # Check and activate buff2 if it's not currently active and its cooldown has passed
        if (self.buff2_time == 0 or now - self.buff2_time > 180) and (self.buff1_time == 0 or now - self.buff1_time > 60):
            for key in buffs["buff2"]:
                press(key, 3, up_time=0.3)
            self.buff2_time = now

        # Check and activate origin after 365 seconds
        if self.buff1_time != 0 and (self.origin_time == 0 or now - self.origin_time > 365):
            for key in buffs["origin"]:
                press(key, 1, up_time=0.3)
            self.origin_time = now

			
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
            # Additional actions for jumping twice upwards
            press(Key.UP_ARROW, 1)  # First jump upward
            time.sleep(0.1)  # Adjust sleep time if necessary
            press(Key.UP_ARROW, 1)  # Second jump upward
        key_up(self.direction)
        time.sleep(0.5)


class FlashJumpUp(Command):
    """Performs a flash jump up."""

    def __init__(self, direction):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)

    def main(self):
        press(Key.JUMP, 1)  # Press the "JUMP" key once
        time.sleep(0.1)  # Add a small delay for synchronization
        press(Key.UP, 2)  # Press the "UP" key twice


			
class DemonThrash(Command):
    """Attacks using 'Demon Thrash' in a given direction."""

    def __init__(self, direction, attacks=2, repetitions=1):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.attacks = int(attacks)
        self.repetitions = int(repetitions)

    def main(self):
        time.sleep(0.05)
        key_down(self.direction)
        time.sleep(0.05)
        if config.stage_fright and utils.bernoulli(0.7):
            time.sleep(utils.rand_float(0.1, 0.3))
        for _ in range(self.repetitions):
            press(Key.DEMON_THRASH, self.attacks, up_time=0.05)
        key_up(self.direction)
        if self.attacks > 1:
            time.sleep(0.3)
        else:
            time.sleep(0.2)


class InfernalConcussion(Command):
    """Uses 'Infernal Concussion' once."""

    def main(self):
        press(Key.INFERNAL_CONCUSSION, 1, up_time=0.05)

class FlashJumpInfernalConcussion(Command):
    """Uses 'Double Jump Infernal Concussion' once."""

    def __init__(self, jump=True):
        super().__init__(locals())
        self.jump = settings.validate_boolean(jump)

    def main(self):
        if self.jump:
            press(Key.JUMP, 1, down_time=0.1, up_time=0.15)
            press(Key.JUMP, 1, down_time=0.1, up_time=0.15)
        press(Key.INFERNAL_CONCUSSION, 2, up_time=0.05)
		
class DemonCry(Command):
    """Uses 'Demon Cry' once."""

    def main(self):
        press(Key.DEMON_CRY, 1, up_time=0.05)

class JumpDemonCry(Command):
    """Uses 'Double Jump Demon Cry' once."""

    def __init__(self, jump=True):
        super().__init__(locals())
        self.jump = settings.validate_boolean(jump)

    def main(self):
        if self.jump:
            press(Key.JUMP, 1, down_time=0.1, up_time=0.15)
        press(Key.DEMON_CRY, 2, up_time=0.05)

class DemonImpact(Command):
    """Uses 'Demon Impact' once."""

    def main(self):
        press(Key.DEMON_IMPACT, 1, up_time=0.05)

class FlashJumpDemonImpact(Command):
    """Uses 'Double Jump Demon Impact' once."""

    def __init__(self, jump=True):
        super().__init__(locals())
        self.jump = settings.validate_boolean(jump)

    def main(self):
        if self.jump:
            press(Key.JUMP, 1, down_time=0.1, up_time=0.15)
            press(Key.JUMP, 1, down_time=0.1, up_time=0.15)
        press(Key.DEMON_IMPACT, 2, up_time=0.05)

class Cerburus(Command):
    """Uses 'Cerburus' once."""

    def main(self):
        press(Key.CERBURUS, 1, up_time=0.05)

class Jormungand(Command):
    """Uses 'Jormungand' once."""

    def main(self):
        press(Key.JORMUNGAND, 1, up_time=0.05)


class SpiderCore(Command):
    """Uses 'Spider Core' once."""

    def main(self):
        press(Key.SPIDER_CORE, 2)


class ErdaShower(Command):
    """Uses 'Erda Shower' once."""

    def main(self):
        press(Key.ERDA_SHOWER, 2, down_time=0.1)		


class SerenCore(Command):
    """Uses 'Seren Core' once."""

    def main(self):
        press(Key.SEREN_CORE, 2)


class Origin(Command):
    """Uses 'Origin' once."""

    def main(self):
        press(Key.ORIGIN, 2)

class RopeConnect(Command):
    """Uses 'Rope' once."""

    def main(self):
        press(Key.ROPE_CONNECT, 2)


