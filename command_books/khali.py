"""A collection of all commands that Adele can use to interact with the game. 	"""

from src.common import config, settings, utils
import time
import math
from src.routine.components import Command
from src.common.vkeys import press, key_down, key_up


# List of key mappings
class Key:
    # Movement
    JUMP = 'alt'
    # ROPE_LIFT = "v"
    # BLINK_SHOT = "n"

    # 90s Buffs
    

    # 120s Buffs

    # 300s+ Buffs
    # MAPLE_WARRIOR = '5'
    
    # 2 hour familiar juice 
    # JUICE = "4"

    # Skills
    # ARROW_STREAM = "shift"
    # HURRICANE = 'a'


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
    press(Key.JUMP, num_presses)


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
                            time.sleep(utils.rand_float(0.04, 0.05))
                            walk_counter += 1
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('left')
                    else:
                        key_down('right')
                        while config.enabled and d_x > threshold and walk_counter < 60:
                            time.sleep(utils.rand_float(0.04, 0.05))
                            walk_counter += 1
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('right')
                    counter -= 1
            else:
                d_y = self.target[1] - config.player_pos[1]
                if abs(d_y) > settings.adjust_tolerance / math.sqrt(2):
                    if d_y < 0:
                        # stop moving
                        time.sleep(utils.rand_float(0.04, 0.05))
                        JumpUp().main()
                    else:
                        key_down('down')
                        time.sleep(utils.rand_float(0.04, 0.05))
                        press(Key.JUMP, 3, down_time=0.1)
                        key_up('down')
                        time.sleep(utils.rand_float(0.04, 0.05))
                    counter -= 1
            error = utils.distance(config.player_pos, self.target)
            toggle = not toggle

class Buff(Command):
    def __init__(self, BlinkShot=False):
        super().__init__(locals())
        self.cd90_buff_time = 0
        self.cd120_buff_time = 0
        self.cd300_buff_time = 0

    def main(self):
        now = time.time()

        # if self.cd90_buff_time == 0 or now - self.cd120_buff_time > 90:
        #     # press(Key.CONCENTRATION, 2)
        #     # press(Key.VICIOUS_SHOT, 2)
        #     self.cd90_buff_time = now
        if self.cd120_buff_time == 0 or now - self.cd120_buff_time > 120:
            # press(Key.QUIVER_BARRAGE, 1)
            # time.sleep(utils.rand_float(0.15, 0.2))
            # press(Key.STORM_OF_ARROWS, 1)
            # time.sleep(utils.rand_float(0.15, 0.2))
            # press(Key.INHUMAN_SPEED, 1)
            # time.sleep(utils.rand_float(0.15, 0.2))
            self.cd120_buff_time = now
        if self.cd300_buff_time == 0 or now - self.cd300_buff_time > 300:
            # press(Key.MAPLE_WARRIOR, 1)
            # time.sleep(utils.rand_float(0.15, 0.2))
            # press(Key.PHOENIX, 1)
            # time.sleep(utils.rand_float(0.15, 0.2))
            # press(Key.SHARP_EYES, 1)
            # time.sleep(utils.rand_float(0.15, 0.2))
            self.cd300_buff_time = now

# class ArrowStream(Command):
#     """ Performs Arrow Stream attack """
#     def __init__(self, direction):
#         super().__init__(locals())
#         self.direction = settings.validate_horizontal_arrows(direction)

#     def main(self):
#         time.sleep(utils.rand_float(0.04, 0.05))
#         press(self.direction, 1)
#         time.sleep(utils.rand_float(0.04, 0.05))
#         press(Key.ARROW_STREAM, 1)

# class ArrowStreamMulti(Command):
#     def __init__(self, direction, attacks=2, repetitions=1):
#         super().__init__(locals())
#         self.direction = settings.validate_horizontal_arrows(direction)
#         self.attacks = int(attacks)
#         self.repetitions = int(repetitions)

#     def main(self):
#         time.sleep(utils.rand_float(0.04, 0.05))
#         press(self.direction, 1)
#         time.sleep(utils.rand_float(0.04, 0.05))
#         for _ in range(self.repetitions):
#             press(Key.ARROW_STREAM, self.attacks)
#             time.sleep(utils.rand_float(0.05, 0.07))
#         time.sleep(0.1)

class FlashJump(Command):
    """Performs a flash jump in the given direction."""

    def __init__(self, direction):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)

    def main(self):
        if self.direction.upper() != "LEFT" and self.direction.upper() != "RIGHT":
            return
        key_down(self.direction)
        time.sleep(utils.rand_float(0.1, 0.15))
        press(Key.JUMP, 2)
        key_up(self.direction)
        time.sleep(utils.rand_float(0.5, 0.6))

class Arachnid(Command):
    """Uses 'True Arachnid Reflection' once."""
    def main(self):
        press(Key.ARACHNID, 3)


class JumpAtt(Command):
    """ jump arrow stream, only works with two directions: right or left"""
    def __init__(self, direction, attacks=2, repetitions=1):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.attacks = int(attacks)
        self.repetitions = int(repetitions)

    def main(self):
        time.sleep(utils.rand_float(0.04, 0.05))
        press(self.direction, 1)
        time.sleep(utils.rand_float(0.04, 0.05))
        for _ in range(self.repetitions):
            press(Key.JUMP, 1)
            time.sleep(utils.rand_float(0.04, 0.05))
            press(Key.ARROW_STREAM, self.attacks)
            time.sleep(utils.rand_float(0.2, 0.3))
        time.sleep(0.1)

class FlashJumpAtt(Command):
    """ flash jump arrow stream, only works with two directions: right or left"""
    def __init__(self, direction, times=1):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.times = int(times)

    def main(self):
        if self.direction != "left" and self.direction != "right":
            return
        
        key_down(self.direction)
        for i in range(self.times):
            print("loop ", i)
            time.sleep(utils.rand_float(0.1, 0.15))
            press(Key.JUMP, 2)

            press(Key.ARROW_STREAM, 1)
            time.sleep(utils.rand_float(0.3, 0.5))
        key_up(self.direction)

class JumpUp(Command):
    """ Jumps up"""

    def __init__(self, direction=None):
        super().__init__(locals())
        if direction is None:
            self.direction = direction
        else:
            self.direction = settings.validate_horizontal_arrows(direction)

    def main(self):
        time.sleep(utils.rand_float(0.1, 0.15))
        press(Key.JUMP, 1)
        time.sleep(utils.rand_float(0.1, 0.15))
        press("up", 1)
        time.sleep(utils.rand_float(0.1, 0.15))
        press("up", 1)
        time.sleep(utils.rand_float(0.1, 0.15))


class RopeLift(Command):
    """ Sets up / uses the 5th Job RopeLift skill - direction not affected"""

    def __init__(self):
        super().__init__(locals())

    def main(self):
        time.sleep(utils.rand_float(0.1, 0.15))
        press(Key.ROPE_LIFT, 2)
        time.sleep(utils.rand_float(0.1, 0.15))