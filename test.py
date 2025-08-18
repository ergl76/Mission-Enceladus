# Kode-Kommando: Minimales Pygame-Skript
# Auftrag: Ein leeres, schwarzes Fenster mit dem Titel "Mission Enceladus - Prototyp" erstellen.

# 1. Importieren der Pygame-Bibliothek
# Dies ist der erste Schritt in jedem Pygame-Programm.
import pygame

# 2. Initialisieren von Pygame
# Dieser Befehl startet alle Pygame-Module, die wir benötigen.
pygame.init()

# 3. Definieren der Fenstergrösse und Erstellen des Fensters
# Wir definieren die Breite und Höhe in Pixeln.
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# pygame.display.set_mode() erstellt das eigentliche Fenster (genannt "surface").
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# 4. Setzen des Fenstertitels
# Dieser Text wird in der Titelleiste des Fensters angezeigt.
pygame.display.set_caption("Mission Enceladus - Prototyp")

# 5. Die Haupt-Spielschleife (Game Loop)
# Ein Spiel ist eine Schleife, die ständig läuft. Sie prüft auf Benutzereingaben,
# aktualisiert den Spielzustand und zeichnet alles auf den Bildschirm.
# Wir verwenden eine Variable 'running', um die Schleife zu steuern.
running = True
while running:

    # 6. Ereignisverarbeitung (Event Handling)
    # Die Schleife überprüft alle Ereignisse, die der Benutzer auslöst (Mausklicks, Tastendrücke etc.).
    for event in pygame.event.get():
        # Das wichtigste Ereignis ist hier das Schliessen des Fensters.
        if event.type == pygame.QUIT:
            # Wenn der Benutzer auf das 'X' klickt, setzen wir 'running' auf False.
            # Dadurch wird die while-Schleife beim nächsten Durchlauf beendet.
            running = False

    # 7. Zeichnen des Hintergrunds
    # Wir füllen den gesamten Bildschirm mit einer Farbe.
    # Farben werden als (R, G, B) Tupel angegeben. (0, 0, 0) ist schwarz.
    screen.fill((0, 0, 0))

    # 8. Aktualisieren des Bildschirms
    # Nachdem wir alles gezeichnet haben (hier nur der schwarze Hintergrund),
    # müssen wir Pygame anweisen, den Bildschirm tatsächlich zu aktualisieren,
    # damit der Benutzer die Änderungen sieht.
    pygame.display.flip()

# 9. Beenden von Pygame
# Sobald die Schleife beendet ist, müssen wir die Pygame-Module sauber beenden.
# Dies ist das Gegenteil von pygame.init().
pygame.quit()

# Mission erfüllt. Das Skript ist bereit zur Ausführung.
