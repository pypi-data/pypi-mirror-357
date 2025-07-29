from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from coc_api.models import (
        Clan, League, Achievement, Troop,
        Hero, Equipment, Spell, Label, ClanCapitalHouse
    )

@dataclass
class Player:
    tag: Optional[str]
    name: Optional[str]
    town_hall_level: Optional[int]
    town_hall_weapon_level: Optional[int]
    exp_level: Optional[int]
    trophies: Optional[int]
    best_trophies: Optional[int]
    war_stars: Optional[int]
    attack_wins: Optional[int]
    defense_wins: Optional[int]
    builder_hall_level: Optional[int]
    builder_trophies: Optional[int]
    builder_best_trophies: Optional[int]
    donations: Optional[int]
    donations_received: Optional[int]
    clan_capital_contributions: Optional[int]
    clan: Optional["Clan"]
    league: "League"
    builder_league: "League"
    achievements: List["Achievement"] = field(default_factory=list)
    player_house: List["ClanCapitalHouse"] = field(default_factory=list)
    labels: List["Label"] = field(default_factory=list)
    troops: List["Troop"] = field(default_factory=list)
    heroes: List["Hero"] = field(default_factory=list)
    hero_equipment: List["Equipment"] = field(default_factory=list)
    spells: List["Spell"] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Player:
        from coc_api.models import (
            Clan, League, Achievement, Troop, Hero,
            Equipment, Spell, Label, ClanCapitalHouse
        )

        clan_data = data.get("clan")
        clan = Clan.from_dict(clan_data) if clan_data else None
        achievements = [Achievement.from_dict(a) for a in data.get("achievements", [])]
        labels = [Label.from_dict(l) for l in data.get("labels", [])]
        troops = [Troop.from_dict(t) for t in data.get("troops", [])]
        heroes = [Hero.from_dict(h) for h in data.get("heroes", [])]
        hero_equipment = [Equipment.from_dict(e) for e in data.get("heroEquipment", [])]
        spells = [Spell.from_dict(s) for s in data.get("spells", [])]
        player_house = [ClanCapitalHouse.from_dict(c) for c in data.get("playerHouse", {}).get("elements", [])]

        return cls(
            tag=data.get("tag"),
            name=data.get("name"),
            town_hall_level=data.get("townHallLevel"),
            town_hall_weapon_level=data.get("townHallWeaponLevel"),
            exp_level=data.get("expLevel"),
            trophies=data.get("trophies"),
            best_trophies=data.get("bestTrophies"),
            war_stars=data.get("warStars"),
            attack_wins=data.get("attackWins"),
            defense_wins=data.get("defenseWins"),
            builder_hall_level=data.get("builderHallLevel"),
            builder_trophies=data.get("builderBaseTrophies"),
            builder_best_trophies=data.get("bestBuilderBaseTrophies"),
            donations=data.get("donations"),
            donations_received=data.get("donationsReceived"),
            clan_capital_contributions=data.get("clanCapitalContributions"),
            clan=clan,
            league=League.from_dict(data.get("league", {})),
            builder_league=League.from_dict(data.get("builderBaseLeague", {})),
            achievements=achievements,
            labels=labels,
            troops=troops,
            heroes=heroes,
            hero_equipment=hero_equipment,
            spells=spells,
            player_house=player_house
        )
