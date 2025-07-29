from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Literal, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from coc_api.models import Location, League, Label, ClanCapital, Player

@dataclass
class Clan:
    tag: Optional[str]
    name: Optional[str]
    type: Optional[str]
    description: Optional[str]
    location: 'Location'
    is_family_friendly: Optional[bool]
    icon: Optional[str]
    clan_level: Optional[int]
    clan_points: Optional[int]
    clan_builder_base_points: Optional[int]
    clan_capital_points: Optional[int]
    captical_league: 'League'
    required_trophies: Optional[int]
    war_frequency: Optional[str]
    war_win_streak: Optional[int]
    war_wins: Optional[int]
    war_ties: Optional[int]
    war_losses: Optional[int]
    is_war_log_public: Optional[bool]
    war_league: 'League'
    members: Optional[int]
    member_list: List['Player'] = field(default_factory=list)
    labels: List['Label'] = field(default_factory=list)
    required_builder_base_trophies: Optional[int] = None
    required_townhall_level: Optional[int] = None
    clan_captial: Optional['ClanCapital'] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any], icon_size: Literal["small", "medium", "large"] = "small") -> 'Clan':
        from coc_api.models import Location, League, Label, ClanCapital, Player

        location = Location.from_dict(data.get("location", {}))
        captical_league = League.from_dict(data.get("capitalLeague", {}))
        war_league = League.from_dict(data.get("warLeague", {}))
        clan_captial = ClanCapital.from_dict(data.get("clanCapital", {})) if hasattr(ClanCapital,
                                                                                     'from_dict') else ClanCapital(
            data.get("clanCapital", {}))

        member_list = [Player.from_dict(p) for p in data.get("memberList", [])]
        labels = [Label.from_dict(l) for l in data.get("labels", [])]

        return cls(
            tag=data.get("tag"),
            name=data.get("name"),
            type=data.get("type"),
            description=data.get("description"),
            location=location,
            is_family_friendly=data.get("isFamilyFriendly"),
            icon=data.get("badgeUrls", {}).get(icon_size),
            clan_level=data.get("clanLevel"),
            clan_points=data.get("clanPoints"),
            clan_builder_base_points=data.get("clanBuilderBasePoints"),
            clan_capital_points=data.get("clanCapitalPoints"),
            captical_league=captical_league,
            required_trophies=data.get("requiredTrophies"),
            war_frequency=data.get("warFrequency"),
            war_win_streak=data.get("warWinStreak"),
            war_wins=data.get("warWins"),
            war_ties=data.get("warTies"),
            war_losses=data.get("warLosses"),
            is_war_log_public=data.get("isWarLogPublic"),
            war_league=war_league,
            members=data.get("members"),
            member_list=member_list,
            labels=labels,
            required_builder_base_trophies=data.get("requiredBuilderBaseTrophies"),
            required_townhall_level=data.get("requiredTownhallLevel"),
            clan_captial=clan_captial
        )
