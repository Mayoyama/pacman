class Player:
    """Tracks player-owned game state: lives and cheat-mode invincibility.

    Position, movement, and collision belong to Movement, not Player.
    """

    def __init__(self, lives: int = 3) -> None:
        self.lives = lives
        self.is_invincible = False

    def get_lives(self) -> int:
        """Return the player's current life count."""
        return self.lives

    def increase_lives(self, amount: int = 1) -> None:
        """Add to the player's life count.

        Args:
            amount: Number of lives to add. Must be at least 1.

        Raises:
            ValueError: If amount is less than 1.
        """
        if amount < 1:
            raise ValueError("increase_lives: amount must be at least 1")
        self.lives += amount

    def decrease_lives(self) -> int:
        """Remove one life from the player's count.

        Returns:
            The player's remaining life count.

        Raises:
            ValueError: If called when no lives remain.
        """
        if self.lives < 1:
            raise ValueError("decrease_lives: no lives remaining")
        self.lives -= 1
        return self.lives

    def set_invincible(self, value: bool) -> None:
        """Enable or disable invincibility (cheat mode)."""
        self.is_invincible = value

    def get_invincible(self) -> bool:
        """Return whether the player is currently invincible."""
        return self.is_invincible
