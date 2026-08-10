class Player:
    """Tracks player-owned game state.

    Position, movement, and collision belong to Movement, not Player.
    """

    def __init__(self, lives: int = 3) -> None:
        """Sets up starting lives and invincibility state.

        Args:
            lives: Starting life count.
        """
        self._lives = lives
        self._score = 0
        self._is_invincible = False
        self._name = ""

    def set_name(self) -> None:
        """Prompts for and validates the player's name via stdin.

        Repeats the prompt until a name of 3-10 characters, containing
        only letters, digits, and spaces, is entered.
        """
        while not self._name:
            self._name = str(input("Player's name: "))
            for char in self._name:
                if len(self._name) < 3:
                    print("WARNING: player name too short.")
                    self._name = ""
                    break
                if len(self._name) > 10:
                    print("WARNING: player name too long.")
                    self._name = ""
                    break
                if not char.isalnum() and char != ' ':
                    print("WARNING: invalid character in player name.")
                    self._name = ""
                    break

    def get_name(self) -> str:
        """Return the player's name."""
        return self._name

    def get_lives(self) -> int:
        """Return the player's current life count."""
        return self._lives

    def increase_lives(self, amount: int = 1) -> None:
        """Add to the player's life count.

        Args:
            amount: Number of lives to add. Must be at least 1.

        Raises:
            ValueError: If amount is less than 1.
        """
        if amount < 1:
            raise ValueError("increase_lives: amount must be at least 1")
        self._lives += amount

    def decrease_lives(self) -> int:
        """Remove one life from the player's count.

        Returns:
            The player's remaining life count.

        Raises:
            ValueError: If called when no lives remain.
        """
        if self._lives < 1:
            raise ValueError("decrease_lives: no lives remaining")
        self._lives -= 1
        return self._lives

    def increase_score(self, points: int) -> None:
        if points < 1:
            raise ValueError("increase_score: 0 or negative value passed")
        self._score += points

    def get_score(self) -> int:
        return self._score

    def set_invincible(self, value: bool) -> None:
        """Enable or disable invincibility (cheat mode)."""
        self._is_invincible = value

    def get_invincible(self) -> bool:
        """Return whether the player is currently invincible."""
        return self._is_invincible
