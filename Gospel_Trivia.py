"""
A trivia game where you can learn all about Christ's ministry!

questions.txt contains all the questions in the game. You can add as many
as you'd like. It must be in the following format:
question;ans0;ans1;ans2;ans3;correct answer (0-3)

Disclaimer:
Currently, The question file is loaded with lots questions, and some of them were
made with help from generative AI.
It would have taken many hours to single-handedly get all the questions by myself,
so I researched, and used AI to help generate answers to fill in the game. Rest
assured, this project has taken me at least 20 hours to program not including
filling in questions.

Enjoy!

Written by Michael Marsh
04/01/2026
"""

import pygame
from pygame.locals import *
import sys
import os
import random

# Helper for use with pyinstaller
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # when running as .exe
    except Exception:
        base_path = os.path.abspath(".")  # when running normally
    return os.path.join(base_path, relative_path)

# Constants
RATE = 30
S_WIDTH = 1920
S_HEIGHT = 1080

BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(255, 255, 255)
RED = pygame.Color(150, 0, 0)
GREEN = pygame.Color(0, 150, 0)

#-------------------- Object Class Definitions --------------------
class Button(pygame.sprite.Sprite):
    def __init__(
        self,
        image,
        hover_image,
        x,
        y,
        index=None,
        text="",
        font=None,
        font_name=None,
        text_color=WHITE,
        padding=10
    ):
        super().__init__()

        self.index = index
        self.text = text
        self.font = font
        self.font_name = font_name
        self.text_color = text_color
        self.padding = padding

        # Store provided images
        self.normal_image_base = pygame.image.load(resource_path(image)).convert_alpha()
        self.hover_image_base = pygame.image.load(resource_path(hover_image)).convert_alpha()

        # Build visuals (with optional text overlay)
        self.normal_image = self._build_image(self.normal_image_base)
        self.hover_image = self._build_image(self.hover_image_base)

        self.image = self.normal_image
        self.rect = self.image.get_rect(topleft=(x, y))

    # -----------------------------
    # Image helpers
    # -----------------------------
    def _build_image(self, base_image):
        """Creates final button surface with optional text overlay"""
        image = base_image.copy()

        if not self.text or not self.font:
            return image

        text_surface = self._render_text_to_fit(image.get_width(), image.get_height())
        if text_surface:
            text_rect = text_surface.get_rect(
                center=(image.get_width() // 2, image.get_height() // 2)
            )
            image.blit(text_surface, text_rect)

        return image
    
    def change_text(self, new_text):
        """Updates the button text and re-renders the button surfaces."""
        self.text = new_text

        self.normal_image = self._build_image(self.normal_image_base)
        self.hover_image = self._build_image(self.hover_image_base)

        self.react()

    # -----------------------------
    # Text fitting
    # -----------------------------
    def _render_text_to_fit(self, max_width, max_height):
        """Wrap text and shrink font size if needed to fit within bounds"""

        font_size = self.font.get_height()

        while font_size > 10:
            test_font = pygame.font.SysFont(self.font_name, font_size)

            words = self.text.split(" ")
            lines = []
            current_line = ""

            for word in words:
                test_line = current_line + word + " "
                if test_font.size(test_line)[0] <= (max_width - 2 * self.padding):
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word + " "
            lines.append(current_line)

            line_surfaces = []
            total_height = 0

            for line in lines:
                surf = test_font.render(line.strip(), True, self.text_color)
                line_surfaces.append(surf)
                total_height += surf.get_height()

            if total_height <= (max_height - 2 * self.padding):
                combined_surface = pygame.Surface(
                    (max_width, total_height), pygame.SRCALPHA
                )

                y = 0
                for surf in line_surfaces:
                    x = (max_width - surf.get_width()) // 2
                    combined_surface.blit(surf, (x, y))
                    y += surf.get_height()

                return combined_surface

            font_size -= 2

        fallback_font = (
            pygame.font.Font(self.font.get_name(), 10)
            if hasattr(self.font, "get_name")
            else self.font
        )

        return fallback_font.render(self.text, True, self.text_color)

    # -----------------------------
    # Behavior
    # -----------------------------
    def react(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.image = self.hover_image
        else:
            self.image = self.normal_image

    def is_clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


class QuestionManager:
    def __init__(self, filepath, q_num):
        self.questions = []
        with open(resource_path(filepath), 'r') as f:
            for line in f:
                parts = line.strip().split(';')
                if len(parts) >= 6:
                    self.questions.append({
                        'q': parts[0],
                        'a': parts[1:5],
                        'k': int(parts[5])
                    })
        # Trim questions to amount specified
        random.shuffle(self.questions)
        self.questions = self.questions[:q_num]

    def next_question(self):
        if not self.questions:
            return None
        return self.questions.pop()
    

#-------------------- Game State Definitions --------------------
class TitleState:
    def __init__(self, engine):
        self.engine = engine

        self.background = pygame.image.load(resource_path("img/bg/title.jpg"))
        self.background = pygame.transform.scale(self.background, (S_WIDTH, S_HEIGHT))
        self.foreground = pygame.image.load(resource_path("img/fg/title.png"))
        self.foreground = pygame.transform.scale(self.foreground, (S_WIDTH, S_HEIGHT))

        # Buttons
        self.buttons = pygame.sprite.Group()
        self.start_btn = Button("img/btn/start.png", "img/btn/start-h.png", 760, 479)
        self.options_btn = Button("img/btn/options.png", "img/btn/options-h.png", 760, 680)
        self.quit_btn = Button("img/btn/quit.png", "img/btn/quit-h.png", 760, 883)

        self.buttons.add(self.start_btn, self.options_btn, self.quit_btn)

        # Music
        self.engine.change_music("sfx/title.mp3")

    def update(self, events):
        # Update button images
        for button in self.buttons:
            button.react()

        for event in events:
            if self.start_btn.is_clicked(event):
                self.engine.change_state(TriviaState)
            if self.options_btn.is_clicked(event):
                self.engine.change_state(OptionsState)
            if self.quit_btn.is_clicked(event):
                self.engine.running = False # Quit game

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        screen.blit(self.foreground, (0, 0))
        self.buttons.draw(screen)

class OptionsState:
    def __init__(self, engine):
        self.engine = engine

        self.background = pygame.image.load(resource_path("img/bg/options.jpg"))
        self.background = pygame.transform.scale(self.background, (S_WIDTH, S_HEIGHT))
        self.foreground = pygame.image.load(resource_path("img/fg/options.png"))
        self.foreground = pygame.transform.scale(self.foreground, (S_WIDTH, S_HEIGHT))

        # Buttons
        self.buttons = pygame.sprite.Group()
        self.back_btn = Button("img/btn/back.png", "img/btn/back-h.png", 50, 50)

        self.q_num_btn_left = Button("img/btn/arr_left.png", "img/btn/arr_left-h.png", 735, 465)
        self.q_num_btn_right = Button("img/btn/arr_right.png", "img/btn/arr_right-h.png", 1035, 465)

        self.score_btn_left = Button("img/btn/arr_left.png", "img/btn/arr_left-h.png", 735, 665)
        self.score_btn_right = Button("img/btn/arr_right.png", "img/btn/arr_right-h.png", 1035, 665)

        self.q_time_btn_left = Button("img/btn/arr_left.png", "img/btn/arr_left-h.png", 735, 865)
        self.q_time_btn_right = Button("img/btn/arr_right.png", "img/btn/arr_right-h.png", 1035, 865)

        self.buttons.add(self.back_btn, self.q_num_btn_left, self.q_num_btn_right, self.score_btn_left, self.score_btn_right, self.q_time_btn_left, self.q_time_btn_right)

        # Questions/game option
        self.q_num_label_surf = self.engine.smallest_font.render(f"Questions/Game (1-{self.engine.max_q})", True, BLACK)
        self.q_num_label_rect = self.q_num_label_surf.get_rect(center=(S_WIDTH // 2, 630))
        self.q_num_surf = self.engine.small_font.render(f"{self.engine.set_q}", True, WHITE)
        self.q_num_rect = self.q_num_surf.get_rect(center=(S_WIDTH // 2, S_HEIGHT // 2))

        # Score/question option
        self.score_label_surf = self.engine.smallest_font.render("Score/Question (100-10000)", True, BLACK)
        self.score_label_rect = self.score_label_surf.get_rect(center=(S_WIDTH // 2, 830))
        self.score_surf = self.engine.small_font.render(f"{self.engine.max_score}", True, WHITE)
        self.score_rect = self.score_surf.get_rect(center=(S_WIDTH // 2, (S_HEIGHT // 2) + 200))

        # Time/question option
        self.q_time_label_surf = self.engine.smallest_font.render("Time/Question until score reaches 0 (1-60 sec)", True, BLACK)
        self.q_time_label_rect = self.q_time_label_surf.get_rect(center=(S_WIDTH // 2, 1030))
        self.q_time_surf = self.engine.small_font.render(f"{self.engine.time_limit / 1000}", True, WHITE)
        self.q_time_rect = self.q_time_surf.get_rect(center=(S_WIDTH // 2, (S_HEIGHT // 2) + 400))

        # Music
        self.engine.change_music("sfx/options.mp3")
    
    def update(self, events):
        # Update button images
        for button in self.buttons:
            button.react()

        for event in events:
            if self.back_btn.is_clicked(event):
                self.engine.change_state(TitleState)

            if self.q_num_btn_left.is_clicked(event):
                if self.engine.set_q > 1:
                    self.engine.set_q -= 1
                    self.q_num_surf = self.engine.small_font.render(f"{self.engine.set_q}", True, WHITE)
            if self.q_num_btn_right.is_clicked(event):
                if self.engine.set_q < self.engine.max_q:
                    self.engine.set_q += 1
                    self.q_num_surf = self.engine.small_font.render(f"{self.engine.set_q}", True, WHITE)

            if self.score_btn_left.is_clicked(event):
                if self.engine.max_score > 100:
                    self.engine.max_score -= 100
                    self.score_surf = self.engine.small_font.render(f"{self.engine.max_score}", True, WHITE)
            if self.score_btn_right.is_clicked(event):
                if self.engine.max_score < 10000:
                    self.engine.max_score += 100
                    self.score_surf = self.engine.small_font.render(f"{self.engine.max_score}", True, WHITE)

            if self.q_time_btn_left.is_clicked(event):
                if self.engine.time_limit > 1:
                    self.engine.time_limit -= 1000
                    self.q_time_surf = self.engine.small_font.render(f"{self.engine.time_limit / 1000}", True, WHITE)
            if self.q_time_btn_right.is_clicked(event):
                if self.engine.time_limit < 60000:
                    self.engine.time_limit += 1000
                    self.q_time_surf = self.engine.small_font.render(f"{self.engine.time_limit / 1000}", True, WHITE)
                


    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        screen.blit(self.foreground, (0, 0))
        self.buttons.draw(screen)

        screen.blit(self.q_num_label_surf, self.q_num_label_rect)
        screen.blit(self.q_num_surf, self.q_num_rect)

        screen.blit(self.score_label_surf, self.score_label_rect)
        screen.blit(self.score_surf, self.score_rect)

        screen.blit(self.q_time_label_surf, self.q_time_label_rect)
        screen.blit(self.q_time_surf, self.q_time_rect)


class TriviaState:
    def __init__(self, engine):
        self.engine = engine

        # Reset score
        self.engine.score = 0

        # Mark timestamp at start of state
        self.refresh_ms = pygame.time.get_ticks()

        # Load assets
        self.bgs = [
        pygame.transform.scale(
            pygame.image.load(resource_path(f"img/bg/trivia{i}.jpg")),
            (S_WIDTH, S_HEIGHT)
            )
            for i in range(1, 11)]

        self.background = random.choice(self.bgs)

        # Setup UI
        b_width = 600
        b_height = 250
        spacing_x = 350
        spacing_y = 50

        start_x = (S_WIDTH - (b_width * 2 + spacing_x)) // 2
        start_y = 500

        self.buttons = pygame.sprite.Group()

        self.btn1 = Button("img/btn/ans1.png", "img/btn/ans1-h.png", start_x, start_y, 0, "", self.engine.normal_font, self.engine.font_name, WHITE)
        self.btn2 = Button("img/btn/ans2.png", "img/btn/ans2-h.png", start_x + b_width + spacing_x, start_y, 1, "", self.engine.normal_font, self.engine.font_name, WHITE)
        self.btn3 = Button("img/btn/ans3.png", "img/btn/ans3-h.png", start_x, start_y + b_height + spacing_y, 2, "", self.engine.normal_font, self.engine.font_name, WHITE)
        self.btn4 = Button("img/btn/ans4.png", "img/btn/ans4-h.png", start_x + b_width + spacing_x, start_y + b_height + spacing_y, 3, "", self.engine.normal_font, self.engine.font_name, WHITE)
        self.buttons.add(self.btn1, self.btn2, self.btn3, self.btn4)

        # Get questions
        self.q_manager = QuestionManager("questions.txt", self.engine.set_q)
        self.curr_q = self.q_manager.next_question()
        self.question_surfs = []

        # Music
        self.engine.change_music(f"sfx/trivia{random.randint(1, 5)}.mp3", 0.5)

        # Refresh UI
        self.refresh_ui()

        self.update_score_surface()
        self.score_rect = self.score_surf.get_rect(topleft=(5, 5))

    def render_multiline_text(self, text, font, color, max_width):
        """For large text (namely the question). Makes sure it 
            doesn't go off screen by wrapping around."""
        words = text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "

        lines.append(current_line)

        surfaces = [font.render(line.strip(), True, color) for line in lines]
        return surfaces

    def change_background(self):
        """Picks a random background from bg list, renders, and scales it."""
        pick = random.choice(self.bgs)
        while pick == self.background:
            pick = random.choice(self.bgs)
        self.background = pick
    
    def update_button_labels(self):
        """Updates button labels from curr_q's stored answers"""
        self.btn1.change_text(self.curr_q['a'][0])
        self.btn2.change_text(self.curr_q['a'][1])
        self.btn3.change_text(self.curr_q['a'][2])
        self.btn4.change_text(self.curr_q['a'][3])

    def update_question_text(self):
        """Updates question text at top of screen from curr_q's stored question"""
        self.question_surfs = self.render_multiline_text(self.curr_q['q'], self.engine.normal_font, WHITE, 1400)

    def update_score_surface(self):
        self.score_surf = self.engine.small_font.render(
            f"SCORE: {self.engine.score}", True, WHITE)
    
    def is_correct_answer(self, ans):
        """Helper function that compares chosen answer with correct answer, from curr_q's stored key"""
        if self.curr_q:
            return ans == self.curr_q['k']
        else:
            return None
    
    def show_transition_screen(self, correct, sub_text=None):
        """Displays a question transition screen of either correct, or incorrect."""
        if correct:
            self.engine.sfx_correct.play()
            message = "CORRECT!"
            bg_color = GREEN
        else:
            self.engine.sfx_incorrect.play()
            message = "INCORRECT!"
            bg_color = RED

        self.engine.screen.fill(bg_color)

        # Render and draw text
        cor_surf = self.engine.large_font.render(message, True, WHITE)
        cor_rect = cor_surf.get_rect(center=(S_WIDTH // 2, S_HEIGHT // 2))
        self.engine.screen.blit(cor_surf, cor_rect)

        if sub_text:
            ans_surf = self.engine.small_font.render(sub_text, True, WHITE)
            ans_rect = ans_surf.get_rect(center=(S_WIDTH // 2, (S_HEIGHT // 2) + 150))
            self.engine.screen.blit(ans_surf, ans_rect)


        # Update display
        pygame.display.flip()

        # Pause for 2 seconds
        pygame.time.wait(1500)

    def refresh_ui(self):
        self.change_background()
        self.update_button_labels()
        self.update_question_text()
        self.update_score_surface()

    def handle_answer(self, chosen):
        if self.is_correct_answer(chosen):
            elapsed = min(pygame.time.get_ticks() - self.refresh_ms, self.engine.time_limit)
            q_score = int(self.engine.max_score * (1 - elapsed / self.engine.time_limit))
            self.engine.score += q_score
            self.show_transition_screen(True, f"+ {q_score}")
        else:
            self.show_transition_screen(False, self.curr_q['a'][self.curr_q['k']])

        self.curr_q = self.q_manager.next_question()
        if self.curr_q:
            self.refresh_ms = pygame.time.get_ticks()
            self.refresh_ui()
        else:
            if self.engine.score > self.engine.hi_score:
                self.engine.hi_score = self.engine.score
            self.engine.change_state(GameOverState)


    def update(self, events):
        # Update button hover states
        for btn in self.buttons:
            btn.react()

        # Handle click events
        for event in events:
            for btn in self.buttons:
                if btn.is_clicked(event):
                    self.handle_answer(btn.index)

    def draw(self, screen):
        # Background
        screen.blit(self.background, (0, 0))

        # Score display
        screen.blit(self.score_surf, self.score_rect)

        # Question and answers
        y = 150
        for surf in self.question_surfs:
            rect = surf.get_rect(center=(S_WIDTH // 2, y))
            screen.blit(surf, rect)
            y += surf.get_height() + 10
        self.buttons.draw(screen)

class GameOverState:
    def __init__(self, engine):
        self.engine = engine

        self.background = pygame.image.load(resource_path("img/bg/game-over.jpg"))
        self.background = pygame.transform.scale(self.background, (S_WIDTH, S_HEIGHT))
        self.foreground = pygame.image.load(resource_path("img/fg/game-over.png"))
        self.foreground = pygame.transform.scale(self.foreground, (S_WIDTH, S_HEIGHT))

        # Buttons
        self.buttons = pygame.sprite.Group()
        self.retry_btn = Button("img/btn/retry.png", "img/btn/retry-h.png", 770, 680)
        self.options_btn = Button("img/btn/options.png", "img/btn/options-h.png", 320, 680)
        self.quit_btn = Button("img/btn/quit.png", "img/btn/quit-h.png", 1220, 680)
        self.buttons.add(self.retry_btn, self.options_btn, self.quit_btn)

        # Scoreboard
        self.score_surf = self.engine.small_font.render(f"- Score: {self.engine.score} -", True, WHITE)
        self.score_rect = self.score_surf.get_rect(center=(S_WIDTH // 2, 500))

        self.hi_score_surf = self.engine.small_font.render(f"- High Score: {self.engine.hi_score} -", True, WHITE)
        self.hi_score_rect = self.hi_score_surf.get_rect(center=(S_WIDTH // 2, 580))

        self.engine.sfx_applause.play()

    def update(self, events):
        # Update button images
        for button in self.buttons:
            button.react()
    
        for event in events:
            if self.retry_btn.is_clicked(event):
                self.engine.change_state(TriviaState)
            if self.options_btn.is_clicked(event):
                self.engine.change_state(OptionsState)
            if self.quit_btn.is_clicked(event):
                self.engine.running = False # Quit game

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        screen.blit(self.foreground, (0, 0))

        screen.blit(self.score_surf, self.score_rect)
        screen.blit(self.hi_score_surf, self.hi_score_rect)

        self.buttons.draw(screen)

#-------------------- Game engine --------------------
class GameEngine:
    def __init__(self):
        """Initializes game and sets state"""
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((S_WIDTH, S_HEIGHT))
        pygame.display.set_icon(pygame.image.load(resource_path("img/icon.png")))
        pygame.display.set_caption("Gospel Trivia!")
        self.font_name = "comicsansms"
        self.smallest_font = pygame.font.SysFont(self.font_name, 24)
        self.small_font = pygame.font.SysFont(self.font_name, 40)
        self.normal_font = pygame.font.SysFont(self.font_name, 80)
        self.large_font = pygame.font.SysFont(self.font_name, 120)
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = TitleState(self)

        

        self.score = 0
        self.hi_score = 0
        self.max_score = 1000
        self.time_limit = 20000 # in ms

        # Get questions amounts
        self.max_q = 0
        with open(resource_path("questions.txt"), 'r') as f:
            for line in f:
                self.max_q += 1
        if self.max_q > 10:
            self.set_q = 10
        else:
            self.set_q = self.max_q

        # SFX
        self.sfx_click = pygame.mixer.Sound(resource_path("sfx/click.mp3"))
        self.sfx_correct = pygame.mixer.Sound(resource_path("sfx/correct.mp3"))
        self.sfx_incorrect = pygame.mixer.Sound(resource_path("sfx/incorrect.mp3"))
        self.sfx_applause = pygame.mixer.Sound(resource_path("sfx/applause.mp3"))
        self.sfx_applause.set_volume(0.5)

    def change_state(self, state):
        """Changes game state"""
        self.state = state(self)

    def change_music(self, track, vol=1):
        pygame.mixer.music.set_volume(vol)
        pygame.mixer.music.load(resource_path(track))
        pygame.mixer.music.play(-1)


    def run(self):
        """Main game loop"""
        while self.running:
            events = pygame.event.get()

            #===== EVENTS =====
            for event in events:
                if event.type == QUIT:
                    self.running = False
                # Mouse input
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.sfx_click.play()

                # Keyboard input
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

            # Pass events to state, draw screen
            self.state.update(events)
            self.state.draw(self.screen)

            # Update display surface
            pygame.display.update()
            self.clock.tick(RATE)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = GameEngine()
    game.run()
