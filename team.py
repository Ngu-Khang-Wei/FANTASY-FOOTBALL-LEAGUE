from __future__ import annotations
from data_structures.referential_array import ArrayR
from constants import GameResult, PlayerPosition, PlayerStats, TeamStats, Constants
from customconstants import CustomConstants
from player import Player
from typing import Collection, TypeVar
from data_structures.linked_queue import LinkedQueue
from data_structures.linked_list import LinkedList
from hashy_step_table import HashyStepTable
T = TypeVar("T")


class Team:
    TEAM_NUMBER_GLOBAL = 0
    def __init__(self, team_name: str, players: ArrayR[Player]) -> None: 
        """
        Constructor for the Team class

        Args:
            team_name (str): The name of the team
            players (ArrayR[Player]): The players of the team

        Returns:
            None

        Complexity:

            Best Case Complexity: O(M + N + P * Q + R * S) where M is the size of self.statistics hashy step table, N is size of self.players hashy step table,
                                  P is the number of team statistics, Q is the length of the longest team statistic key, R is the number of player positions and 
                                  S is the length of the longest player position key. This occurs when every single key is hashed to an unoccupied position in the hashy step table when inserting, 
                                  so no probing is needed since there are no collisions. The table sizes selected can greatly outweight the number of statistics and players so it is included in the analysis,
                                  contributing to O(M + N).

            Worst Case Complexity: O(M * (N + P) + Q * (R + S)) where M is the number of team statistics, N is the length of the longest team statistic key, P is the size of self.statistics hashy step table, Q is the number of player positions, 
            R is the length of the longest player position key and S is size of self.players hashy step table. This occurs when the keys are hashed to occupied postions (collision) when inserting and probing is done many times using hashy probe to find the 
            empty slot for the team statistics and player positions. In the worst case, the table is searched all the way through, contributing to O(P) and O(S). 

        
        """
        self.team_name = team_name
        self.length = len(players)
        self.number = Team.TEAM_NUMBER_GLOBAL + 1
        Team.TEAM_NUMBER_GLOBAL += 1
        self.unsorted_player_array = players

        # This whole portion of code is for selecting the table size so that rehash does not happen, leading to better efficiency.
        # The complexity of this portion of code is overshadowed by the later parts.
        num_player_positions = len(PlayerPosition) * CustomConstants.LOAD_FACTOR
        hashy_table_sizes = CustomConstants.TABLE_SIZES
        table_start_index = 0
        for table_size_index in range(len(hashy_table_sizes)): # Number of iterations will always be less than the table size, so can be ignored.
            if hashy_table_sizes[table_size_index] > num_player_positions:
                table_start_index = table_size_index
                break
        
        #Initialise the hashy step tables
        self.players = HashyStepTable(hashy_table_sizes[table_start_index:]) 
        self.statistics = HashyStepTable(CustomConstants.TABLE_SIZES[CustomConstants.TEAM_INIT_TABLE_SIZE_INDEX:]) # Prevent rehashing 

        # Setting the values
        for team_stat in TeamStats:
            self.statistics[team_stat.value] = 0 
        self.statistics[TeamStats.LAST_FIVE_RESULTS.value] = LinkedQueue()         
        for player_position in PlayerPosition: 
            self.players[player_position.value] = LinkedList() 
        for player in players: 
            self.players[player.get_position().value].append(player) 

    def reset_stats(self) -> None: 
        """
        Resets all the statistics of the team to the values they were during init.

        Complexity:
            Best Case Complexity: O(M * N) Where M is the number of team statistics and N is the length of 
                                  the longest team statistic key to be hashed. This occurs when the keys are always hashed to the correct position, so no further probing is 
                                  needed to find the team statistics since there is no collision.
            Worst Case Complexity: O(M * (N + O)) Where M is the number of team statistics, N is the length 
                                   of the longest team statistic key to be hashed and O is the size of the self.statistics hashy step table. This occurs when the keys are hashed to the 
                                   wrong position occupied by different keys (collision) and probing is done many times using hashy probe to find the correct team statistics. In the worst case, 
                                    the table is searched all the way through, contributing to O(O). 
        """
        for team_stat in TeamStats:
            self.statistics[team_stat.value] = 0 
        self.statistics[TeamStats.LAST_FIVE_RESULTS.value] = LinkedQueue() 

    def add_player(self, player: Player) -> None: 
        """
        Adds a player to the team.

        Args:
            player (Player): The player to add

        Returns:
            None

        Complexity:
            Best Case Complexity: O(N) where N is the key length corresponding to the the input player's position. This occurs when the key is always hashed to the correct position, so no further probing is 
                                  needed to find the player position since there is no collision.
            Worst Case Complexity: O(M + N) where M is the key length corresponding to the the input player's position and N is the size
            of self.players hashy step table. This occurs when the key is hashed to the 
                                    wrong position occupied by a different key (collision) and probing is done many times using hashy probe to find the correct player position. In the worst case, 
                                    the table is searched all the way through, contributing to O(N).
        """
        self.players[player.get_position().value].append(player) 
        self.length += 1

    def remove_player(self, player: Player) -> None:
        """
        Removes a player from the team.

        Args:
            player (Player): The player to remove

        Returns:
            None

        Complexity:
            Best Case Complexity: O(N) where N is the key length corresponding to the the input player's position and the
                                  player to be deleted is the very first player in his/her team position group.
                                  This also occurs when the key is always hashed to the correct position, so no further probing is 
                                  needed to find the player position since there is no collision.
            Worst Case Complexity: O(M + N + O) where M is the key length corresponding to the the input player's position, N is the size
             of self.players hashy step table and O is the number of 
                                   players in the same position group as the player to be removed. This happens
                                   when the player to be deleted is the last player in his/her team position group, contributing to O(O). This occurs when the key is hashed to the 
                                    wrong position occupied by a different key (collision) and probing is done many times using hashy probe to find the correct player position. In the worst case, 
                                    the table is searched all the way through, contributing to O(N).
        """
        team_position_group = self.players[player.get_position().value] 
        team_position_group.delete_at_index(team_position_group.index(player)) 
        self.length -= 1

    def get_number(self) -> int:
        """
        Returns the number of the team.

        Complexity:
            Analysis not required.
        """
        return self.number

    def get_name(self) -> str:
        """
        Returns the name of the team.

        Complexity:
            Analysis not required.
        """
        return self.team_name

    def get_players(self, position: PlayerPosition | None = None) -> Collection[Player] | None: 
        """
        Returns the players of the team that play in the specified position.
        If position is None, it should return ALL players in the team.
        You may assume the position will always be valid.
        Args:
            position (PlayerPosition): The position of the players to return

        Returns:
            Collection[Player]: The players that play in the specified position
            held in a valid data structure provided to you within
            the data_structures folder this includes the ArrayR
            which was previously prohibited.

            None: When no players match the criteria / team has no players

        Complexity:
            Best Case Complexity: O(1) when there are no players in the team. This can happen when all the players are removed from
            the team using the remove player method. When this happens the function just returns None.
            Worst Case Complexity: O(M * (N + O) + P) Where M is the number of player positions, N is the length of the 
                                   longest player position key, O is the size of the self.players hashy step table 
                                   and P is the total number of players in this team. This occurs when the keys are hashed to the 
                                    wrong position occupied by a different key (collision) and probing is done many times using hashy probe to find the correct player position. In the worst case, 
                                    the table is searched all the way through, contributing to O(O). Also, every single player has to be retrived and put in a collection
                                    to be returned so the number of iterations of that will be the the total number of players, contributing to O(P). This is also
                                    when no player position is specified in the function call.
        """
        # Don't have to check the rest if len(self) is 0 since there are no players
        if len(self) == 0:
            return None
        elif position:
            if self.players[position.value].is_empty(): # If no players in the position requested
                return None
            position_players = LinkedList() 
            for players in self.players[position.value]: 
                position_players.append(players)
            return position_players
        else:
            all_players = LinkedList() 
            for player_position in PlayerPosition: # Get every single player in the team in a specified order
                for player in self.players[player_position.value]: 
                    all_players.append(player)                             

            return all_players


    def get_statistics(self):
        """
        Get the statistics of the team

        Returns:
            statistics: The teams' statistics

        Complexity:
            Best Case Complexity: O(1)
            Worst Case Complexity: O(1)
        """
        return self.statistics

    def get_last_five_results(self) -> Collection[GameResult] | None: 
        """
        Returns the last five results of the team.
        If the team has played less than five games,
        return all the result of all the games played so far.

        For example:
        If a team has only played 4 games and they have:
        Won the first, lost the second and third, and drawn the last,
        the array should be an array of size 4
        [GameResult.WIN, GameResult.LOSS, GameResult.LOSS, GameResult.DRAW]

        **Important Note:**
        If this method is called before the team has played any games,
        return None the reason for this is explained in the specefication.

        Returns:
            Collection[GameResult]: The last five results of the team
            or
            None if the team has not played any games.

        Complexity:
            Best Case Complexity: O(N) where N is the length of the 'LAST FIVE RESULTS' key. This occurs when
                                 the key is always hashed to the correct position, so no probing is 
                                  needed to find the last five results queue since there is no collision.
            Worst Case Complexity: O(M + N) where M is the length of the 'LAST FIVE RESULTS' key and
                                    N is the size of the self.statistics hashy step table. This occurs when the key is hashed to the 
                                    wrong position occupied by a different key (collision) and probing is done many times using hashy probe 
                                    to find the last five results queue. In the worst case, the table is searched all the way through, contributing to O(N).
        """
        if self.statistics[TeamStats.LAST_FIVE_RESULTS.value].is_empty(): 
            return None
        return self.statistics[TeamStats.LAST_FIVE_RESULTS.value] 

    def get_top_x_players(self, player_stat: PlayerStats, num_players: int) -> list[tuple[int, str, Player]]:
        """
        Note: This method is only required for FIT1054 students only!

        Args:
            player_stat (PlayerStats): The player statistic to use to order the top players
            num_players (int): The number of players to return from this team

        Return:
            list[tuple[int, str, Player]]: The top x players from this team
        Complexity:
            Best Case Complexity:
            Worst Case Complexity:
        """
        raise NotImplementedError

    def __setitem__(self, statistic: TeamStats, value: int) -> None: 
        """
        Updates the team's statistics.

        Args:
            statistic (TeamStats): The statistic to update
            value (int): The new value of the statistic

        Complexity:
            Best Case Complexity: O(N) where N is the length of the longest key among the "GOALS DIFFERENCE", "GOALS FOR" and "GOALS AGAINST"
                                  keys for team statistics. This occurs when the team statistic chosen is either 'GOALS FOR' or 'GOALS AGAINST'.
                                  Best case is when the keys are always hashed to the correct position, so no further probing is needed to find
                                  the "GOALS DIFFERENCE", "GOALS FOR" and "GOALS AGAINST" statistics since there are no collisions.

            Alternative worst case: O(get_players + M + N) where get_players is the worst case complexity of self.get_players(), M is the length 
                                    of the longest team statistic key used in the function (except for the key "GOAL DIFFERENCE") and N is the 
                                    size of the self.statistics hashy step table. O(M + N) is the worst case complexity for setting the team 
                                    statistics using the set_item method from hashy step table. This happens when the team statistic keys are 
                                    hashed to the wrong position occupied by a different key (collision) and probing is done many times using hashy
                                    probe to find the right team statistic, so the table has to be searched all the way through, contributing to
                                    O(N). There is no way to prove O(get_players) > O(M + N) or vice versa, so both included.
        """
        if (statistic == TeamStats.GOALS_FOR) or (statistic == TeamStats.GOALS_AGAINST):
            self.statistics[statistic.value] = value 
            self.statistics[TeamStats.GOALS_DIFFERENCE.value] = self.statistics[TeamStats.GOALS_FOR.value] - self.statistics[TeamStats.GOALS_AGAINST.value] 
        else: 
            increment = value - self.statistics[statistic.value] # If WINS = 2, statistic = WIN and value = 5, increment = 5 - 2 = 3
            self.statistics[statistic.value] = value 

            # Increment number of games played in total for the team and every player inside
            self.statistics[TeamStats.GAMES_PLAYED.value] += increment 
            for player in self.get_players(): 
                player.statistics[PlayerStats.GAMES_PLAYED.value] += increment # O(1)

            game_result = None
            if statistic == TeamStats.WINS:
                self.statistics[TeamStats.POINTS.value] += (increment * GameResult.WIN) 
                game_result = GameResult.WIN
            elif statistic == TeamStats.DRAWS:
                self.statistics[TeamStats.POINTS.value] += (increment * GameResult.DRAW) 
                game_result = GameResult.DRAW
            else:
                game_result = GameResult.LOSS # No need to add 0

            last_five_results_container = self.statistics[TeamStats.LAST_FIVE_RESULTS.value] 
            for _ in range(increment if increment <= 5 else 5): # if 7 WINS, serve and append 7 times or 5 times yield similar output
                if len(last_five_results_container) == 5:
                    last_five_results_container.serve()
                last_five_results_container.append(game_result)


    def __getitem__(self, statistic: TeamStats) -> int: 
        """
        Returns the value of the specified statistic.

        Args:
            statistic (TeamStats): The statistic to return

        Returns:
            int: The value of the specified statistic

        Raises:
            ValueError: If the statistic is invalid

        Complexity:
            Best Case Complexity: O(N) Where N is the key length corresponding to the team statistic input. This occurs when the key 
                                  is always hashed to the correct position, so no probing is needed to find the corresponding team statistic 
                                  since there is no collision.

            Worst Case Complexity: O(M + N) Where M is the key length corresponding to the team statistic input and N is the size of the team 
                                   statistics hash table. This occurs when the key is hashed to the wrong position occupied by a different key 
                                   (collision) and probing is done many times using hashy probe to find the correct team statistic. In the worst 
                                   case, the table is searched all the way through, contributing to O(N).
        """
        if statistic == TeamStats.LAST_FIVE_RESULTS: # LAST FIVE RESULTS is obtained via another method
            raise ValueError
        return self.statistics[statistic.value] 

    def get_unsorted_player_array(self) -> ArrayR[Player]:
        """
        Returns the array of players in the team in no particular order.

        Complexity:
            Best Case Complexity: O(1)
            Worst Case Complexity: O(1)
        """
        return self.unsorted_player_array # More efficient way to get all players for a function in season

    def __len__(self) -> int:
        """
        Returns the number of players in the team.

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
            str: The string representation of the team object.

        Complexity:
            Analysis not required.
        """
        return ""

    def __repr__(self) -> str:
        """Returns a string representation of the Team object.
        Useful for debugging or when the Team is held in another data structure."""
        return str(self)
    
    def __lt__(self, other : Team) -> bool: 
        """
        Returns whether a team is 'less than' another team. A team is less than 
        another team if the former is superior in terms of their game performance
        or, if equal performance, the former is lexicographically less than the 
        other team.

        Returns:
            bool: Whether a team is 'less than' another team or not.

        Complexity:
            Best Case Complexity: O(N) where N is the length of the 'POINTS' key. This occurs when the points of the self team is not
                                  equal to the points of the other team, so only the very first if statement is visited. Best case is 
                                  when the key is always hashed to the right position, so no probing is needed to find the 'POINTS' team 
                                  statistic since there is no collision.
                                  
            Worst Case Complexity: O(M + N) where M is the length of the longest key among the "POINTS", "GOAL DIFFERENCE" AND "GOALS FOR" 
                                   keys for team statistics and N is the size of the self.statistics hashy step table. This occurs when the 
                                   self team and the other team both have the same points, goals difference and goals for values. Hence, all 
                                   the if statements have to be visited. This also occurs when the keys are hashed to the wrong position occupied 
                                   by a different key (collision) and probing is done many times using hashy probe to find the correct team 
                                   statistic. In the worst case, the table is searched all the way through, contributing to O(N).
            
        """
        if self[TeamStats.POINTS] != other[TeamStats.POINTS]:
            return self[TeamStats.POINTS] > other[TeamStats.POINTS]
        elif self[TeamStats.GOALS_DIFFERENCE] != other[TeamStats.GOALS_DIFFERENCE]:
            return self[TeamStats.GOALS_DIFFERENCE] > other[TeamStats.GOALS_DIFFERENCE]
        elif self[TeamStats.GOALS_FOR] != other[TeamStats.GOALS_FOR]:
            return self[TeamStats.GOALS_FOR] > other[TeamStats.GOALS_FOR]
        else:
            return self.team_name < other.get_name() # Compare lexicographically

