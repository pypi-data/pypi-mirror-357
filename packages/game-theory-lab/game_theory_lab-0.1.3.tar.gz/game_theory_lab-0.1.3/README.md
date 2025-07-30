# GameTheoryLab: Interactive Game Theory Simulation

**GameTheoryLab** is a Python-based simulation library that brings foundational concepts of Game Theory to life. With an intuitive interface and robust set of features, users can explore cooperative and competitive dynamics through interactive simulations of classical and custom-designed games.

The initial release focuses on the **Iterated Prisoner's Dilemma (IPD)**, enabling players to compete against diverse strategies, simulate matches and tournaments, and even create their own strategies.

---

## ✨ Features
The ```axelrod_interactive``` subpackage houses the functionality for simulating and interacting with the IPD. The subpackage boasts of the following features:

- **Extensive Strategy Library**: Includes 20 distinct IPD strategies—ranging from deterministic to stochastic, nice to nasty, forgiving to punitive, and simple to sophisticated.

- **Interactive User Mode**: The `User` class allows players to engage directly with strategies in one-on-one matches, offering hands-on insights into performance and behavior.

- **Flexible Match and Tournament Engine**: Simulate individual matches or full round-robin tournaments with customizable settings and detailed results.

- **CSV-Based Dataset Export**: Easily export match and tournament outcomes to `.csv` format for deeper analysis.

---

## 🛠️ Installation

GameTheoryLab is easy to set up on your local machine. All you need to do is:

```pip install game-theory-lab```

Then, import it into your project using:

```import gametheorylab```

And you're all set!

---

## 🚀 Usage

Below is a simple demo illustrating how to use GameTheoryLab to explore the IPD, with the help of the ``axelrod_interactive`` subpackage:

```
# Demonstrating using the User class to play against strategies and saving the results

from gametheorylab import axelrod_interactive as axl
from gametheorylab.axelrod_interactive.strategies.user import User
from gametheorylab.axelrod_interactive.strategies import STRATEGIES
from gametheorylab.axelrod_interactive.arena import Arena
from random import choice, sample

# Code that sets the payoff matrix for the session. Include at the top of your script for best practices
axl.set_payoffs()

user = User("Player1")
player = choice(list(STRATEGIES.values()))()
print(player.name + ":", player.__doc__) # Information about the strategy

arena = Arena(user, player, num_rounds=20, show_results=True)
result = arena.play_round()
result.to_csv(f"user_vs_{player.__class__.__name__}") # Saving the result to a .csv file for further analysis

# Demonstrating simulating a round-robin tournament and saving the results
from gametheorylab.axelrod_interactive.tournament import Tournament

players = [s() for s in sample(list(STRATEGIES.values()), k=15)]
tournament = Tournament(players, num_repeats=5, num_rounds=250)
result = tournament.play(show_results=True) # Tournament results are displayed in the console
result.to_csv("tournament_results.csv")

```

---

## 🤝 Contributing

Contributions are welcome! Please follow the steps to contribute:

1. Fork this repository
2. Create a new branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request.

---

## 🧑‍💻 Author

**Ayomide Olumide-Attah**

Math & CS Double Major at Fisk University

---

## 📄 License

This project is licensed under the MIT License.
