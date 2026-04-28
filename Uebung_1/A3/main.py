from random import randint
from statistics import mean
    
"""
Simulation von Pre-Image und Collision Experimenten.
"""

DEFAULT_RUNS = 1000
DEFAULT_N = 10000

def rand_nums_until_key(n: int, key: int) -> int:
    """
    Generiert Zufallszahlen bis bestimmter Wert (key) getroffen wird.
    """
    count = 1
    num = randint(0, n - 1)
    
    while num != key:
        count += 1
        num = randint(0, n - 1)
    
    return count

def rand_nums_until_collision(n: int) -> int:
    """
    Generiert Zufallszahlen bis eine Kollision auftritt.
    """
    count = 1
    seen = set()
    
    num = randint(0, n - 1)
    seen.add(num)
    
    while True:
        num = randint(0, n - 1)
        count += 1
        
        if num in seen:
            return count
        
        seen.add(num)
        
def verification(runs: int = DEFAULT_RUNS, n: int = DEFAULT_N) -> None:
    """
    Führt mehrere Simulationen durch und vergleicht Mittelwerte mit Erwartungswerten.
    """
    print(f"Running {runs} iterations with n = {n}... \n")
    
    # Pre-Image
    counts_pre = [
        rand_nums_until_key(n, randint(0, n - 1))
        for _ in range(runs)
        ]
    avg_pre = mean(counts_pre)
    deviation_pre = abs(n - avg_pre)
    print(f"a) Pre-Image -> Expected ~ {n}, Actual = {avg_pre}, Abweichung = {deviation_pre}")
    
    # Collision
    counts_col = [
        rand_nums_until_collision(n)
        for _ in range(runs)
    ]
    avg_col = mean(counts_col)
    deviation_col = abs(125 - avg_col)
    print(f"b) Collision -> Expected ~ 125 (für n = 10000), Actual = {avg_col}, Abweichung = {deviation_col}\n")

if __name__ == '__main__':
    print("\n=== Zufallsexperimente: Pre-Image & Collision ===\n")
    print("a) Pre-Image Simulation")
    print("b) Collision Simulation")
    print("c) Verifikation")
    
    choice = input("Auswahl (a/b/c, sonst quit): ").strip().lower()
    
    if choice == 'a':
        n = int(input("n: "))
        y = int(input("Zielwert y: "))
        count = rand_nums_until_key(n, y)
        print(f"Benötigte Versuche: {count}")
    
    elif choice == 'b':
        n = int(input("n: "))
        count = rand_nums_until_collision(n)
        print(f"Benötigte Versuche bis Kollision: {count}")
    
    elif choice == 'c':
        verification()
    
    else:
        print("Programm beendet.")