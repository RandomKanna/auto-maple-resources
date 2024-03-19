"""A collection of all commands that a Bishop can use to interact with the game."""

from src.common import config, settings, utils
import time
import math
import random
from src.routine.components import Command
from src.common.vkeys import press, key_down, key_up


# List of key mappings
class Key:
    # Movement
    JUMP = 'space'
    TELEPORT = 'e'

    # Buffs
    MAPLE_WARRIOR = 'f1'
    ANGEL_OF_LIBRA = 'f2'
    PRAYER = 'f3'
    EPIC_ADVENTURE = 'f4'
    INFINITY = 'f5'
    INFINITY2 = 'f6'
    BAHAMUT = 'f7'
    MAPLE_GODNESS = 'f8'


    # Skills
    BIGBANG = 'r'
    ANGELRAY = 'q'
    PEACEMAKER = 'w'
    SEREN = 't'
    WILL = 'y'
    FOUNTAIN_OF_ANGEL = '2'
    HEAVEN_DOOR = 'f'
    ROPE = 'ctrl'
    HEAL = 'shift'
    ERDA_SHOWER = '1'
    ORIGIN = '8'


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
    press(Key.TELEPORT, num_presses)


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
                        Teleport('up').main()
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
    """Uses each of Bishop's buffs once."""

    def __init__(self):
        super().__init__(locals())
        self.buff1_time = 0
        self.buff2_time = 0
        self.origin_time = 0

    def main(self):
        buffs = {
            "buff1": [Key.ANGEL_OF_LIBRA, Key.INFINITY, Key.EPIC_ADVENTURE, Key.MAPLE_WARRIOR],
            "buff2": [Key.MAPLE_GODNESS, Key.PRAYER, Key.INFINITY2],  # Change this to your second set of buffs
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



class Teleport(Command):
    """
    Teleports in a given direction, jumping if specified. Adds the player's position
    to the current Layout if necessary.
    """

    def __init__(self, direction, jump='False'):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.jump = settings.validate_boolean(jump)

    def main(self):
        num_presses = 3
        time.sleep(0.05)
        if self.direction in ['up', 'down']:
            num_presses = 2
        if self.direction != 'up':
            key_down(self.direction)
            time.sleep(0.05)
        if self.jump:
            if self.direction == 'down':
                press(Key.JUMP, 3, down_time=0.1)
            else:
                press(Key.JUMP, 1)
        if self.direction == 'up':
            key_down(self.direction)
            time.sleep(0.05)
        press(Key.TELEPORT, num_presses)
        key_up(self.direction)
        if settings.record_layout:
            config.layout.add(*config.player_pos)


class AngelRay(Command):
    """Attacks using 'BigBang' in a given direction."""

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
            press(Key.ANGELRAY, self.attacks, up_time=0.05)
        key_up(self.direction)
        if self.attacks > 2:
            time.sleep(0.3)
        else:
            time.sleep(0.2)


class JumpBigBang(Command):
    """Uses 'Jump BigBang' once."""

    def __init__(self, jump='False'):
        super().__init__(locals())
        self.jump = settings.validate_boolean(jump)

    def main(self):
        if self.jump:
            press(Key.JUMP, 1, down_time=0.1, up_time=0.15)
        press(Key.BIGBANG, 2, up_time=0.05)


class JumpBigBangRandom(Command):
    """Uses 'Jump BigBang' once."""

    def __init__(self):
        super().__init__(locals())
        self.jump = random.choice([True, False])

    def main(self):
        if self.jump:
            press(Key.JUMP, 1, down_time=0.1, up_time=0.15)
        press(Key.BIGBANG, 2, up_time=0.05)


class PeaceMaker(Command):
    """Attacks using 'Peacemaker' in a given direction."""

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
            press(Key.PEACEMAKER, self.attacks, up_time=0.05)
        key_up(self.direction)
        if self.attacks > 2:
            time.sleep(0.3)
        else:
            time.sleep(0.2)


class BigBang(Command):
    """Uses 'Big Bang' once."""

    def main(self):
        press(Key.BIGBANG, 1, up_time=0.05)


class FountainOfAngel(Command):
    """
    Places 'Fountain of Angel' in a given direction, or towards the center of the map if
    no direction is specified.
    """

    def __init__(self, direction=None):
        super().__init__(locals())
        if direction is None:
            self.direction = direction
        else:
            self.direction = settings.validate_horizontal_arrows(direction)

    def main(self):
        if self.direction:
            press(self.direction, 1, down_time=0.1, up_time=0.05)
        else:
            if config.player_pos[0] > 0.5:
                press('left', 1, down_time=0.1, up_time=0.05)
            else:
                press('right', 1, down_time=0.1, up_time=0.05)
        press(Key.FOUNTAIN_OF_ANGEL, 3)


class HeavenDoor(Command):
    """Uses 'HeavenDoor' once."""

    def main(self):
        press(Key.HEAVEN_DOOR, 4, down_time=0.1, up_time=0.15)


class Rope(Command):
    """Uses 'Rope' once."""

    def main(self):
        press(Key.ROPE, 3)


class Seren(Command):
    """Uses 'Seren Core' once."""

    def main(self):
        press(Key.SEREN, 3)


class Will(Command):
    """Uses 'Will Core' once."""

    def main(self):
        press(Key.WILL, 3)


class Heal(Command):
    """Uses 'Heal' once."""

    def main(self):
        press(Key.HEAL, 3)


class ErdaShower(Command):
    """Uses 'ErdaShower' once."""

    def main(self):
        press(Key.ERDA_SHOWER, 3)


class Origin(Command):
    """Uses 'origin' once."""

    def main(self):
        press(Key.ORIGIN, 3)