import random
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict


class ArenaSimulator:
    def __init__(self, winrate=0.5):
        self.winrate = winrate
        self.cost_per_run = 300
        self.pack_value = 100  # Valeur d'un paquet de cartes

        # Récompenses en or selon le nombre de victoires
        self.gold_rewards = {
            0: 0, 1: 0,
            2: 30,
            3: 45,
            4: 95,
            5: 150,
            6: 150,
            7: 300, 8: 300, 9: 300, 10: 300, 11: 300, 12: 300
        }

        # Récompenses en paquets selon le nombre de victoires
        self.pack_rewards = {
            0: 2, 1: 2, 2: 2, 3: 2, 4: 2, 5: 2,  # 0-5 victoires: 2 paquets
            6: 3, 7: 3,  # 6-7 victoires: 3 paquets
            8: 4,  # 8 victoires: 4 paquets
            9: 5,  # 9 victoires: 5 paquets
            10: 5,  # 10 victoires: 5 paquets
            11: 5,  # 11 victoires: 5 paquets
            12: None  # 12 victoires: variable selon défaites
        }

    def get_pack_reward(self, wins, losses):
        """Calcule le nombre de paquets selon les victoires et défaites"""
        if wins < 12:
            return self.pack_rewards.get(wins, 0)
        else:  # 12 victoires
            if losses == 0:
                return 8  # 12-0: 6 paquets
            elif losses == 1:
                return 7  # 12-1: 5 paquets
            elif losses == 2:
                return 6  # 12-2: 4 paquets
            else:
                return 4

    def calculate_bonus_chance(self, wins, losses):
        """Calcule la chance de bonus de 2000po selon les règles spécifiées"""
        if wins < 6:
            return 0.0

        base_chance = 0.05  # 5% de base à partir de 6 victoires

        if wins == 12:
            if losses == 0:
                return 0.13  # 13% pour 12-0
            elif losses == 1:
                return 0.12  # 12% pour 12-1
            elif losses == 2:
                return 0.11  # 11% pour 12-2

        # +1% par victoire supplémentaire après 6
        additional_chance = (wins - 6) * 0.01
        return base_chance + additional_chance

    def simulate_single_run(self):
        """Simule une seule run d'arène"""
        wins = 0
        losses = 0

        while wins < 12 and losses < 3:
            if random.random() < self.winrate:
                wins += 1
            else:
                losses += 1

        # Calcul des récompenses
        gold_reward = self.gold_rewards.get(wins, 0)
        pack_count = self.get_pack_reward(wins, losses)
        pack_value = pack_count * self.pack_value

        # Chance de bonus en or
        bonus_chance = self.calculate_bonus_chance(wins, losses)
        bonus_gold = 2000 if random.random() < bonus_chance else 0

        # Totaux
        total_gold = gold_reward + bonus_gold
        total_value = total_gold + pack_value
        profit_gold = total_gold - self.cost_per_run
        profit_total = total_value - self.cost_per_run

        return {
            'wins': wins,
            'losses': losses,
            'gold_reward': gold_reward,
            'bonus_gold': bonus_gold,
            'total_gold': total_gold,
            'pack_count': pack_count,
            'pack_value': pack_value,
            'total_value': total_value,
            'profit_gold': profit_gold,
            'profit_total': profit_total,
            'got_bonus': bonus_gold > 0
        }

    def simulate_cumulative_profit(self, num_runs=5000):
        """Simule les runs et retourne les profits cumulés"""
        cumulative_gold = []
        cumulative_total = []
        running_gold = 0
        running_total = 0

        for i in range(num_runs):
            result = self.simulate_single_run()
            running_gold += result['profit_gold']
            running_total += result['profit_total']
            cumulative_gold.append(running_gold)
            cumulative_total.append(running_total)

        return cumulative_gold, cumulative_total


def create_profit_graphs():
    """Crée les graphiques de profit cumulé"""
    # Configuration
    winrates = [0.48,0.49,0.5,0.52,0.54,0.55]
    #winrates = [0.69,0.7,0.71,0.72,0.73,0.74]
    num_runs = 10000
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']

    # Définir la graine pour la reproductibilité
    random.seed(4201)
    np.random.seed(4201)

    # Créer les données pour chaque winrate
    data_gold = {}
    data_total = {}

    for winrate in winrates:
        simulator = ArenaSimulator(winrate=winrate)
        cumulative_gold, cumulative_total = simulator.simulate_cumulative_profit(num_runs)
        data_gold[winrate] = cumulative_gold
        data_total[winrate] = cumulative_total

    # Graphique 1 : Profit en or uniquement
    plt.figure(figsize=(12, 6))
    plt.title('Profit Cumulé - Or Uniquement', fontsize=16, fontweight='bold')
    plt.axhline(y=0, color='black', linestyle='--', alpha=0.3, linewidth=1)
    plt.grid(True, alpha=0.3)

    for i, winrate in enumerate(winrates):
        plt.plot(range(1, num_runs + 1), data_gold[winrate],
                 label=f'{winrate * 100:.0f}% winrate',
                 color=colors[i], linewidth=2, alpha=0.8)

    plt.xlabel('Nombre de parties')
    plt.ylabel('Profit cumulé (po)')
    plt.legend(loc='upper left')
    plt.xlim(0, num_runs)

    plt.tight_layout()
    plt.savefig('profit_or_uniquement.png')
    plt.close()

    # Graphique 2 : Profit total (or + paquets)
    plt.figure(figsize=(12, 6))
    plt.title('Profit Cumulé - Total (Or + Paquets)', fontsize=16, fontweight='bold')
    plt.axhline(y=0, color='black', linestyle='--', alpha=0.3, linewidth=1)
    plt.grid(True, alpha=0.3)

    for i, winrate in enumerate(winrates):
        plt.plot(range(1, num_runs + 1), data_total[winrate],
                 label=f'{winrate * 100:.0f}% winrate',
                 color=colors[i], linewidth=2, alpha=0.8)

    plt.xlabel('Nombre de parties')
    plt.ylabel('Profit cumulé (po)')
    plt.legend(loc='upper left')
    plt.xlim(0, num_runs)

    plt.tight_layout()
    plt.savefig('profit_total_or_paquets.png')
    # plt.close()

    # Afficher quelques statistiques finales
    print("=== RÉSULTATS FINAUX APRÈS 1000 PARTIES ===")
    print("Winrate | Profit Or Final | Profit Total Final | Diff Or/Total")
    print("-" * 65)

    for winrate in winrates:
        final_gold = data_gold[winrate][-1]
        final_total = data_total[winrate][-1]
        diff = final_total - final_gold
        print(f"{winrate * 100:6.0f}% | {final_gold:14,.0f} | {final_total:17,.0f} | {diff:12,.0f}")


def create_detailed_analysis():
    """Analyse détaillée pour comprendre les différences"""
    print("\n=== ANALYSE DÉTAILLÉE ===")

    winrates_analysis = [0.5, 0.6, 0.7]

    for wr in winrates_analysis:
        print(f"\n--- Winrate {wr * 100:.0f}% ---")
        simulator = ArenaSimulator(winrate=wr)

        # Simulation de 10000 runs pour des stats précises
        results = []
        for _ in range(10000):
            result = simulator.simulate_single_run()
            results.append(result)

        profits_gold = [r['profit_gold'] for r in results]
        profits_total = [r['profit_total'] for r in results]

        print(f"Profit moyen (or): {np.mean(profits_gold):.1f} po")
        print(f"Profit moyen (total): {np.mean(profits_total):.1f} po")
        print(f"Écart-type (or): {np.std(profits_gold):.1f} po")
        print(f"Écart-type (total): {np.std(profits_total):.1f} po")
        print(f"Runs profitables (or): {sum(1 for p in profits_gold if p > 0) / len(profits_gold) * 100:.1f}%")
        print(f"Runs profitables (total): {sum(1 for p in profits_total if p > 0) / len(profits_total) * 100:.1f}%")


if __name__ == "__main__":
    # Créer les graphiques
    create_profit_graphs()

    # Analyse détaillée
    create_detailed_analysis()