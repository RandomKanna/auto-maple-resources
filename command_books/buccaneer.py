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
    ROPE = 'ctrl'
    UP_JUMP = 'up+space'
    DOWN_JUMP = 'down+space'
    ADVANCED_DASH = 'shift'

    # Buffs
    BUFF_1              = '1'    # 
    ROLL_OF_THE_DICE    = 'home'    # 
    HOLY_SYMBOL         = '5'    # 
    ADVANCED_BLESSING   = '6'    #
    COMBAT_ORDERS       = '7'    # 
    SHARP_EYE           = '8'    # 
    SPEED_INFUSION      = '9'    # Speed Infusion
    MAPLE_WARRIOR       = '0'    # Maple Warrior


    # Potion
    GOLD_POT = '.'          #MPARK GOLD POT

    # Attack Skills
    SKILL_G = 'g'           #LOTD
    SKILL_D = 'd'           #Serpent Vortex
    SKILL_X = 'x'           #Hook Bomber
    SKILL_F = 'down+f'      #Erda Shower
    SKILL_A = 'a'           #True Arachnid Reflection
    SKILL_S = 's'           #Corkscrew Blow
    SKILL_R = 'r'           #Howling Fist


def step(direction, target):
    """
    Performs one movement step in the given DIRECTION towards TARGET.
    Should not press any arrow keys, as those are handled by Auto Maple.
    """

    d_y = target[1] - config.player_pos[1]
    d_x = target[0] - config.player_pos[0]

    if direction == 'left' or direction == 'right':
        utils.wait_for_is_standing(1000)
        d_y = target[1] - config.player_pos[1]
        d_x = target[0] - config.player_pos[0]
        if config.player_states['is_stuck'] and abs(d_x) < 16:
            print("is stuck")
            time.sleep(utils.rand_float(0.1, 0.2))
            press(Key.JUMP)
            Skill_X(direction='').execute()
            WaitStanding(duration='1').execute()
        if abs(d_x) >= 16:
            if abs(d_x) >= 60:
                FlashJump(direction='',triple_jump='false',fast_jump='false').execute()
                SkillCombination(direction='',jump='false',target_skills='skill_x').execute()
            elif abs(d_x) >= 28:
                FlashJump(direction='',triple_jump='false',fast_jump='false').execute()
                SkillCombination(direction='',jump='false',target_skills='skill_x').execute()
            else:
                if d_y == 0:
                    Skill_S().execute()
                else:
                    Skill_X(direction='',jump='true').execute()
            time.sleep(utils.rand_float(0.04, 0.06))
            # if abs(d_x) <= 22:
            #     key_up(direction)
            if config.player_states['movement_state'] == config.MOVEMENT_STATE_FALLING:
                SkillCombination(direction='',jump='false',target_skills='skill_x').execute()
            utils.wait_for_is_standing(500)
        else:
            time.sleep(utils.rand_float(0.05, 0.08))
            utils.wait_for_is_standing(500)
    
    if direction == 'up':
        utils.wait_for_is_standing(500)
        if abs(d_x) > settings.move_tolerance:
            return
        if abs(d_y) > 6 :
            if abs(d_y) > 36:
                press(Key.JUMP, 1)
                time.sleep(utils.rand_float(0.1, 0.15))
                press(Key.ROPE, 1)
                time.sleep(utils.rand_float(1.2, 1.5))
            elif abs(d_y) <= 25:
                UpJump().execute()
                SkillCombination(direction='',jump='false',target_skills='skill_x').execute()
            else:
                press(Key.ROPE, 1)
                time.sleep(utils.rand_float(1.2, 1.5))
                SkillCombination(direction='',jump='false',target_skills='skill_x').execute()
            utils.wait_for_is_standing(300)
        else:
            press(Key.JUMP, 1) 
            time.sleep(utils.rand_float(0.1, 0.15))

    if direction == 'down':
        if abs(d_x) > settings.move_tolerance:
            return
        down_duration = 0.15                #changed
        if abs(d_y) > 20:
            down_duration = 0.55            #changed
        elif abs(d_y) > 13:
            down_duration = 0.35            #changed
        
        if config.player_states['movement_state'] == config.MOVEMENT_STATE_STANDING and config.player_states['in_bottom_platform'] == False:
            # print("down stair")
            if abs(d_x) >= 5:
                if d_x > 0:
                    Fall(direction='right',duration=down_duration).execute()
                else:
                    Fall(direction='left',duration=down_duration).execute()
                
            else:
                Fall(direction='',duration=(down_duration+0.1)).execute()
                if config.player_states['movement_state'] == config.MOVEMENT_STATE_STANDING:
                    print("leave lader")
                    if d_x > 0:
                        key_down('left')
                        press(Key.JUMP)
                        key_up('left')
                    else:
                        key_down('right')
                        press(Key.JUMP)
                        key_up('right')
            SkillCombination(direction='',jump='false',target_skills='skill_x').execute()
                
        utils.wait_for_is_standing(2000)
        time.sleep(utils.rand_float(0.1, 0.12))

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
    """Uses each of Adele's buffs once."""

    def __init__(self):
        super().__init__(locals())
        self.cd120_buff_time = 0
        self.cd150_buff_time = 0
        self.cd180_buff_time = 0
        self.cd200_buff_time = 0
        self.cd240_buff_time = 0
        self.cd900_buff_time = 0
        self.decent_buff_time = 0

    def main(self):
        # buffs = [Key.SPEED_INFUSION, Key.HOLY_SYMBOL, Key.SHARP_EYE, Key.COMBAT_ORDERS, Key.ADVANCED_BLESSING]
        buffs = [Key.SPEED_INFUSION, Key.HOLY_SYMBOL, Key.COMBAT_ORDERS, Key.ADVANCED_BLESSING, Key.MAPLE_WARRIOR, Key.ROLL_OF_THE_DICE, Key.SHARP_EYE]
        now = time.time()
        utils.wait_for_is_standing(1000)
        if self.cd120_buff_time == 0 or now - self.cd120_buff_time > 121:
            self.cd120_buff_time = now
        if self.cd180_buff_time == 0 or now - self.cd150_buff_time > 151:
            self.cd150_buff_time = now
        if self.cd180_buff_time == 0 or now - self.cd180_buff_time > 181:
            # Skill_4().execute()
            self.cd180_buff_time = now
        if self.cd200_buff_time == 0 or now - self.cd200_buff_time > 200:
            self.cd200_buff_time = now
        if self.cd240_buff_time == 0 or now - self.cd240_buff_time > 240:
            self.cd240_buff_time = now
        if self.cd900_buff_time == 0 or now - self.cd900_buff_time > 900:
            self.cd900_buff_time = now
        if self.decent_buff_time == 0 or now - self.decent_buff_time > settings.buff_cooldown:
	        for key in buffs:
		        press(key, 3, up_time=0.3)
	        self.decent_buff_time = now		

class FlashJump(Command):
    """Performs a flash jump in the given direction."""
    _display_name = 'Flash Jump'

    def __init__(self, direction="",jump='false',combo='False',triple_jump="False",fast_jump="false",reverse_triple='false'):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.triple_jump = settings.validate_boolean(triple_jump)
        self.fast_jump = settings.validate_boolean(fast_jump)
        self.jump = settings.validate_boolean(jump)
        self.reverse_triple = settings.validate_boolean(reverse_triple)

    def main(self):
        if not self.jump:
            utils.wait_for_is_standing()
            if not self.fast_jump:
                self.player_jump(self.direction)
                time.sleep(utils.rand_float(0.02, 0.04)) # fast flash jump gap
            else:
                key_down(self.direction,down_time=0.05)
                press(Key.JUMP,down_time=0.06,up_time=0.05)
        else:
            key_down(self.direction,down_time=0.05)
            press(Key.JUMP,down_time=0.06,up_time=0.05)
        
        press(Key.FLASH_JUMP, 1,down_time=0.06,up_time=0.01)
        key_up(self.direction,up_time=0.01)
        if self.triple_jump:
            time.sleep(utils.rand_float(0.03, 0.05))
            # reverse_direction
            reverse_direction = ''
            if self.reverse_triple:
                if self.direction == 'left':
                    reverse_direction = 'right'
                elif self.direction == 'right':
                    reverse_direction = 'left'
                print('reverse_direction : ',reverse_direction)
                key_down(reverse_direction,down_time=0.05)
            else:
                time.sleep(utils.rand_float(0.02, 0.03))
            press(Key.FLASH_JUMP, 1,down_time=0.07,up_time=0.04) # if this job can do triple jump
            if self.reverse_triple:
                key_up(reverse_direction,up_time=0.01)
        time.sleep(utils.rand_float(0.01, 0.02))

class UpJump(BaseSkill):
    """Performs a up jump in the given direction."""
    _display_name = 'Up Jump'
    _distance = 27
    key=Key.UP_JUMP
    delay=0.1
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.1
    def main(self):
        self.jump = True
        super().main()
        
class Rope(BaseSkill):
    """Performs a up jump in the given direction."""
    _display_name = 'Rope Lift'
    _distance = 27
    key=Key.ROPE
    delay=1.4
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.2

class SuperJump(Command):
    """Performs a super jump in the given direction."""

    def __init__(self, direction):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)

    def main(self):
        key_down(self.direction)
        time.sleep(0.1)
        key_down(Key.ADVANCED_DASH)
        time.sleep(0.1)
        key_down(Key.JUMP)
        time.sleep(0.5)
        key_up(Key.ADVANCED_DASH)
        key_up(Key.JUMP)
        key_up(self.direction)



class Gold_Pot(BaseSkill):
    _display_name ='MP Gold Pot'
    key=Key.GOLD_POT
    delay=0.5
    rep_interval=0.5
    skill_cool_down=1800
    ground_skill=False
    buff_time=1800
    combo_delay = 0.2

class Skill_G(BaseSkill):
    _display_name ='Lord of the Deep'
    key=Key.SKILL_G
    delay=0.5
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=False
    buff_time=60
    combo_delay = 0.2
    skill_image = IMAGE_DIR + 'lotd.png'


class Skill_D(BaseSkill):
    _display_name ='Serpent Vortex'
    key=Key.SKILL_D
    delay=0.3
    rep_interval=0.25
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.1

class Skill_F(BaseSkill):
    _display_name ='Erda Shower'
    key=Key.SKILL_F
    delay=0.9
    rep_interval=0.25
    skill_cool_down=57
    ground_skill=True
    buff_time=60
    combo_delay = 0.3

class Skill_X(BaseSkill):
    _display_name = 'Hook Bomber'
    _distance = 27
    key=Key.SKILL_X
    delay=0.45
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.25

class Skill_A(BaseSkill):
    _display_name ='True Arachnid Reflection'
    key=Key.SKILL_A
    delay=0.6
    rep_interval=0.25
    skill_cool_down=240
    ground_skill=False
    buff_time=0
    combo_delay = 0.4

class Skill_S(BaseSkill):
    _display_name ='Corkscrew Blow'
    key=Key.SKILL_S
    delay=0.5
    rep_interval=0.25
    skill_cool_down=0
    ground_skill=True
    buff_time=0
    combo_delay = 0.3

    
class Skill_R(BaseSkill):
    _display_name ='Howling Fist'
    key=Key.SKILL_R
    delay=0.9
    rep_interval=0.25
    skill_cool_down=90
    ground_skill=False
    buff_time=90
    combo_delay = 0.3
    
