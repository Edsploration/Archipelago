from typing import TYPE_CHECKING
from BaseClasses import CollectionState
from worlds.generic.Rules import add_rule, set_rule

from .Locations import course_locations, Group, shared_hazard_locations, cup_locations, cup_events
from .Options import Opt, GameMode, Goal, CupTrophyLocations
from .Items import item_name_groups

if TYPE_CHECKING:
    from . import MK64World

karts = item_name_groups["Karts"]
qualify_item_score_values = {
    "Triple Red Shell Power": 1,
    "Blue Shell Power":       0.5,
    "Lightning Power":        1,
    "Star Power":             1,
    "Mushroom Power":         0.5,
    "Triple Mushroom Power":  1,
    "Super Mushroom Power":   1
}
win_item_score_values = {
    "Red Shell Power":        0.5,
    "Triple Red Shell Power": 1,
    "Blue Shell Power":       0.5,
    "Lightning Power":        0.5,
    "Star Power":             0.5,
    "Mushroom Power":         0.5,
    "Triple Mushroom Power":  1,
    "Super Mushroom Power":   0.5
}


def item_qualify_score(state: CollectionState, player: int) -> int:  # 0 to 6
    thing1 = [rating if state.has(item, player) else 0 for item, rating in qualify_item_score_values.items()]
    thing2 = [rating if state.has("P2 " + item, player) else 0 for item, rating in qualify_item_score_values.items()]
    sum1 = sum(thing1)
    sum2 = sum(thing2)
    maxsum = max(sum1, sum2)
    return maxsum


def item_win_score(state: CollectionState, player: int) -> int:  # 0 to 5
    return max(sum([rating for item, rating in win_item_score_values.items() if state.has(item, player)]),
               sum([rating for item, rating in win_item_score_values.items() if state.has("P2 " + item, player)]))


def track_score(state: CollectionState, player: int) -> int:  # 0 to 2
    ratings = [min(state.count("Progressive Drift " + kart, player), 2) for kart in karts if state.has(kart, player)]
    return max(ratings, default=0)


def off_road_score(state: CollectionState, player: int) -> int:  # 0 to 3
    ratings = [min(state.count("Progressive Drift " + kart, player), 2) + state.has("Off-Road Tires " + kart, player)
               for kart in karts if state.has(kart, player)]
    return max(ratings, default=0)


def winter_score(state: CollectionState, player: int) -> int:  # 0 to 4
    ratings = [min(state.count("Progressive Drift " + kart, player), 2)
               + (state.has("Winter Tires " + kart, player) and 2) or (state.has("Off-Road Tires " + kart, player))
               for kart in karts if state.has(kart, player)]
    return max(ratings, default=0)


def fence_score(state: CollectionState, player: int) -> int:  # 0 to 8  # TODO: Check for feather item boxes on course
    switch_ratings = [0, 4, 6, 7, 8]
    feather_ratings = [2, 1, 0, 0, 0]
    switch_count = state.count_group("Switches", player)
    return (switch_ratings[switch_count]
            + (state.has_any({"Feather Power", "P2 Feather Power"}, player) and feather_ratings[switch_count]))


def score_track_qualify(state: CollectionState, player: int) -> int:  # 0 to 16
    return fence_score(state, player) + track_score(state, player) + item_qualify_score(state, player)


def score_off_road_qualify(state: CollectionState, player: int) -> int:  # 0 to 17
    return fence_score(state, player) + off_road_score(state, player) + item_qualify_score(state, player)


def score_winter_qualify(state: CollectionState, player: int) -> int:  # 0 to 18
    return fence_score(state, player) + winter_score(state, player) + item_qualify_score(state, player)


def score_track_win(state: CollectionState, player: int) -> int:  # 0 to 15
    return fence_score(state, player) + track_score(state, player) + item_win_score(state, player)


def score_off_road_win(state: CollectionState, player: int) -> int:  # 0 to 16
    return fence_score(state, player) + off_road_score(state, player) + item_win_score(state, player)


def score_winter_win(state: CollectionState, player: int) -> int:  # 0 to 17
    return fence_score(state, player) + winter_score(state, player) + item_win_score(state, player)


course_qualify_rules = [    # TODO: Refactor with coupling among score types after more play testing & timing
    # lambda:           score threshhold <= fence_score + terrain score + item power score + optional railings score
    lambda state, player, ease: True,                                                            # Luigi Raceway
    lambda state, player, ease: ease - 1 <= score_track_qualify(state, player),                  # Moo Moo Farm
    lambda state, player, ease: ease + 3 <= score_track_qualify(state, player),                  # Koopa Troopa Beach
    lambda state, player, ease: (ease - 1 <= score_off_road_qualify(state, player))              # Kalimari Desert
                                or (state.has("Yellow Switch", player)
                                    and state.has_any({"Star Power", "P2 Star Power"}, player)),
    lambda state, player, ease: ease - 1 <= score_track_qualify(state, player),                  # Toad's Turnpike
    lambda state, player, ease: ease + 4 <= score_winter_qualify(state, player),                 # Frappe Snowland
    lambda state, player, ease: ease + 0 <= score_off_road_qualify(state, player),               # Choco Mountain
    lambda state, player, ease: ease + 0 <= score_off_road_qualify(state, player),               # Mario Raceway
    lambda state, player, ease: ease + 2 <= score_off_road_qualify(state, player),               # Wario Stadium
    lambda state, player, ease: ease + 2 <= score_winter_qualify(state, player),                 # Sherbet Land
    lambda state, player, ease: ease + 3 <= score_off_road_qualify(state, player),               # Royal Raceway
    lambda state, player, ease: ease + 3 <= score_off_road_qualify(state, player),               # Bowser's Castle
    lambda state, player, ease: ease + 2 <= (score_off_road_qualify(state, player)               # D.K.'s Jungle Parkway
                                             + state.has("Railings D.K.'s Jungle Parkway", player)),
    lambda state, player, ease: ease + 5 <= (score_off_road_qualify(state, player)               # Yoshi Valley
                                             + state.has("Railings Yoshi Valley Main Track", player)
                                             + state.has("Railings Yoshi Valley Maze", player)),
    lambda state, player, ease: ease + 3 <= (score_track_qualify(state, player)                  # Banshee Boardwalk
                                             + state.has("Railings Banshee Boardwalk North", player)
                                             + state.has("Railings Banshee Boardwalk North", player)),
    lambda state, player, ease: ease + 4 <= (score_track_qualify(state, player)                  # Rainbow Road
                                             + 2 * state.has("Railings Rainbow Road 1", player)
                                             + 2 * state.has("Railings Rainbow Road 2", player)
                                             + 2 * state.has("Railings Rainbow Road 3", player)
                                             + state.has("Railings Rainbow Road 5", player))
]

course_win_rules = [    # TODO: Refactor with coupling among score types after more play testing & timing
    # lambda:           score threshhold <= fence_score + terrain score + item power score + optional railings score
    lambda state, player, ease: True,                                                            # Luigi Raceway
    lambda state, player, ease: ease + 1 <= score_track_win(state, player),                      # Moo Moo Farm
    lambda state, player, ease: ease + 5 <= score_track_win(state, player),                      # Koopa Troopa Beach
    lambda state, player, ease: (ease + 1 <= score_off_road_win(state, player))                  # Kalimari Desert
                                or (state.has("Yellow Switch", player)
                                    and state.has_any({"Star Power", "P2 Star Power"}, player)),
    lambda state, player, ease: ease + 1 <= score_track_win(state, player),                      # Toad's Turnpike
    lambda state, player, ease: ease + 6 <= score_winter_win(state, player),                     # Frappe Snowland
    lambda state, player, ease: ease + 3 <= score_off_road_win(state, player),                   # Choco Mountain
    lambda state, player, ease: ease + 3 <= score_off_road_win(state, player),                   # Mario Raceway
    lambda state, player, ease: ease + 4 <= score_off_road_win(state, player),                   # Wario Stadium
    lambda state, player, ease: ease + 4 <= score_winter_win(state, player),                     # Sherbet Land
    lambda state, player, ease: ease + 5 <= score_off_road_win(state, player),                   # Royal Raceway
    lambda state, player, ease: ease + 5 <= score_off_road_win(state, player),                   # Bowser's Castle
    lambda state, player, ease: ease + 4 <= (score_off_road_win(state, player)                   # D.K.'s Jungle Parkway
                                             + state.has("Railings D.K.'s Jungle Parkway", player)),
    lambda state, player, ease: ease + 7 <= (score_off_road_win(state, player)                   # Yoshi Valley
                                             + state.has("Railings Yoshi Valley Main Track", player)
                                             + state.has("Railings Yoshi Valley Maze", player)),
    lambda state, player, ease: ease + 5 <= (score_track_win(state, player)                      # Banshee Boardwalk
                                             + state.has("Railings Banshee Boardwalk North", player)
                                             + state.has("Railings Banshee Boardwalk North", player)),
    lambda state, player, ease: ease + 6 <= (score_track_win(state, player)                      # Rainbow Road
                                             + 2 * state.has("Railings Rainbow Road 1", player)
                                             + 2 * state.has("Railings Rainbow Road 2", player)
                                             + 2 * state.has("Railings Rainbow Road 3", player)
                                             + state.has("Railings Rainbow Road 5", player))
]


def can_win_trophy(state: CollectionState, player: int, courses: frozenset[int], trophy_class: int, ease: int) -> bool:
    return trophy_class <= sum(course_win_rules[course](state, player, ease) for course in courses)


def set_star_access_rule(world: "MK64World", loc_name: str, player: int, opt: Opt) -> None:
    if opt.two_player:
        set_rule(world.get_location(loc_name),
                 lambda state: state.has_any({"Star Power", "P2 Star Power"}, player))
    else:
        set_rule(world.get_location(loc_name), lambda state: state.has("Star Power", player))


def create_rules(world: "MK64World") -> None:
    multiworld = world.multiworld
    player = world.player
    opt = world.opt
    order = world.course_order

    # Make starting kart(s) required, which has them show up in the spoiler log Playthrough.
    if opt.mode == GameMode.option_cups:
        first_entrance = world.multiworld.get_region("Menu", player).get_exits()[0]
        if len(world.starting_karts) == 1:
            first_entrance.access_rule = lambda state, kart=world.starting_karts[0]: state.has(kart, player)
        else:
            first_entrance.access_rule = lambda state, kts=frozenset(world.starting_karts): state.has_all(kts, player)

    # Region (Entrance) Rules (handled in Regions.py instead for now)
    # if opt_game_mode == GameMode.option_cups:
    #    set_rule(multiworld.get_entrance("Flower Cup 1", player),
    #             lambda state: state.has("Progressive Cup Unlock", player, 1))
    #     set_rule(multiworld.get_entrance("Star Cup 1", player),
    #              lambda state: state.has("Progressive Cup Unlock", player, 2))
    #     set_rule(multiworld.get_entrance("Special Cup 1", player),
    #              lambda state: state.has("Progressive Cup Unlock", player, 3))
    # elif opt_game_mode == GameMode.option_courses:
    #     pass

    # Base Course Rules # TODO: Clean this up, probably combine with Star Access Rules section
    for locations in course_locations.values():
        for name, (code, group) in locations.items():
            if group == Group.base:
                if code % 3 < 2:
                    set_rule(world.get_location(name),
                             lambda state: course_win_rules[(code - 4660000) // 3](state, player, opt.logic))
                else:
                    set_rule(world.get_location(name),
                             lambda state: course_qualify_rules[(code - 4660000) // 3](state, player, opt.logic))

    # Item Spot Access Rules moved to Regions.py for context that knows which item box spots to apply rules to

    # Koopa Troopa Beach Rock Access
    if opt.special_boxes:
        set_rule(world.get_location("Koopa Troopa Beach Rock"),
                 lambda state: state.has_all({"Yellow Switch", "Blue Switch"}, player)
                               or state.has_all({"Red Switch", "Green Switch"}, player))

    if opt.secrets:
        # Kalimari Desert Secret Access
        set_rule(world.get_location("Kalimari Desert Secret"),
                 lambda state: state.has_any({"Yellow Switch", "Red Switch", "Blue Switch",
                                              "Feather Power", "P2 Feather Power"}, player))

        # Marty's Secret Access
        set_rule(world.get_location("Marty's Secret"),
                 lambda state: state.has_any({"Green Switch", "Feather Power", "P2 Feather Power"}, player))

    # Hazard Access, all use Star Power
    if opt.hazards:
        for locations in course_locations.values():
            for name, (_, group) in locations.items():
                if group == Group.hazard:
                    set_star_access_rule(world, name, player, opt)
        for name, _ in shared_hazard_locations.items():
            set_star_access_rule(world, name, player, opt)

        # Add Blue Fence rule to Mario sign
        add_rule(world.get_location("Destroy Mario Sign"), lambda state: state.has("Blue Switch", player))

    # Cup Trophy Rules
    cup_courses = [frozenset(order[i:i + 4]) for i in range(0, len(order), 4)]
    if opt.mode == GameMode.option_cups:
        trophy_class_mapping = {"Bronze": 1, "Silver": 2, "Gold": 3}
        engine_class_mapping = {"100cc": 2, "150cc": 3}  # 50cc is 0
        for locations, courses in zip(cup_locations.values(), cup_courses):
            for loc_name, _, option_filter in locations:
                if option_filter & opt.trophies:
                    difficulty, trophy = loc_name.rsplit(" ", 2)[-2:]
                    trophy_class = trophy_class_mapping[trophy]
                    ease = opt.logic + engine_class_mapping.get(difficulty, 0)
                    set_rule(world.get_location(loc_name),
                             lambda state, o=courses, t=trophy_class, e=ease: can_win_trophy(state, player, o, t, e))

        # Event & Victory Rules
        if opt.goal == Goal.option_all_wins:
            for cup_event, courses in zip(cup_events, cup_courses):
                ease = opt.logic + (0 if opt.trophies == CupTrophyLocations.option_three else 3)
                set_rule(world.get_location(cup_event),
                         lambda state, o=courses, e=ease: can_win_trophy(state, player, o, 3, e))
            world.victory_location.access_rule = lambda state: state.has_all(cup_events, player)
        multiworld.completion_condition[player] = lambda state: state.has("Victory", player)
