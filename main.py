# ==============================================================================
# main.py
# Haupt-Skript zum Testen und Demonstrieren der Kernfunktionalität.
# ==============================================================================
from src.game.decks import create_initial_action_deck, create_crisis_deck_phase1

def main():
    """Main function to demonstrate the implemented features."""
    print("--- Kode-Kommando Sprint 1: Kern-Loop ---")
    print("Initialisiere Datenstrukturen...\n")
    
    # --- Testfall: Initialisierung des Aktionskarten-Decks ---
    print("1. Erstelle Aktionskarten-Deck...")
    action_deck = create_initial_action_deck()
    print(f"Aktions-Deck erstellt: {action_deck}")
    print(f"Anzahl Karten: {len(action_deck)}")
    
    print("\nZiehe eine Beispielkarte:")
    card = action_deck.draw()
    print(f"Gezogene Karte: {card}")
    print(f"Verbleibende Karten im Deck: {len(action_deck)}\n")

    # --- Testfall: Initialisierung des Krisen-Karten-Decks ---
    print("2. Erstelle Krisen-Deck (für 2 Spieler)...")
    crisis_deck_2p = create_crisis_deck_phase1(player_count=2)
    print(f"Krisen-Deck (2P) erstellt: {crisis_deck_2p}")
    crisis_to_solve_2p = crisis_deck_2p.draw()
    print(f"Gezogene Krise (2P): {crisis_to_solve_2p}\n")

    print("3. Erstelle Krisen-Deck (für 4 Spieler)...")
    crisis_deck_4p = create_crisis_deck_phase1(player_count=4)
    print(f"Krisen-Deck (4P) erstellt: {crisis_deck_4p}")
    crisis_to_solve_4p = crisis_deck_4p.draw()
    print(f"Gezogene Krise (4P): {crisis_to_solve_4p}\n")
    
    print("--- Demonstration abgeschlossen ---")

if __name__ == "__main__":
    main()