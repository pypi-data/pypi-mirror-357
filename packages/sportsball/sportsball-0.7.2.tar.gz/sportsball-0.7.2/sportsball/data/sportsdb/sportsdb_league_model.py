"""Sports DB league model."""

# pylint: disable=line-too-long
import datetime
from typing import Iterator

import tqdm
from scrapesession.scrapesession import ScrapeSession  # type: ignore

from ..game_model import GameModel
from ..league import League
from ..league_model import LeagueModel
from ..season_type import SeasonType
from .sportsdb_game_model import create_sportsdb_game_model


class SportsDBLeagueModel(LeagueModel):
    """SportsDB implementation of the league model."""

    # pylint: disable=too-many-arguments

    def __init__(
        self,
        session: ScrapeSession,
        league_id: str,
        league: League,
        position: int | None = None,
    ) -> None:
        super().__init__(league, session, position=position)
        self._league_id = league_id

    @classmethod
    def name(cls) -> str:
        return "sportsdb-league-model"

    def _produce_games(
        self,
        round_str: str,
        week: int,
        league_id: str,
        season_year: str,
        season_type: SeasonType,
        pbar: tqdm.tqdm,
    ) -> Iterator[GameModel]:
        # pylint: disable=line-too-long
        year = int(season_year.split("-")[0])

        def internal_produce_games() -> Iterator[GameModel]:
            response = self.session.get(
                f"https://www.thesportsdb.com/api/v1/json/3/eventsround.php?id={league_id}&r={round_str}&s={season_year}"
            )
            response.raise_for_status()
            games = response.json()
            events = games["events"]
            if events is None:
                return
            for count, game in enumerate(events):
                pbar.update(1)
                game_model = create_sportsdb_game_model(
                    self.session,
                    game,
                    week,
                    count,
                    self.league,
                    year,
                    season_type,
                )
                pbar.set_description(
                    f"SportsDB {season_year} - {season_type} - {game_model.dt}"
                )
                yield game_model

        if year < datetime.datetime.now().year - 1:
            yield from internal_produce_games()
        else:
            with self.session.cache_disabled():
                yield from internal_produce_games()

    @property
    def games(self) -> Iterator[GameModel]:
        with self.session.cache_disabled():
            response = self.session.get(
                f"https://www.thesportsdb.com/api/v1/json/3/search_all_seasons.php?id={self._league_id}"
            )
            response.raise_for_status()
            seasons = response.json()
        with tqdm.tqdm(position=self.position) as pbar:
            for season in seasons["seasons"]:
                season_year = season["strSeason"]
                for season_type in SeasonType:
                    match season_type:
                        case SeasonType.OFFSEASON:
                            yield from self._produce_games(
                                str(0),
                                0,
                                self._league_id,
                                season_year,
                                season_type,
                                pbar,
                            )
                        case SeasonType.PRESEASON:
                            try:
                                yield from self._produce_games(
                                    str(500),
                                    0,
                                    self._league_id,
                                    season_year,
                                    season_type,
                                    pbar,
                                )
                            except ValueError:
                                pass
                        case SeasonType.REGULAR:
                            if self.league != League.NBA:
                                try:
                                    for count, round_str in enumerate(range(1, 125)):
                                        yield from self._produce_games(
                                            str(round_str),
                                            count,
                                            self._league_id,
                                            season_year,
                                            season_type,
                                            pbar,
                                        )
                                except ValueError:
                                    pass
                        case SeasonType.POSTSEASON:
                            for count, round_str in enumerate(
                                [125, 150, 160, 170, 180, 200]
                            ):
                                try:
                                    yield from self._produce_games(
                                        str(round_str),
                                        21 + count,
                                        self._league_id,
                                        season_year,
                                        season_type,
                                        pbar,
                                    )
                                except ValueError:
                                    pass
