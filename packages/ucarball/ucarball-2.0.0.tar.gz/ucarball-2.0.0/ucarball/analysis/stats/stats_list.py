from typing import List

from ucarball.analysis.stats.demos.demos import DemoStat
from ucarball.analysis.stats.dribbles.ball_carry import CarryStat
from ucarball.analysis.stats.kickoffs.kickoff_stat import KickoffStat
from ucarball.analysis.stats.possession.per_possession import PerPossessionStat
from ucarball.analysis.stats.ball_forward.distance_hit_ball_forward import DistanceStats
from ucarball.analysis.stats.boost.boost import BoostStat
from ucarball.analysis.stats.controls.controls import ControlsStat
from ucarball.analysis.stats.possession.ball_distances import BallDistanceStat
from ucarball.analysis.stats.possession.possession import PossessionStat
from ucarball.analysis.stats.possession.turnovers import TurnoverStat
from ucarball.analysis.stats.stats import BaseStat, HitStat
from ucarball.analysis.stats.tendencies.averages import Averages
from ucarball.analysis.stats.tendencies.hit_counts import HitCountStat
from ucarball.analysis.stats.tendencies.positional_tendencies import PositionalTendencies
from ucarball.analysis.stats.tendencies.relative_position_tendencies import RelativeTendencies
from ucarball.analysis.stats.tendencies.speed_tendencies import SpeedTendencies
from ucarball.analysis.stats.tendencies.team_tendencies import TeamTendencies
from ucarball.analysis.stats.rumble.rumble import RumbleItemStat
from ucarball.analysis.stats.rumble.goals import PreRumbleGoals, ItemGoals
from ucarball.analysis.stats.dropshot.goals import DropshotGoals
from ucarball.analysis.stats.dropshot.ball_phase_times import DropshotBallPhaseTimes
from ucarball.analysis.stats.dropshot.damage import DropshotStats


class StatsList:
    """
    Where you add any extra stats you want calculated.
    """

    @staticmethod
    def get_player_stats() -> List[BaseStat]:
        """These are stats that end up being assigned to a specific player"""
        return [BoostStat(),
                PositionalTendencies(),
                Averages(),
                BallDistanceStat(),
                ControlsStat(),
                SpeedTendencies(),
                CarryStat(),
                PerPossessionStat(),
                SpeedTendencies(),
                RumbleItemStat(),
                KickoffStat(),
                DropshotStats(),
                DemoStat()
                ]

    @staticmethod
    def get_team_stats() -> List[BaseStat]:
        """These are stats that end up being assigned to a specific team"""
        return [PossessionStat(),
                TeamTendencies(),
                RelativeTendencies(),
                PerPossessionStat(),
                RumbleItemStat(),
                PreRumbleGoals(),
                DropshotStats()
                ]

    @staticmethod
    def get_general_stats() ->List[BaseStat]:
        """These are stats that end up being assigned to the game as a whole"""
        return [PositionalTendencies(),
                SpeedTendencies(),
                ItemGoals(),
                DropshotGoals(),
                DropshotBallPhaseTimes(),
                DropshotStats()
                ]

    @staticmethod
    def get_hit_stats() ->List[HitStat]:
        """These are stats that depend on current hit and next hit"""
        return [DistanceStats(),
                PossessionStat(),
                HitCountStat(),
                TurnoverStat()
                ]
