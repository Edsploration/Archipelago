from typing import TYPE_CHECKING

from . import Locations
from .Options import CourseOrder, LogicDifficulty

if TYPE_CHECKING:
    from . import MK64World

LR = 0    # Luigi Raceway
MMF = 1   # Moo Moo Farm
KTB = 2   # Koopa Troopa Beach
KD = 3    # Kalimari Desert
TT = 4    # Toad's Turnpike
FS = 5    # Frappe Snowland
CM = 6    # Choco Mountain
MR = 7    # Mario Raceway
WS = 8    # Wario Stadium
SL = 9    # Sherbet Land
RoR = 10  # Royal Raceway
BC = 11   # Bowser's Castle
DK = 12   # D.K.'s Jungle Parkway
YV = 13   # Yoshi Valley
BB = 14   # Banshee Boardwalk
RaR = 15  # Rainbow Road

easy_course_pool = [LR, MMF, KD, TT, CM, MR]
medium_course_pool = easy_course_pool + [WS, SL, DK, BB]
hard_course_pool = medium_course_pool + [KTB, RoR, BC]


def determine_order(world: "MK64World") -> list[int]:
    # if using Universal Tracker, we've already filled in the course order
    if world.using_ut:
        return world.course_order

    random = world.random
    opt = world.opt

    match opt.course_order:
        case CourseOrder.option_short_to_long:
            return [MMF, MR, CM, KTB, LR, FS, BB, KD, SL, YV, BC, DK, RoR, TT, WS, RaR]
        case CourseOrder.option_long_to_short:
            return [RaR, WS, TT, RoR, DK, BC, YV, SL, KD, BB, FS, LR, KTB, CM, MR, MMF]
        case CourseOrder.option_alphabetical:
            return [BB, BC, CM, DK, FS, KD, KTB, LR, MR, MMF, RaR, RoR, SL, TT, WS, YV]
        case CourseOrder.option_shuffle:
            order = list(range(16))
            random.shuffle(order)
            if opt.final_pool:
                final = list(Locations.course_locations.keys()).index(random.choice(opt.final_pool))
            else:
                final = random.randrange(16)
            order.remove(final)
            order.append(final)
            if opt.logic == LogicDifficulty.option_no_logic:
                return order
            while True:  # do-while loop to choose good starting courses
                match opt.logic:
                    case LogicDifficulty.option_generous:
                        first = random.choice(easy_course_pool)
                        second = random.choice(medium_course_pool)
                    case LogicDifficulty.option_basic:
                        first = random.choice(medium_course_pool)
                        second = random.choice(hard_course_pool)
                    case _:  # LogicDifficulty.option_advanced
                        first = random.choice(hard_course_pool)
                        second = random.randrange(16)
                if first != second and first != final and second != final:
                    break
            order.remove(first)
            order.remove(second)
            return [first, second] + order
        case _:  # CourseOrder.option_vanilla
            return list(range(16))
