from typing import TYPE_CHECKING
from enum import IntFlag, auto

from BaseClasses import Item, ItemClassification

from .Locations import cup_events
from .Options import GameMode, ShuffleDriftAbilities, Goal

if TYPE_CHECKING:
    from . import MK64World


class MK64Item(Item):
    game: str = "Mario Kart 64"


class Group(IntFlag):
    base = auto()
    special = auto()
    feather = auto()
    two_player = auto()
    two_player_feather = auto()
    kart = auto()
    drift = auto()
    traction = auto()
    starting_items = auto()
    railings = auto()
    fences = auto()
    box_respawning = auto()
    special_box = auto()
    item_boxes = auto()
    queueable = auto()
    trap = auto()


def create_item(name: str, player: int, classification: ItemClassification = -1) -> Item:
    item_data = item_table[name]
    if classification == -1:
        classification = item_data[2]
    return MK64Item(name, classification, item_data[0], player)


def create_items(world: "MK64World"):
    player = world.player
    opt = world.opt
    num_filler = world.num_filler_items
    itempool = world.multiworld.itempool
    random = world.random

    item_group_mask = (Group.base
                       | (opt.feather and Group.feather)
                       | (opt.two_player and Group.two_player)
                       | (opt.feather and opt.two_player and Group.two_player_feather)
                       | (opt.drift and Group.drift)
                       | (opt.traction and Group.traction)
                       | (opt.starting_items and Group.starting_items)
                       | (opt.railings and Group.railings)
                       | (opt.fences and Group.fences)
                       | (opt.box_respawning and Group.box_respawning)
                       | (opt.special_boxes and Group.special_box))

    # Create unlock items based on game mode
    match opt.mode:
        case GameMode.option_cups:
            itempool += [create_item("Progressive Cup", player) for _ in range(3)]
        case GameMode.option_courses:
            itempool += [create_item("Progressive Course", player) for _ in range(opt.locked_courses)]

    # Create items based on player options
    cluster_id = 0
    karts = []
    filler_items = []
    trap_items = []
    for name, (_, group, _) in item_table.items():
        if group & item_group_mask:
            itempool.append(create_item(name, player))
            if group == Group.drift:
                if opt.drift == ShuffleDriftAbilities.option_on:
                    itempool.append(create_item(name, player))
                elif opt.drift == ShuffleDriftAbilities.option_plentiful:
                    itempool += [create_item(name, player), create_item(name, player)]
        elif group == Group.item_boxes:
            if world.shuffle_clusters[cluster_id]:
                itempool.append(create_item(name, player))
            cluster_id += 1
        elif group == Group.kart:
            karts.append(name)
        elif group == Group.queueable:
            filler_items.append(name)
        elif group == Group.trap:
            trap_items.append(name)

    # if using Universal Tracker, read from the starting karts we got from slot data
    if world.using_ut:
        for kart in world.starting_karts:
            world.multiworld.push_precollected(create_item(kart, player, ItemClassification.progression))
            karts.remove(kart)
    else:
        for _ in range(1 + opt.two_player):
            kart_index = random.randrange(len(karts))
            world.multiworld.push_precollected(create_item(karts[kart_index], player, ItemClassification.progression))
            world.starting_karts.append(karts.pop(kart_index))
    for kart in karts:
        itempool.append(create_item(kart, player))
    for _ in range(round(num_filler * (100 - opt.trap_percentage) * 0.01)):
        itempool.append(create_item(random.choice(filler_items), player))
    for _ in range(round(num_filler * opt.trap_percentage * 0.01)):
        itempool.append(create_item(random.choice(trap_items), player))

    # Create and place Victory item event
    if opt.goal == Goal.option_all_wins:
        for event in cup_events:
            world.get_location(event).place_locked_item(
                MK64Item(event, ItemClassification.progression_skip_balancing, None, player))
    world.victory_location.place_locked_item(
        MK64Item("Victory", ItemClassification.progression_skip_balancing, None, player))


# Item data table
# 4660000 - 4660212
# Item:                                         (item id, Group, ItemClassification),
item_table = {
    "Progressive Cup":                          (466000_0, Group.special, ItemClassification.progression),
    "Progressive Course":                       (466000_1, Group.special, ItemClassification.progression),
    "Banana Power":                             (466000_2, Group.base, ItemClassification.useful),
    "Banana Bunch Power":                       (466000_3, Group.base, ItemClassification.useful),
    "Green Shell Power":                        (466000_4, Group.base, ItemClassification.useful),
    "Triple Green Shell Power":                 (466000_5, Group.base, ItemClassification.useful),
    "Red Shell Power":                          (466000_6, Group.base, ItemClassification.progression),
    "Triple Red Shell Power":                   (466000_7, Group.base, ItemClassification.progression),
    "Blue Shell Power":                         (466000_8, Group.base, ItemClassification.progression),
    "Lightning Power":                          (466000_9, Group.base, ItemClassification.progression),
    "Fake Item Box Power":                      (46600_10, Group.base, ItemClassification.progression),
    "Star Power":                               (46600_11, Group.base, ItemClassification.progression),
    "Ghost Power":                              (46600_12, Group.base, ItemClassification.useful),
    "Mushroom Power":                           (46600_13, Group.base, ItemClassification.progression),
    "Triple Mushroom Power":                    (46600_14, Group.base, ItemClassification.progression),
    "Super Mushroom Power":                     (46600_15, Group.base, ItemClassification.progression),
    "Feather Power":                            (46600_16, Group.feather, ItemClassification.progression),
    "P2 Banana Power":                          (46600_17, Group.two_player, ItemClassification.useful),
    "P2 Banana Bunch Power":                    (46600_18, Group.two_player, ItemClassification.useful),
    "P2 Green Shell Power":                     (46600_19, Group.two_player, ItemClassification.useful),
    "P2 Triple Green Shell Power":              (46600_20, Group.two_player, ItemClassification.useful),
    "P2 Red Shell Power":                       (46600_21, Group.two_player, ItemClassification.progression),
    "P2 Triple Red Shell Power":                (46600_22, Group.two_player, ItemClassification.progression),
    "P2 Blue Shell Power":                      (46600_23, Group.two_player, ItemClassification.progression),
    "P2 Lightning Power":                       (46600_24, Group.two_player, ItemClassification.progression),
    "P2 Fake Item Box Power":                   (46600_25, Group.two_player, ItemClassification.progression),
    "P2 Star Power":                            (46600_26, Group.two_player, ItemClassification.progression),
    "P2 Ghost Power":                           (46600_27, Group.two_player, ItemClassification.useful),
    "P2 Mushroom Power":                        (46600_28, Group.two_player, ItemClassification.progression),
    "P2 Triple Mushroom Power":                 (46600_29, Group.two_player, ItemClassification.progression),
    "P2 Super Mushroom Power":                  (46600_30, Group.two_player, ItemClassification.progression),
    "P2 Feather Power":                         (46600_31, Group.two_player_feather, ItemClassification.progression),
    "Mario":                                    (46600_32, Group.kart, ItemClassification.progression),
    "Luigi":                                    (46600_33, Group.kart, ItemClassification.progression),
    "Peach":                                    (46600_34, Group.kart, ItemClassification.progression),
    "Toad":                                     (46600_35, Group.kart, ItemClassification.progression),
    "Yoshi":                                    (46600_36, Group.kart, ItemClassification.progression),
    "D.K.":                                     (46600_37, Group.kart, ItemClassification.progression),
    "Wario":                                    (46600_38, Group.kart, ItemClassification.progression),
    "Bowser":                                   (46600_39, Group.kart, ItemClassification.progression),
    "Progressive Drift Mario":                  (46600_41, Group.drift, ItemClassification.progression),
    "Progressive Drift Luigi":                  (46600_42, Group.drift, ItemClassification.progression),
    "Progressive Drift Peach":                  (46600_43, Group.drift, ItemClassification.progression),
    "Progressive Drift Toad":                   (46600_44, Group.drift, ItemClassification.progression),
    "Progressive Drift Yoshi":                  (46600_45, Group.drift, ItemClassification.progression),
    "Progressive Drift D.K.":                   (46600_46, Group.drift, ItemClassification.progression),
    "Progressive Drift Wario":                  (46600_47, Group.drift, ItemClassification.progression),
    "Progressive Drift Bowser":                 (46600_48, Group.drift, ItemClassification.progression),
    "Off-Road Tires Mario":                     (46600_50, Group.traction, ItemClassification.progression),
    "Off-Road Tires Luigi":                     (46600_51, Group.traction, ItemClassification.progression),
    "Off-Road Tires Peach":                     (46600_52, Group.traction, ItemClassification.progression),
    "Off-Road Tires Toad":                      (46600_53, Group.traction, ItemClassification.progression),
    "Off-Road Tires Yoshi":                     (46600_54, Group.traction, ItemClassification.progression),
    "Off-Road Tires D.K.":                      (46600_55, Group.traction, ItemClassification.progression),
    "Off-Road Tires Wario":                     (46600_56, Group.traction, ItemClassification.progression),
    "Off-Road Tires Bowser":                    (46600_57, Group.traction, ItemClassification.progression),
    "Winter Tires Mario":                       (46600_59, Group.traction, ItemClassification.progression),
    "Winter Tires Luigi":                       (46600_60, Group.traction, ItemClassification.progression),
    "Winter Tires Peach":                       (46600_61, Group.traction, ItemClassification.progression),
    "Winter Tires Toad":                        (46600_62, Group.traction, ItemClassification.progression),
    "Winter Tires Yoshi":                       (46600_63, Group.traction, ItemClassification.progression),
    "Winter Tires D.K.":                        (46600_64, Group.traction, ItemClassification.progression),
    "Winter Tires Wario":                       (46600_65, Group.traction, ItemClassification.progression),
    "Winter Tires Bowser":                      (46600_66, Group.traction, ItemClassification.progression),
    "Starting Item Mario":                      (46600_68, Group.starting_items, ItemClassification.useful),
    "Starting Item Luigi":                      (46600_69, Group.starting_items, ItemClassification.useful),
    "Starting Item Peach":                      (46600_70, Group.starting_items, ItemClassification.useful),
    "Starting Item Toad":                       (46600_71, Group.starting_items, ItemClassification.useful),
    "Starting Item Yoshi":                      (46600_72, Group.starting_items, ItemClassification.useful),
    "Starting Item D.K.":                       (46600_73, Group.starting_items, ItemClassification.useful),
    "Starting Item Wario":                      (46600_74, Group.starting_items, ItemClassification.useful),
    "Starting Item Bowser":                     (46600_75, Group.starting_items, ItemClassification.useful),
    "Railings - Choco Mountain":                (46600_77, Group.railings, ItemClassification.useful),
    "Railings - Royal Raceway":                 (46600_78, Group.railings, ItemClassification.useful),
    "Railings - Bowser's Castle":               (46600_79, Group.railings, ItemClassification.useful),
    "Railings - D.K.'s Jungle Parkway":         (46600_80, Group.railings, ItemClassification.progression),
    "Railings - Yoshi Valley Main Track":       (46600_81, Group.railings, ItemClassification.progression),
    "Railings - Yoshi Valley Maze":             (46600_82, Group.railings, ItemClassification.progression),
    "Railings - Banshee Boardwalk North":       (46600_83, Group.railings, ItemClassification.progression),
    "Railings - Banshee Boardwalk South":       (46600_84, Group.railings, ItemClassification.progression),
    "Railings - Rainbow Road 1":                (46600_85, Group.railings, ItemClassification.progression),
    "Railings - Rainbow Road 2":                (46600_86, Group.railings, ItemClassification.progression),
    "Railings - Rainbow Road 3":                (46600_87, Group.railings, ItemClassification.progression),
    "Railings - Rainbow Road 4":                (46600_88, Group.railings, ItemClassification.useful),
    "Railings - Rainbow Road 5":                (46600_89, Group.railings, ItemClassification.progression),
    "Yellow Switch":                            (46600_90, Group.fences, ItemClassification.progression),
    "Red Switch":                               (46600_91, Group.fences, ItemClassification.progression),
    "Green Switch":                             (46600_92, Group.fences, ItemClassification.progression),
    "Blue Switch":                              (46600_93, Group.fences, ItemClassification.progression),
    "Item Box Respawning":                      (46600_94, Group.box_respawning, ItemClassification.useful),
    "Luigi Raceway Special Item Box":           (46600_95, Group.special_box, ItemClassification.filler),
    "Koopa Troopa Beach Special Item Box":      (46600_96, Group.special_box, ItemClassification.filler),
    "Luigi Raceway Item Boxes 1":               (46600_97, Group.item_boxes, ItemClassification.filler),
    "Luigi Raceway Item Boxes 2":               (46600_98, Group.item_boxes, ItemClassification.filler),
    "Luigi Raceway Item Boxes 3":               (46600_99, Group.item_boxes, ItemClassification.filler),
    "Moo Moo Farm Item Boxes 1":                (4660_100, Group.item_boxes, ItemClassification.filler),
    "Moo Moo Farm Item Boxes 2":                (4660_101, Group.item_boxes, ItemClassification.filler),
    "Moo Moo Farm Item Boxes 3":                (4660_102, Group.item_boxes, ItemClassification.filler),
    "Moo Moo Farm Item Boxes 4":                (4660_103, Group.item_boxes, ItemClassification.filler),
    "Koopa Troopa Beach Item Boxes 1":          (4660_104, Group.item_boxes, ItemClassification.filler),
    "Koopa Troopa Beach Item Boxes 2":          (4660_105, Group.item_boxes, ItemClassification.filler),
    "Koopa Troopa Beach Item Boxes 3":          (4660_106, Group.item_boxes, ItemClassification.filler),
    "Koopa Troopa Beach Item Boxes 4":          (4660_107, Group.item_boxes, ItemClassification.filler),
    "Koopa Troopa Beach Item Boxes 5":          (4660_108, Group.item_boxes, ItemClassification.filler),
    "Koopa Troopa Beach Item Boxes 6":          (4660_109, Group.item_boxes, ItemClassification.filler),
    "Kalimari Desert Item Boxes 1":             (4660_110, Group.item_boxes, ItemClassification.filler),
    "Kalimari Desert Item Boxes 2":             (4660_111, Group.item_boxes, ItemClassification.filler),
    "Kalimari Desert Item Boxes 3":             (4660_112, Group.item_boxes, ItemClassification.filler),
    "Toad's Turnpike Item Boxes 1":             (4660_113, Group.item_boxes, ItemClassification.filler),
    "Toad's Turnpike Item Boxes 2":             (4660_114, Group.item_boxes, ItemClassification.filler),
    "Toad's Turnpike Item Boxes 3":             (4660_115, Group.item_boxes, ItemClassification.filler),
    "Toad's Turnpike Item Boxes 4":             (4660_116, Group.item_boxes, ItemClassification.filler),
    "Frappe Snowland Item Boxes 1":             (4660_117, Group.item_boxes, ItemClassification.filler),
    "Frappe Snowland Item Boxes 2":             (4660_118, Group.item_boxes, ItemClassification.filler),
    "Frappe Snowland Item Boxes 3":             (4660_119, Group.item_boxes, ItemClassification.filler),
    "Choco Mountain Item Boxes 1":              (4660_120, Group.item_boxes, ItemClassification.filler),
    "Choco Mountain Item Boxes 2":              (4660_121, Group.item_boxes, ItemClassification.filler),
    "Choco Mountain Item Boxes 3":              (4660_122, Group.item_boxes, ItemClassification.filler),
    "Mario Raceway Item Boxes 1":               (4660_123, Group.item_boxes, ItemClassification.filler),
    "Mario Raceway Item Boxes 2":               (4660_124, Group.item_boxes, ItemClassification.filler),
    "Mario Raceway Item Boxes 3":               (4660_125, Group.item_boxes, ItemClassification.filler),
    "Wario Stadium Item Boxes 1":               (4660_126, Group.item_boxes, ItemClassification.filler),
    "Wario Stadium Item Boxes 2":               (4660_127, Group.item_boxes, ItemClassification.filler),
    "Wario Stadium Item Boxes 3":               (4660_128, Group.item_boxes, ItemClassification.filler),
    "Wario Stadium Item Boxes 4":               (4660_129, Group.item_boxes, ItemClassification.filler),
    "Wario Stadium Item Boxes 5":               (4660_130, Group.item_boxes, ItemClassification.filler),
    "Wario Stadium Item Boxes 6":               (4660_131, Group.item_boxes, ItemClassification.filler),
    "Sherbet Land Item Boxes 1":                (4660_132, Group.item_boxes, ItemClassification.filler),
    "Sherbet Land Item Boxes 2":                (4660_133, Group.item_boxes, ItemClassification.filler),
    "Sherbet Land Bypass Item Box":             (4660_134, Group.item_boxes, ItemClassification.filler),
    "Sherbet Land Item Boxes 3":                (4660_135, Group.item_boxes, ItemClassification.filler),
    "Sherbet Land Item Boxes 4":                (4660_136, Group.item_boxes, ItemClassification.filler),
    "Royal Raceway Item Boxes 1":               (4660_137, Group.item_boxes, ItemClassification.filler),
    "Royal Raceway Item Boxes 2":               (4660_138, Group.item_boxes, ItemClassification.filler),
    "Royal Raceway Item Boxes 3":               (4660_139, Group.item_boxes, ItemClassification.filler),
    "Royal Raceway Item Boxes 4":               (4660_140, Group.item_boxes, ItemClassification.filler),
    "Bowser's Castle Item Boxes 1":             (4660_141, Group.item_boxes, ItemClassification.filler),
    "Bowser's Castle Item Boxes 2":             (4660_142, Group.item_boxes, ItemClassification.filler),
    "Bowser's Castle Item Boxes 3":             (4660_143, Group.item_boxes, ItemClassification.filler),
    "D.K.'s Jungle Parkway Item Boxes 1":       (4660_144, Group.item_boxes, ItemClassification.filler),
    "D.K.'s Jungle Parkway Item Boxes 2":       (4660_145, Group.item_boxes, ItemClassification.filler),
    "D.K.'s Jungle Parkway Item Boxes 3":       (4660_146, Group.item_boxes, ItemClassification.filler),
    "D.K.'s Jungle Parkway Item Boxes 4":       (4660_147, Group.item_boxes, ItemClassification.filler),
    "D.K.'s Jungle Parkway Item Boxes 5":       (4660_148, Group.item_boxes, ItemClassification.filler),
    "Yoshi Valley Field Item Boxes":            (4660_149, Group.item_boxes, ItemClassification.filler),
    "Yoshi Valley Maze Entry Item Boxes":       (4660_150, Group.item_boxes, ItemClassification.filler),
    "Yoshi Valley Maze Bridge Item Boxes":      (4660_151, Group.item_boxes, ItemClassification.filler),
    "Yoshi Valley Maze Rightmost Item Boxes":   (4660_152, Group.item_boxes, ItemClassification.filler),
    "Yoshi Valley Maze Left Fork Item Boxes":   (4660_153, Group.item_boxes, ItemClassification.filler),
    "Yoshi Valley Maze Left Ledge Item Boxes":  (4660_154, Group.item_boxes, ItemClassification.filler),
    "Yoshi Valley Hairpin Turn Item Boxes":     (4660_155, Group.item_boxes, ItemClassification.filler),
    "Yoshi Valley Giant Egg Item Boxes":        (4660_156, Group.item_boxes, ItemClassification.filler),
    "Banshee Boardwalk Item Boxes 1":           (4660_157, Group.item_boxes, ItemClassification.filler),
    "Banshee Boardwalk Item Boxes 2":           (4660_158, Group.item_boxes, ItemClassification.filler),
    "Banshee Boardwalk Item Boxes 3":           (4660_159, Group.item_boxes, ItemClassification.filler),
    "Banshee Boardwalk Item Boxes 4":           (4660_160, Group.item_boxes, ItemClassification.filler),
    "Rainbow Road Item Boxes 1":                (4660_161, Group.item_boxes, ItemClassification.filler),
    "Rainbow Road Item Boxes 2":                (4660_162, Group.item_boxes, ItemClassification.filler),
    "Rainbow Road Item Boxes 3":                (4660_163, Group.item_boxes, ItemClassification.filler),
    "Rainbow Road Item Boxes 4":                (4660_164, Group.item_boxes, ItemClassification.filler),
    "Rainbow Road Item Boxes 5":                (4660_165, Group.item_boxes, ItemClassification.filler),
    "Rainbow Road Item Boxes 6":                (4660_166, Group.item_boxes, ItemClassification.filler),
    "Rainbow Road Item Boxes 7":                (4660_167, Group.item_boxes, ItemClassification.filler),
    "Rainbow Road Item Boxes 8":                (4660_168, Group.item_boxes, ItemClassification.filler),
    "Item Roulette":                            (4660_212, Group.queueable, ItemClassification.filler),
    "Banana Trap":                              (4660_213, Group.trap, ItemClassification.trap),
    "Green Shell Trap":                         (4660_214, Group.trap, ItemClassification.trap),
    "Bomb Trap":                                (4660_215, Group.trap, ItemClassification.trap),
    "Lightning Trap":                           (4660_216, Group.trap, ItemClassification.trap),
    "Lakitu Trap":                              (4660_217, Group.trap, ItemClassification.trap),
}

item_name_to_id = {name: code for name, (code, *_) in item_table.items()}

item_name_groups = {
    "Karts": [
        "Mario",
        "Luigi",
        "Peach",
        "Toad",
        "Yoshi",
        "D.K.",
        "Wario",
        "Bowser"
    ],
    "Switches": [
        "Yellow Switch",
        "Red Switch",
        "Green Switch",
        "Blue Switch"
    ],
}
