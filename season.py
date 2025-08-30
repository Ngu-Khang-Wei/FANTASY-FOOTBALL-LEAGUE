from __future__ import annotations
from data_structures.bset import BSet
from data_structures.referential_array import ArrayR
from dataclasses import dataclass
from team import Team
from typing import Generator
from data_structures.array_sorted_list import ArraySortedList
from data_structures.linked_list import LinkedList
from game_simulator import GameSimulator
from constants import ResultStats, TeamStats, PlayerStats
from customconstants import CustomConstants
from hashy_step_table import HashyStepTable
from player import Player
from data_structures.hash_table import LinearProbeTable

@dataclass
class Game:
    """
    Simple container for a game between two teams.
    Both teams must be team objects, there cannot be a game without two teams.

    Note: Python will automatically generate the init for you.
    Use Game(home_team: Team, away_team: Team) to use this class.
    See: https://docs.python.org/3/library/dataclasses.html
    """
    home_team: Team = None
    away_team: Team = None


class WeekOfGames:
    """
    Simple container for a week of games.

    A fixture must have at least one game.
    """

    def __init__(self, week: int, games: ArrayR[Game]) -> None:
        """
        Container for a week of games.

        Args:
            week (int): The week number.
            games (ArrayR[Game]): The games for this week.
        """
        self.games: ArrayR[Game] = games
        self.week: int = week

    def get_games(self) -> ArrayR:
        """
        Returns the games in a given week.

        Returns:
            ArrayR: The games in a given week.

        Complexity:
        Best Case Complexity: O(1)
        Worst Case Complexity: O(1)
        """
        return self.games

    def get_week(self) -> int:
        """
        Returns the week number.

        Returns:
            int: The week number.

        Complexity:
        Best Case Complexity: O(1)
        Worst Case Complexity: O(1)
        """
        return self.week

    def __iter__(self):
        """
        Complexity:
        Best Case Complexity: O(1)
        Worst Case Complexity: O(1)
        """
        self.next_game_index = 0
        return self

    def __next__(self):
        """
        Complexity:
        Best Case Complexity: O(1)
        Worst Case Complexity: O(1)
        """
        if self.next_game_index >= len(self.games):
            raise StopIteration
        current_game_index = self.next_game_index
        self.next_game_index += 1
        return self.games[current_game_index]


class Season:

    def __init__(self, teams: ArrayR[Team]) -> None: 
        """
        Initializes the season with a schedule.

        Args:
            teams (ArrayR[Team]): The teams played in this season.

        Complexity:
            Best Case Complexity: O(K^2) where K is the number of teams in the season. generate_schedule is O(K^2). Number of game 
                                  weeks and self.leaderboard initilisation are not taken into account as they are dominated by K^2. 
                                  Adding teams in leaderboard takes O(K * log K) when all the team statistics are either None or 0 so 
                                  string comparison is needed for team name comparison. Best case is when each team added is lexicographically 
                                  greater than the previously added team, so they are always added to the back of the leaderboard,
                                  one after another. Only binary search occurs, no shifting. So O(K) for iterating through each team
                                  * O(log K) for binary search for last position. O(K * log K) is still dominated by O(K^2).

            Worst Case Complexity: O(K^2) where K is the number of teams in the season. generate_schedule is O(K^2). Number of game weeks 
                                   and self.leaderboard initilisation are not taken into account as they are dominated by K^2. In the worst 
                                   case, when iterating through K teams (O(K)), each team is lexicographically lesser than the previously added
                                   team, so they are always added to the front of the leaderboard. The last team added to the front of the 
                                   leaderboard will cause all the other teams to be shifted right which is an O(K) operation. So worst complexity 
                                   remains O(K^2). It is also important to note that all the team statistics are either None or 0, so string 
                                   comparison is needed for team name comparison.
        """
        self.teams = teams
        self.length = len(teams)
        
        self.leaderboard = ArraySortedList(len(teams))
        for team in teams: # O(N) where N is the number of teams playing in this season
            self.leaderboard.add(team) 

        self.schedule = LinkedList() # O(1)
        temp_schedule = self._generate_schedule() # O(N^2) where N is the number of teams in the season.
        for week_index, week_of_games in enumerate(temp_schedule): # O(M) where M is the number of game weeks in this season (Always < N)
            self.schedule.append(WeekOfGames(week_index + 1, week_of_games))


    def _generate_schedule(self) -> ArrayR[ArrayR[Game]]:
        """
        Generates a schedule by generating all possible games between the teams.

        Return:
            ArrayR[ArrayR[Game]]: The schedule of the season.
                The outer array is the weeks in the season.
                The inner array is the games for that given week.

        Complexity:
            Best Case Complexity: O(N^2) where N is the number of teams in the season.
            Worst Case Complexity: O(N^2) where N is the number of teams in the season.
        """
        num_teams: int = len(self.teams)
        weekly_games: list[ArrayR[Game]] = []
        flipped_weeks: list[ArrayR[Game]] = []
        games: list[Game] = []

        # Generate all possible matchups (team1 vs team2, team2 vs team1, etc.)
        for i in range(num_teams):
            for j in range(i + 1, num_teams):
                games.append(Game(self.teams[i], self.teams[j]))

        # Allocate games into each week ensuring no team plays more than once in a week
        week: int = 0
        while games:
            current_week: list[Game] = []
            flipped_week: list[Game] = []
            used_teams: BSet = BSet()

            week_game_no: int = 0
            for game in games[:]:  # Iterate over a copy of the list
                if game.home_team.get_number() not in used_teams and game.away_team.get_number() not in used_teams:
                    current_week.append(game)
                    used_teams.add(game.home_team.get_number())
                    used_teams.add(game.away_team.get_number())

                    flipped_week.append(Game(game.away_team, game.home_team))
                    games.remove(game)
                    week_game_no += 1

            weekly_games.append(ArrayR.from_list(current_week))
            flipped_weeks.append(ArrayR.from_list(flipped_week))
            week += 1

        return ArrayR.from_list(weekly_games + flipped_weeks)


    def _get_player_dictionary(self) -> HashyStepTable[str, Player]: 
        """
        Generate a dictionary that maps all the player names in the season to their respective player objects.

        Returns:
            HashyStepTable[str, Player]: A Hashy step table that maps every single player name in this season to
            their respective player objects for easy accessing and updating of values in simulate season.

        Complexity:
            Best Case Complexity: O(M * N + P) where M is the total number of players, N is the length of the longest player name and P
                                  is the size of the player_dict hashy step table. This occurs when every single key is hashed to an unoccupied 
                                  position in the hashy step table when inserting, so no probing is needed since there are no collisions. The 
                                  table size used can greatly outweigh the number of players, so it is included in the analysis.

            Worst Case Complexity: O(M * (N + P)) where M is the total number of players, N is the length of the longest player name and P the 
                                   size of the player_dict hashy step table. This occurs when the keys are hashed to occupied postions (collision)
                                   when inserting and probing is done many times using hashy probe to find the empty slot for the players. In the 
                                   worst case, the table is searched all the way through, contributing to O(P). 
        """      
        hashy_table_sizes = CustomConstants.TABLE_SIZES
        table_start_index = 0
        player_count = 0

        # This whole portion of code is for selecting the table size so that rehash does not happen, leading to better efficiency.
        # The complexity of this portion of code is overshadowed by the later parts.        
        for team in self.teams:
            player_count += len(team)
        player_count *= CustomConstants.LOAD_FACTOR
        for table_size_index in range(len(hashy_table_sizes)): 
            if hashy_table_sizes[table_size_index] > player_count:
                table_start_index = table_size_index
                break

        # Create a hash table for more efficient players retrieval (name as key) for large number of players who score,
        # assist, tackle or intercept in a game.
        player_dict = HashyStepTable(CustomConstants.TABLE_SIZES[table_start_index:])
        for team in self.teams: 
            for player in team.get_unsorted_player_array(): 
                player_dict[player.get_name()] = player
        return player_dict

    def simulate_season(self) -> None:
        """
        Simulates the season.

        Complexity:
            Assume simulate_game is O(1)
            Remember to define your variables and their complexity.  

            Best Case Complexity: O(_get_player_dict + N * (_update_team_statistics + _update_player_statistics) + _sort_leaderboard)
            where N is the total number of games multiplied by the addition of the best time complexity of _update_team_statistics method and 
            the best time complexity of the _update_player_statistics method. Best time complexity of _sort_leaderboard method and best time 
            complexity of _get_player_dict method are added as well. In the best case, 'GOAL SCORERS', 'GOAL ASSISTS', 'INTERCEPTION' AND 'TACKLES' 
            have no entries in all games, which is explained in the complexity analysis of _update_player_statistics. Since we can't tell which is
            the dominating factor between _update_team_statistics and _update_player_statistics, both are added. Although 
            N * (_update_team_statistics + _update_player_statistics) seems to overshadow _sort_leaderboard and _get_player_dict, there is no 
            concrete way of provingit due to the assumptions given, so they are added as well.
            
            Worst Case Complexity: O(_get_player_dict + N * (_update_team_statistics + _update_player_statistics) + _sort_leaderboard) where N is
            the total number of games multiplied by the addition of the worst time complexity of _update_team_statistics method and the best worst
            time complexity of the _update_player_statistics method. Lastly, need to add the worst time complexity of _sort_leaderboard method as 
            well. Since we can't tell which is the dominating factor between _update_team_statistics and _update_player_statistics, both are added. Although 
            N * (_update_team_statistics + _update_player_statistics) seems to overshadow _sort_leaderboard, there is no concrete way of proving
            it due to the assumptions given, so they are added as well.
            
         """
        
        # Create the dictionary first. This might be less efficient if there are less players in the result statistics.
        # However, complexity is evaluated for large value variables (can extend to infinity). In that case, this method is very efficient.
        player_dict = self._get_player_dictionary()
        for game in self.get_next_game(): # Iterating over all possible games
            current_game_result = GameSimulator.simulate(game.home_team, game.away_team) # O(1) based on assumption.
            self._update_team_statistics(game, current_game_result) # Update the team statistics accordingly .
            self._update_player_statistics(player_dict, current_game_result) # Update the player statistics accordingly.

        # Sort the leaderboard at the end after the team statistics have changed.
        self._sort_leaderboard()


    def _update_team_statistics(self, game : Game, result : LinearProbeTable) -> None:
        """
        Updates the team statistics after each game

        Args:
            game (Game): Contains the two competing team objects whose statistics need updating.
            result: The result of the pairing which is used to update the team statistics.

        Complexity:
            Best Case Complexity: O(M * N + O + P + Q) Where M is the number of player positions in a team, N is the length of the longest player 
                                  position key to be hashed, O is the number of players in the larger team between home and away team, P is the 
                                  length of the longest team statistic key and Q is the length of the longest result statistic key. This occurs 
                                  when the keys are always hashed to the correct position, so no further probing is needed to find the team 
                                  statistics and result statistics since there are no collisions.

            Worst Case Complexity: O(M * (N + U) + O + P + Q + V + W) Where M is the number of player positions in a team, N is the length of the 
                                   longest player position key, U is the size of the player positions hash table , O is the total number of players 
                                   in the largest team, P is the length of the longest team statistic key, Q is the length of the longest result 
                                   statistic key, V is the size of the team statistic hash table, W is the size of the result hash table. This 
                                   occurs when the keys are hashed to the wrong position occupied by a different key (collision) and probing is 
                                   done many times using hashy probe to find the correct team statistics and result statistics. In the worst case, 
                                   the tables are searched all the way through, contributing to O(V + W). O(M * (N + U) + O) is basically the worst 
                                   case complexity of the get_players method for a team and is used in this case to update the games played 
                                   statistic of each player.

        """
        # Pretty self explanatory
        if result[ResultStats.HOME_GOALS.value] > result[ResultStats.AWAY_GOALS.value]:
            game.home_team[TeamStats.WINS] += 1 
            game.away_team[TeamStats.LOSSES] += 1 
        elif result[ResultStats.HOME_GOALS.value] < result[ResultStats.AWAY_GOALS.value]:
            game.away_team[TeamStats.WINS] += 1
            game.home_team[TeamStats.LOSSES] += 1
        else:
            game.home_team[TeamStats.DRAWS] += 1
            game.away_team[TeamStats.DRAWS] += 1

        game.home_team[TeamStats.GOALS_FOR] += result[ResultStats.HOME_GOALS.value]
        game.away_team[TeamStats.GOALS_AGAINST] += result[ResultStats.HOME_GOALS.value]

        game.home_team[TeamStats.GOALS_AGAINST] += result[ResultStats.AWAY_GOALS.value]
        game.away_team[TeamStats.GOALS_FOR] += result[ResultStats.AWAY_GOALS.value]


    def _update_player_statistics(self, player_dict : HashyStepTable, result : LinearProbeTable) -> None:
        """
        Updates the player statistics after each game

        Args:
            player_dict (HashyStepTable): Contains all the player names mapped to their respective player objects for more efficient access.
            result: The result of the a game which is used to update the player statistics.

        Complexity:
            Best Case Complexity: O(N) where N is the length of the longest result statistic key to be hased. This occurs when the keys are 
                                  always hashed to the correct position, so no further probing is needed to find the result statistics, since 
                                  there is are no collisions. O(N) only in the case where there are no goal scorers, goal assists, interceptions 
                                  nor tackles, so there are no players whose statistics need changing.

            Worst Case Complexity: O(M * (N + P) + Q + R) Where M is the total number of players, N is the length of the longest player name, P 
                                   is the size of player_dict hashy step table , Q is the length of the longest result statistic key and R is the 
                                   size of the result hash table. This occurs when the keys are hashed to the wrong position occupied by a 
                                   different key (collision) and probing is done many times using hashy probe to find the correct player objects 
                                   and result statistics. In the worst case, the tables are searched all the way through, contributing to O(P) and 
                                   O(R).         
        """

        # Pretty self explanatory
        goal_scorers = result[ResultStats.GOAL_SCORERS.value]
        if goal_scorers:
            for player_name in goal_scorers: 
                player_dict[player_name][PlayerStats.GOALS] += 1 

        goal_assists = result[ResultStats.GOAL_ASSISTS.value]
        if goal_assists:
            for player_name in goal_assists: 
                player_dict[player_name][PlayerStats.ASSISTS] += 1

        interceptions = result[ResultStats.INTERCEPTIONS.value]
        if interceptions: 
            for player_name in interceptions: 
                player_dict[player_name][PlayerStats.INTERCEPTIONS] += 1

        tackles = result[ResultStats.TACKLES.value]
        if tackles:
            for player_name in tackles: 
                player_dict[player_name][PlayerStats.TACKLES] += 1         


    def _sort_leaderboard(self) -> None:
        """
        Sorts the teams in the leaderboard after all the games are played to get final rankings.

        Complexity:
            Best Case Complexity: O(R * log R)  where R is the total number of teams. This occurs when each team added is "greater" than the 
                                  previous team added, so they are always added to the next available slot after the last player, one after 
                                  another. Only binary search occurs, no shifting. So O(R) for iterating through each team * O(log R) for 
                                  binary search for last position. So the best case complexity is O(K * log K).

            Worst Case Complexity: O(R^2) Where R is the total number of teams. In the worst case, when iterating through R teams (O(R)), each 
                                   team is "lesser" than the previously added team, so they are always added to the front of the leaderboard. 
                                   The last team added to the front of the leaderboard will cause all the other teams to be shifted right which 
                                   is an O(R) operation. So worst complexity remains O(R^2). 
        """
        # Make a new leaderboard array sorted list
        temp_new_leaderboard = ArraySortedList(len(self)) 
        # Basically resorts the teams based on updated statistics
        for team in self.leaderboard: 
            temp_new_leaderboard.add(team) 
        # Swaps the original leaderboard with the updated leaderboard
        self.leaderboard = temp_new_leaderboard

    def delay_week_of_games(self, orig_week: int, new_week: int | None = None) -> None: 
        """
        Delay a week of games from one week to another.

        Args:
            orig_week (int): The original week to move the games from.
            new_week (int | None): The new week to move the games to. If this is None, it moves the games to the end of the season.

        Complexity:
            Best Case Complexity: O(1) which occurs if the games are moved from the first week to the second week.
            Worst Case Complexity: O(N) where N is the number of games week. This occurs when the games are moved from
                                   the first week to the final week.
        """  

        original_week = self.schedule[orig_week - 1]
        if new_week:
            self.schedule.insert(new_week, original_week)
        else:
            self.schedule.append(original_week)
        self.schedule.delete_at_index(orig_week - 1)


    def get_next_game(self) -> Generator[Game] | None:
        """
        Gets the next game in the season.

        Returns:
            Game: The next game in the season.
            or None if there are no more games left.

        Complexity:
            Best Case Complexity: O(N) where N is the total number of games.
            Worst Case Complexity: O(N) where N is the total number of games.
        """ 
        for week_of_games in self.schedule:
            for game in week_of_games:
                yield game

    def get_leaderboard(self) -> ArrayR[ArrayR[int | str]]:
        """
        Generates the final season leaderboard.

        Returns:
            ArrayR(ArrayR[ArrayR[int | str]]):
                Outer array represents each team in the leaderboard
                Inner array consists of 10 elements:
                    - Team name (str)
                    - Games Played (int)
                    - Points (int)
                    - Wins (int)
                    - Draws (int)
                    - Losses (int)
                    - Goals For (int)
                    - Goals Against (int)
                    - Goal Difference (int)
                    - Previous Five Results (ArrayR(str)) where result should be WIN LOSS OR DRAW

        Complexity:
            Best Case Complexity: O(L * M * N) where L is the total number of teams, M is the number of team statistics and N is the length 
                                  of the longest team statistic key. This occurs when the keys are always hashed to the correct position so 
                                  no probing is needed to find the team statistics since there are no collisions.
            Worst Case Complexity: O(L * M * (N + P)) where L is the total number of teams, M is the number of team statistics, N is the length 
                                   of the longest team statistic key and P is the size of the team statistics hashy probe table. This occurs when 
                                   the keys are hashed to the wrong position occupied by a different key (collision) and probing is done many times 
                                   using hashy probe to find the correct team statistics. In the worst case, the table is searched all the way 
                                   through, contributing to O(P).
        """
        full_leaderboard = ArrayR(len(self))
        for team_index, team in enumerate(self.leaderboard): # Iterates through every team in order of ranking
            team_stats = ArrayR(len(TeamStats) + 1) # Everything in team statistics and now with name included
            team_stats[0] = team.get_name() # Add the name
            team_stats_index = 1 # Since index 0 is already accessed
            for team_stat in TeamStats: # Add the rest of the team statistics
                if team_stat != TeamStats.LAST_FIVE_RESULTS:
                    team_stats[team_stats_index] = team[team_stat]
                    team_stats_index += 1

            team_stats[team_stats_index] = team.get_last_five_results()
            full_leaderboard[team_index] = team_stats # Added to the outer ArrayR

        return full_leaderboard

    def get_teams(self) -> ArrayR[Team]:
        """
        Returns:
            PlayerPosition (ArrayR(Team)): The teams participating in the season.

        Complexity:
            Best Case Complexity: O(1)
            Worst Case Complexity: O(1)
        """
        return self.teams

    def __len__(self) -> int:
        """
        Returns the number of teams in the season.

        Complexity:
            Best Case Complexity: O(1)
            Worst Case Complexity: O(1)
        """
        return self.length

    def __str__(self) -> str:
        """
        Optional but highly recommended.

        You may choose to implement this method to help you debug.
        However your code must not rely on this method for its functionality.

        Returns:
            str: The string representation of the season object.

        Complexity:
            Analysis not required.
        """
        return ""

    def __repr__(self) -> str:
        """Returns a string representation of the Season object.
        Useful for debugging or when the Season is held in another data structure."""
        return str(self)
