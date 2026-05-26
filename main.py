import random
import time
from enum import Enum

WORLD_MAX = 10
WORLD_MIN = -10

class Difficulty(Enum):
    NORMAL = 1
    HARD = 2

class Gamemode(Enum):
    RETURN_TO_SHIP = 1
    BUILD_BASE = 2
    SURVIVE = 3

def convert_to_int(text, default):
    try:
        return int(text)
    except ValueError:
        print(f"Niepoprawna wartość. Wprowadzono domyślną wartość({default}).")
        return default

def porusz_sie(
    x,
    y,
    energy,
    difficulty,
    visited,
    old_x,
    old_y,
    old_energy,
    return_mode=False,
    target_x=None,
    target_y=None
):
    candidates = [
        ("N", x, y + 1),
        ("S", x, y - 1),
        ("E", x + 1, y),
        ("W", x - 1, y),
    ]

    if not return_mode:
        unvisited = []
        for direction, new_x, new_y in candidates:
            if (new_x, new_y) not in visited:
                unvisited.append((direction, new_x, new_y))
                
        if len(unvisited) > 0 and random.randint(1, 100) > 20:
            move, new_x, new_y = random.choice(unvisited)
        else:
            move, new_x, new_y = random.choice(candidates)
            
    else:
        best_moves = []
        for direction, candidate_x, candidate_y in candidates:
            distance = abs(target_x - candidate_x) + abs(target_y - candidate_y)
            best_moves.append((distance, direction, candidate_x, candidate_y))

        best_moves.sort(key=lambda item: item[0])
        best_choice = best_moves[0]
        move = best_choice[1]
        new_x = best_choice[2]
        new_y = best_choice[3]

    if new_x < WORLD_MIN or new_x > WORLD_MAX or new_y < WORLD_MIN or new_y > WORLD_MAX:
        print(f"Próba ruchu w kierunku {move} poza granice mapy! Łazik zostaje na miejscu.")
        energy -= 1 
        x = old_x
        y = old_y
    else:
        x = new_x
        y = new_y

    visited.add((x, y))

    if difficulty == Difficulty.HARD and random.randint(1, 4) == 1:
        energy -= 2
    else:
        energy -= 1

    print(f"Kierunek ruchu łazika: {move}")
    print(f"Pozycja łazika przed ruchem: ({old_x}, {old_y})")
    print(f"Pozycja łazika po wykonaniu ruchu: ({x}, {y})")
    print(f"Ilość energii przed wykonaniem ruchu: {old_energy}")
    print(f"Ilość energii po wykonaniu ruchu: {energy}")

    return x, y, energy, visited

def do_events(durability, energy, events, x, y, visited, difficulty, gamemode, old_x=None, old_y=None, threats=0):
    event_chance = random.randint(1, 100)
    
    if event_chance <= 60:
        random_event = random.randint(1, 100)
        
        if random_event <= 5:
            damage_amount = random.randint(1, 2)
            print(f"Uderzono w kamień! Utracono {damage_amount} punktów wytrzymałości.")
            durability -= damage_amount
            events.append("Kamień")
            threats += 1

        elif random_event <= 15:
            print("Znaleziono baterię! Dodano 5 punktów energii.")
            energy += 5
            events.append("Bateria")

        elif random_event <= 30:
            print("Wystąpiła burza piaskowa! Utracono 2 punkty energii.")
            energy -= 2
            events.append("Burza")
            threats += 1

        elif random_event <= 40:
            print("Teren błotnisty! Łazik został cofnięty na poprzednią pozycję.")
            if old_x is not None and old_y is not None:
                x = old_x
                y = old_y
            visited.add((x, y))
            events.append("Błoto")
            threats += 1

        elif random_event <= 50:
            print("Odnaleziono stację naprawczą! Dodano 2 punkty energii.")
            energy += 2
            events.append("Naprawa")

        elif random_event <= 80 and difficulty == Difficulty.HARD and gamemode == Gamemode.RETURN_TO_SHIP:
            print("Uderzono w karnister z paliwem, który eksplodował! Utracono 5 punktów wytrzymałości.")
            durability -= 5
            events.append("Bomba")
            threats += 1

        else:
            print("W tym kroku nie wystąpiło żadne zdarzenie.")

        if energy < 0:
            energy = 0
        if durability < 0:
            durability = 0

    return durability, energy, events, x, y, visited, threats

def print_report(name, start_x, start_y, start_energy, start_durability, x, y, step, energy, durability, events, visited, reason, result):
    print("\n" + "=" * 40)
    print("           RAPORT KOŃCOWY MISJI          ")
    print("=" * 40)
    print(f"Nazwa łazika: {name}")
    print(f"Parametry startowe: Pozycja ({start_x}, {start_y}), Energia: {start_energy}, Wytrzymałość: {start_durability}")
    print(f"Granice świata: od {WORLD_MIN} do {WORLD_MAX}")
    print(f"Końcowa pozycja łazika: ({x}, {y})")
    print(f"Status misji: {result} ({reason})")
    print(f"Liczba wykonanych kroków: {step}")
    print(f"Pozostałe zasoby: Energia: {energy} | Wytrzymałość: {durability}")
    
    if len(events) > 0:
        events_string = ', '.join(events)
        print(f"Zdarzenia napotkane: {events_string}")
    else:
        print("Zdarzenia napotkane: Brak")
        
    print(f"Łazik odwiedził {len(visited)} różnych pól mapy.")
    print("=" * 40)

def check_game_over(energy, durability, step):
    if energy <= 0:
        return "Brak energii.", "PORAŻKA"

    if durability <= 0:
        return "Brak wytrzymałości.", "PORAŻKA"

    if step >= 150:
        return "Przekroczono limit kroków.", "PORAŻKA"

    return None, None

def run_mission(gamemode, name, x, y, energy, durability, difficulty):
    # wyswietlanie startu dla trybów
    if gamemode == Gamemode.RETURN_TO_SHIP:
        print("Wybrano tryb gry `Powrót do statku`.")
    elif gamemode == Gamemode.BUILD_BASE:
        print("Wybrano tryb gry `Zbudowanie bazy`.")
    elif gamemode == Gamemode.SURVIVE:
        print("Wybrano tryb gry `Pokonywanie zagrożeń`.")

    print("\n=== Start misji ===")
    print(f"Nazwa minibota: {name}.")
    print(f"Pozycja startowa łazika: ({x}, {y}).")
    print(f"Granice świata wynoszą od {WORLD_MIN} do {WORLD_MAX}.")
    print(f"Początkowa ilość energii łazika: {energy}.")

    # ogólne zmienne gry
    start_x = x
    start_y = y
    start_energy = energy
    start_durability = durability
    
    step = 0
    events = []
    visited = set()
    visited.add((x, y))
    threats = 0
    
    return_mode = False
    target_x = None
    target_y = None

    # inicjalizacja akcji dla poszczególnych trybów
    if gamemode == Gamemode.RETURN_TO_SHIP:
        while True:
            goal_x = random.randint(WORLD_MIN, WORLD_MAX)
            goal_y = random.randint(WORLD_MIN, WORLD_MAX)
            if goal_x != x or goal_y != y:
                break
                
        print(f"Pozycja statku kosmicznego: ({goal_x}, {goal_y}).")
        
        if difficulty == Difficulty.NORMAL:
            goal_fuel = random.randint(15, 20)
        else:
            goal_fuel = random.randint(20, 25)
            
        print(f"Wymagana ilość paliwa do ukończenia misji: {goal_fuel}.")
        print("Cel misji: zdobycie wymaganej liczby paliwa oraz powrót do statku.")
        fuel = 0

    elif gamemode == Gamemode.BUILD_BASE:
        print("Cel misji: zebranie wystarczającej ilości materiałów potrzebnych do zbudowania bazy.")
        metal = 0
        resin = 0
        
        if difficulty == Difficulty.NORMAL:
            required_metal = random.randint(1, 3)
            required_resin = random.randint(2, 4)
            node_count = 18
        else:
            required_metal = random.randint(4, 7)
            required_resin = random.randint(3, 6)
            node_count = 24

        resources = {}
        total_metal = 0
        total_resin = 0
        
        while len(resources) < node_count or total_metal < required_metal * 2 or total_resin < required_resin * 2:
            resource_x = random.randint(WORLD_MIN, WORLD_MAX)
            resource_y = random.randint(WORLD_MIN, WORLD_MAX)
            
            if resource_x == x and resource_y == y:
                continue
            if (resource_x, resource_y) in resources:
                continue
                
            quantity_metal = random.randint(1, 3)
            quantity_resin = random.randint(1, 3)
            
            if random.randint(0, 1) == 1:
                quantity_resin = 0
            else:
                quantity_metal = 0

            resources[(resource_x, resource_y)] = {"metal": quantity_metal, "resin": quantity_resin}
            total_metal += quantity_metal
            total_resin += quantity_resin

        print(f"Rozmieszczono {len(resources)} punktów z surowcami na mapie.")
        print(f"Wymagana ilość materiałów: {required_metal} metalu oraz {required_resin} żywicy.")
        print(f"Łączna ilość materiałów dostępnych na mapie: {total_metal} metalu i {total_resin} żywicy.")

    elif gamemode == Gamemode.SURVIVE:
        print("Cel misji: przetrwanie określonej liczby zagrożeń oraz powrót do punktu startowego.")
        if difficulty == Difficulty.NORMAL:
            goal_threats = random.randint(3, 5)
        else:
            goal_threats = random.randint(6, 9)

    # główna pętla gry
    while True:
        # sprawdzanie warunku końca gry
        reason_result = check_game_over(energy, durability, step)
        if reason_result[0] is not None:
            reason = reason_result[0]
            result = reason_result[1]
            break

        # sprawdzanie warunków wygranej
        if gamemode == Gamemode.RETURN_TO_SHIP:
            if x == goal_x and y == goal_y and fuel >= goal_fuel:
                reason = "Dotarto do celu i zebrano paliwo."
                result = "SUKCES"
                break
            
            if fuel >= goal_fuel:
                return_mode = True
            else:
                return_mode = False
                
            target_x = goal_x
            target_y = goal_y

        elif gamemode == Gamemode.BUILD_BASE:
            if metal >= required_metal and resin >= required_resin:
                reason = "Zebrano wystarczającą liczbę materiałów."
                result = "SUKCES"
                break

        elif gamemode == Gamemode.SURVIVE:
            if threats >= goal_threats and x == start_x and y == start_y:
                reason = "Przeżyto wystarczającą ilość zagrożeń."
                result = "SUKCES"
                break
                
            if threats >= goal_threats:
                return_mode = True
            else:
                return_mode = False
                
            target_x = start_x
            target_y = start_y

        # aktualizacja kroku
        step += 1
        time.sleep(0.5)
        print("\n" + "─" * 40)
        print(f" KROK {step} ".center(40, "─"))
        print("─" * 40)

        old_x = x
        old_y = y
        old_energy = energy

        # poruszanie się
        x, y, energy, visited = porusz_sie(
            x, y, energy, difficulty, visited, old_x, old_y, old_energy,
            return_mode, target_x, target_y
        )

        # dodatkowe akcje zależne od wybranego trybu gry
        if gamemode == Gamemode.RETURN_TO_SHIP:
            action = random.randint(1, 100)
            if difficulty == Difficulty.NORMAL and action <= 50:
                fuel += 1
                print(f"Znaleziono paliwo! Aktualna ilość paliwa: {fuel}.")
            elif difficulty == Difficulty.HARD and action <= 25:
                fuel += 1
                print(f"Znaleziono paliwo! Aktualna ilość paliwa: {fuel}.")

        elif gamemode == Gamemode.BUILD_BASE:
            resource_position = (x, y)
            if resource_position in resources:
                node = resources[resource_position]
                del resources[resource_position]
                
                found_metal = node["metal"]
                found_resin = node["resin"]
                
                metal += found_metal
                resin += found_resin

                collected = []
                if found_metal > 0:
                    collected.append(f"{found_metal} metalu")
                if found_resin > 0:
                    collected.append(f"{found_resin} żywicy")

                collected_text = ', '.join(collected)
                print(f"Znaleziono surowce: {collected_text}. Aktualnie posiadasz {metal} metalu oraz {resin} żywicy.")
            else:
                print(f"Na pozycji ({x}, {y}) nie znaleziono żadnych surowców. Aktualnie posiadasz {metal} metalu oraz {resin} żywicy.")

        # losowe eventy
        durability, energy, events, x, y, visited, threats = do_events(
            durability, energy, events, x, y, visited, difficulty,
            gamemode, old_x, old_y, threats
        )

    # wyświetlanie wyniku końcowego
    print("\n=== KONIEC WYPRAWY ===")
    print(f"Wynik końcowy misji: {result}")
    print(f"Powód zakończenia misji: {reason}")

    score = energy
    if result == "SUKCES":
        score += 50

    print_report(name, start_x, start_y, start_energy, start_durability, x, y, step, energy, durability, events, visited, reason, result)

    # podsumowanie wyniku gry + ranking w punktach
    if gamemode == Gamemode.RETURN_TO_SHIP:
        print(f"Zdobyta ilość paliwa: {fuel}/{goal_fuel}")
        print(f"Pozycja statku kosmicznego: ({goal_x}, {goal_y}).")
    elif gamemode == Gamemode.BUILD_BASE:
        score += metal
        score += resin
        print(f"Łączna ilość zebranego metalu: {metal}")
        print(f"Łączna ilość zebranej żywicy: {resin}")
    elif gamemode == Gamemode.SURVIVE:
        score += threats
        print(f"Liczba przeżytych zagrożeń: {threats}")

    print(f"Wynik punktowy zdobyty podczas misji: {score}")

def game():
    print("=== Symulator minibota ===")

    # wczytywanie początkowych wartości
    print("Podaj nazwę łazika: ")
    name = input()
    
    while True:
        print("Podaj początkową pozycję X łazika: ")
        x = convert_to_int(input(), 0)
        if WORLD_MIN <= x <= WORLD_MAX:
            break
        print("Pozycja znajduje się poza granicami świata.")

    while True:
        print("Podaj początkową pozycję Y łazika: ")
        y = convert_to_int(input(), 0)
        if WORLD_MIN <= y <= WORLD_MAX:
            break
        print("Pozycja znajduje się poza granicami świata.")

    while True:
        print("Podaj ilość energii łazika (energia pozwala na poruszanie się po mapie): ")
        energy = convert_to_int(input(), 100)
        if energy <= 0:
            print("Liczba nie może być mniejsza lub równa zeru!")
        else:
            break
            
    while True:
        print("Podaj wartość wytrzymałości łazika (określa ile uszkodzeń może wytrzymać robot): ")
        durability = convert_to_int(input(), 100)
        if durability <= 0:
            print("Liczba nie może być mniejsza lub równa zeru!")
        else:
            break

    print("Podaj seed świata (lub ENTER, aby wylosować): ")
    seed_input = input()

    if seed_input:
        random.seed(seed_input)
        print(f"Ustawiono seed świata na: {seed_input}")
    else:
        random.seed()

    while True:
        try:
            print("\nWybierz poziom trudności gry (wpływa on na poziom trudności całej rozgrywki)\n1) Normalny\n2) Trudny")
            choice = int(input())

            if choice == 1:
                difficulty = Difficulty.NORMAL
                break
            elif choice == 2:
                difficulty = Difficulty.HARD
                break
            else:
                print("Wybierz 1 albo 2.")

        except ValueError:
            print("To nie jest liczba.")

    while True:
        try:
            print("\nWybierz cel misji (określa on fabułę oraz główny cel gry)\n1) Powrót do statku - Minibot musi zdobyć paliwo i wrócić do statku.\n2) Zbudowanie bazy - Minibot zbiera materiały potrzebne do zbudowania bazy.\n3) Pokonywanie zagrożeń - Minibot musi przetrwać określoną liczbę zagrożeń i wrócić do punktu startowego.")

            choice = int(input())

            if choice == 1:
                run_mission(Gamemode.RETURN_TO_SHIP, name, x, y, energy, durability, difficulty)
                break
            elif choice == 2:
                run_mission(Gamemode.BUILD_BASE, name, x, y, energy, durability, difficulty)
                break
            elif choice == 3:
                run_mission(Gamemode.SURVIVE, name, x, y, energy, durability, difficulty)
                break
            else:
                print("Wybierz 1-3.")

        except ValueError:
            print("To nie jest liczba.")

# pętla rozgrywająca grę w kółko
while True:
    game()

    print("Czy chcesz rozpocząć nową rozgrywkę? (t/n)")
    if input().lower() != "t":
        print("Gra została zakończona.")
        break