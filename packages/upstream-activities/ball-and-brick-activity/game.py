#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# BallAndBrick
# Copyright (C) 2017  Hitesh Agarwal
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from random import random
import pygame
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class BallAndBrick:
    def __init__(self):
        self.green = (34, 139, 34)
        self.red = (255, 0, 0)
        self.yellow = (255, 255, 153)

        self.white = (255, 255, 255)
        self.blue = (0, 0, 255)
        self.black = (0, 0, 0)
        self.back_col = (255, 255, 255)
        self.brick_col = (0, 0, 0)
        self.scroll_col = (0, 0, 0)
        self.ball_still = 0
        self.ball_play = 1
        self.ball_won = 2
        self.ball_game_over = 3
        self.clock = pygame.time.Clock()
        self.pause = False
        self.shake = 0
        self.ball_vel = pygame.Vector2(7, -7)
        self.theme_keys = (
            pygame.K_1,
            pygame.K_2,
            pygame.K_3,
            pygame.K_4,
            pygame.K_5,
            pygame.K_6,
            pygame.K_7,
            pygame.K_8,
            pygame.K_9,
        )
        self.back_cols = (
            (255, 255, 255),
            (228, 47, 12),
            (47, 79, 79),
            (140, 89, 51),
            (0, 255, 255),
            (115, 69, 35),
            (6, 43, 22),
            (25, 25, 112),
            (9, 84, 190),
        )
        self.brick_cols = (
            (0, 0, 0),
            (245, 226, 226),
            (255, 255, 255),
            (237, 201, 175),
            (34, 139, 34),
            (0, 255, 0),
            (173, 255, 47),
            (255, 255, 49),
            (212, 219, 178),
        )
        self.scroll_cols = (
            (0, 0, 0),
            (0, 255, 0),
            (255, 255, 255),
            (237, 201, 175),
            (34, 139, 34),
            (0, 255, 0),
            (173, 255, 47),
            (255, 255, 49),
            (212, 219, 178),
        )

    # Called to save the state of the game to the Journal.
    def write_file(self, file_path):
        pass

    # Called to load the state of the game from the Journal.
    def read_file(self, file_path):
        pass

    def run(self):
        self.brick_hit_sound = pygame.mixer.Sound("assets/brickhit.ogg")
        self.paddle_hit_sound = pygame.mixer.Sound("assets/paddlehit.ogg")
        self.brick_hit_sound.set_volume(0.8)

        def restart_game():
            pygame.mixer.music.load("assets/jazz.ogg")
            pygame.mixer.music.play(-1)
            screen = pygame.display.get_surface()
            scroller_w = round((screen.get_width()) / 10.7)
            scroller_h = round((screen.get_height()) / 40)
            b_diameter = round((scroller_w) / 3.75)
            y_scrol = (screen.get_height() - 10) - scroller_h - 70

            self.lives = 3
            self.score = 0
            self.state = self.ball_still

            self.paddle = pygame.Rect(
                int(screen.get_width() / 2), y_scrol, scroller_w, scroller_h
            )
            self.ball = pygame.Rect(
                int(screen.get_width() / 2),
                y_scrol - b_diameter,
                b_diameter,
                b_diameter,
            )

            brick_make()

        def sx(x):
            screen = pygame.display.get_surface()
            scale = screen.get_width() / 1200
            x *= scale
            return x

        def brick_make():
            screen = pygame.display.get_surface()
            brick_w = round((screen.get_width()) / 10.7)
            brick_h = round((screen.get_height()) / 32)

            brick_start_pos_y = 70
            self.bricks_arr = []
            for i in range(7):
                brick_start_pos_x = \
                    (screen.get_width() - (brick_w + sx(10)) * 8) / 2
                for j in range(8):
                    self.bricks_arr.append(
                        pygame.Rect(
                            brick_start_pos_x, brick_start_pos_y,
                            brick_w, brick_h
                        )
                    )
                    brick_start_pos_x += brick_w + sx(10)
                brick_start_pos_y += brick_h + 5

        def draw_bricks():
            screen = pygame.display.get_surface()
            if self.shake > pygame.time.get_ticks():
                rand = (random() - 0.5) * 6, (random() - 0.5) * 6
            else:
                rand = 0, 0

            for brick in self.bricks_arr:
                pygame.draw.rect(
                    screen,
                    self.brick_col,
                    (brick.x + rand[0], brick.y + rand[1],
                     brick.width, brick.height),
                )

        def check_input():
            screen = pygame.display.get_surface()
            scroller_w = round((screen.get_width()) / 10.7)
            x_max_scrol = screen.get_width() - scroller_w
            while Gtk.events_pending():
                Gtk.main_iteration()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.pause = True
                        paused()
                    if event.key == pygame.K_LEFT:
                        self.keys_pressed[pygame.K_LEFT] = True
                    if event.key == pygame.K_RIGHT:
                        self.keys_pressed[pygame.K_RIGHT] = True

                    if event.key == pygame.K_c and \
                       self.state == self.ball_still:
                        if self.score > 150:
                            self.ball_vel = pygame.Vector2(10, -10)
                        elif self.score > 100:
                            self.ball_vel = pygame.Vector2(8, -8)
                        else:
                            self.ball_vel = pygame.Vector2(7, -7)
                        self.state = self.ball_play
                    elif event.key == pygame.K_n and (
                        self.state == self.ball_game_over or self.state == self.ball_won
                    ):
                        restart_game()
                    elif event.key == pygame.K_s:
                        settings()
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        quit()

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.keys_pressed[pygame.K_LEFT] = False
                    if event.key == pygame.K_RIGHT:
                        self.keys_pressed[pygame.K_RIGHT] = False

            if self.keys_pressed[pygame.K_LEFT]:
                self.paddle.left -= 12
                if self.paddle.left < 0:
                    self.paddle.left = 0

            if self.keys_pressed[pygame.K_RIGHT]:
                self.paddle.left += 12
                if self.paddle.left > x_max_scrol:
                    self.paddle.left = x_max_scrol

        def move_ball():
            screen = pygame.display.get_surface()
            scroller_w = round((screen.get_width()) / 10.7)
            b_diameter = round((scroller_w) / 3.75)
            x_max_ball = (screen.get_width() - sx(10)) - b_diameter
            y_max_ball = (screen.get_height() - 10) - b_diameter

            self.ball.left += self.ball_vel.x
            self.ball.top += self.ball_vel.y

            if self.ball.left <= 0:
                self.ball.left = 0
                self.ball_vel.x = -self.ball_vel.x
            elif self.ball.left >= x_max_ball:
                self.ball.left = x_max_ball
                self.ball_vel.x = -self.ball_vel.x

            if self.ball.top < 0:
                self.ball.top = 0
                self.ball_vel.y = -self.ball_vel.y
            elif self.ball.top >= y_max_ball:
                self.ball.top = y_max_ball
                self.ball_vel.y = -self.ball_vel.y

        def handle_collisions():
            screen = pygame.display.get_surface()
            scroller_w = round((screen.get_width()) / 10.7)
            scroller_h = round((screen.get_height()) / 40)
            b_diameter = round((scroller_w) / 3.75)
            y_scrol = (screen.get_height() - 10) - scroller_h - 70

            for brick in self.bricks_arr:
                if self.ball.colliderect(brick):
                    self.brick_hit_sound.play()
                    self.score += 1
                    self.bricks_arr.remove(brick)
                    self.shake = pygame.time.get_ticks() + 200
                    dr = abs(self.ball.right - brick.left)
                    dl = abs(self.ball.left - brick.right)
                    db = abs(self.ball.bottom - brick.top)
                    dt = abs(self.ball.top - brick.bottom)
                    if min(dl, dr) < min(dt, db):
                        self.ball_vel.x = -self.ball_vel.x
                    else:
                        self.ball_vel.y = -self.ball_vel.y
                    self.ball_vel.rotate_ip(random() * 10 - 5)
                    break

            if len(self.bricks_arr) == 0:
                self.state = self.ball_won

            if self.ball.colliderect(self.paddle):
                self.paddle_hit_sound.play()
                self.ball.top = y_scrol - b_diameter
                self.ball_vel.y = -self.ball_vel.y
                self.ball_vel.rotate_ip(random() * 10 - 5)
            elif self.ball.top > self.paddle.top:
                self.lives -= 1
                if self.lives > 0:
                    self.state = self.ball_still
                else:
                    self.state = self.ball_game_over

        def score_lives():
            screen = pygame.display.get_surface()
            medfont = pygame.font.Font("fonts/comicsansms.ttf", int(sx(30)))
            font_surface = medfont.render(
                "Score: " + str(self.score), True, self.brick_col
            )
            live_surface = medfont.render(
                "Lives left: " + str(self.lives), True, self.brick_col
            )
            screen.blit(font_surface, (sx(100), 5))
            screen.blit(
                live_surface,
                (
                    round(
                        screen.get_width() / 2 - live_surface.get_width() / 2
                    ),
                    5
                ),
            )
            pause_mess = medfont.render("Press P to pause", True,
                                        self.brick_col)
            screen.blit(
                pause_mess,
                (
                    round(
                        screen.get_width() - pause_mess.get_width() - sx(100)
                    ),
                    5
                )
            )

        def text_size(text, color, size):
            smallfont = pygame.font.Font("fonts/comicsansms.ttf", int(sx(30)))
            medfont = pygame.font.Font("fonts/comicsansms.ttf", int(sx(40)))
            largefont = pygame.font.Font("fonts/comicsansms.ttf", int(sx(70)))
            if size == "small":
                textSurf = smallfont.render(text, True, color)
            if size == "medium":
                textSurf = medfont.render(text, True, color)
            if size == "large":
                textSurf = largefont.render(text, True, color)

            return textSurf, textSurf.get_rect()

        def message_to_screen(msg, color, y_displace=100, size="small"):
            screen = pygame.display.get_surface()
            scale = screen.get_height() / 900

            textSur, textRect = text_size(msg, color, size)
            textRect.center = ((screen.get_width()) / 2), (
                (screen.get_height() - 50) / 2
            ) + y_displace * scale
            screen.blit(textSur, textRect)

        def unpause():
            global pause
            pygame.mixer.music.unpause()
            self.pause = False

        def draw_pause():
            screen = pygame.display.get_surface()
            screen.fill(self.back_col)
            message_to_screen("Paused", self.brick_col, 0, size="large")
            message_to_screen("Press P to continue", self.brick_col, 100,
                              size="medium")
            message_to_screen("Press N for a new game", self.brick_col, 170,
                              size="medium")
            message_to_screen("Press Q to quit", self.brick_col, 240,
                              size="medium")
            pygame.display.update()

        def paused():
            draw_pause()
            pygame.mixer.music.pause()
            self.pause = True
            while self.pause:
                while Gtk.events_pending():
                    Gtk.main_iteration()
                for event in pygame.event.get():
                    if event.type == pygame.VIDEORESIZE:
                        pygame.display.set_mode(event.size, pygame.RESIZABLE)
                        draw_pause()

                    if event.type == pygame.QUIT:
                        pygame.quit()
                        quit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_p:
                            unpause()
                        elif event.key == pygame.K_q:
                            pygame.quit()
                            quit()

                        elif event.key == pygame.K_n:
                            gameLoop()

        def draw_settings():
            screen = pygame.display.get_surface()
            screen.fill(self.yellow)
            message_to_screen("Settings", self.black, -400, size="large")
            message_to_screen("Press N to start a new game", self.black, -300,
                              size="medium")
            message_to_screen("Press Q to quit", self.black, -230,
                              size="medium")
            message_to_screen("Themes: ", self.black, -150, size="medium")
            message_to_screen("1. Classic ", self.black, -80, size="small")
            message_to_screen("2. Fresh and Bright ", self.black, -30,
                              size="small")
            message_to_screen("3. Professional ", self.black, 20, size="small")
            message_to_screen("4. Earthy ", self.black, 70, size="small")
            message_to_screen("5. Watery ", self.black, 120, size="small")
            message_to_screen("6. Natural ", self.black, 170, size="small")
            message_to_screen("7. Energetic ", self.black, 220, size="small")
            message_to_screen("8. Day and Night ", self.black, 270,
                              size="small")
            message_to_screen("9. Aqua Blues ", self.black, 320, size="small")
            message_to_screen("Press the theme number to select the theme ",
                              self.black, 370, size="medium")
            pygame.display.update()

        def settings():
            draw_settings()
            while True:
                while Gtk.events_pending():
                    Gtk.main_iteration()
                for event in pygame.event.get():
                    if event.type == pygame.VIDEORESIZE:
                        pygame.display.set_mode(event.size, pygame.RESIZABLE)
                        draw_settings()

                    if event.type == pygame.QUIT:
                        pygame.quit()
                        quit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_n:
                            gameLoop()
                        elif event.key == pygame.K_q:
                            pygame.quit()
                            quit()
                        else:
                            for i, key in enumerate(self.theme_keys):
                                if event.key == key:
                                    self.back_col = self.back_cols[i]
                                    self.brick_col = self.brick_cols[i]
                                    self.scroll_col = self.scroll_cols[i]
                                    gameLoop()
                                    break

        def gameLoop():
            screen = pygame.display.get_surface()
            scroller_w = round((screen.get_width()) / 10.7)
            b_diameter = round((scroller_w) / 3.75)

            pygame.display.update()
            restart_game()
            self.keys_pressed = {
                pygame.K_LEFT: False,
                pygame.K_RIGHT: False
            }
            while 1:
                self.clock.tick(50)
                screen.fill(self.back_col)
                check_input()
                draw_bricks()
                pygame.draw.rect(screen, self.scroll_col, self.paddle)
                pygame.draw.circle(
                    screen,
                    self.scroll_col,
                    (
                        self.ball.left + int(b_diameter / 2),
                        self.ball.top + int(b_diameter / 2),
                    ),
                    int(b_diameter / 2),
                )
                score_lives()
                if self.state == self.ball_play:
                    move_ball()
                    handle_collisions()
                elif self.state == self.ball_still:
                    self.ball.left = self.paddle.left + self.paddle.width / 2
                    self.ball.top = self.paddle.top - self.ball.height
                    message_to_screen(
                        "Press C to play", self.brick_col, 0, size="large"
                    )
                elif self.state == self.ball_game_over:
                    message_to_screen("Game Over", self.brick_col, 50,
                                      size="large")
                    message_to_screen("Press N for New Game", self.brick_col,
                                      150, size="medium")
                    message_to_screen("Press S for setting the theme",
                                      self.brick_col, 220, size="medium")
                    message_to_screen("Press Q to quit", self.brick_col, 290,
                                      size="medium")
                    pygame.mixer.music.stop()
                elif self.state == self.ball_won:
                    message_to_screen("You Won", self.brick_col, 50,
                                      size="large")
                    message_to_screen("Press N for New Game", self.brick_col,
                                      150, size="medium")
                    message_to_screen("Press S for setting the theme",
                                      self.brick_col, 220, size="medium")
                    message_to_screen("Press Q to quit", self.brick_col, 290,
                                      size="medium")
                    pygame.mixer.music.stop()

                pygame.display.update()

        #####################################################################
        pygame.init()
        pygame.display.set_mode((0, 0), pygame.RESIZABLE)
        screen = pygame.display.get_surface()

        def draw_welcome():
            screen.fill(self.yellow)
            message_to_screen("Welcome to Ball and Brick", [0, 0, 0], -100,
                              size="large")
            message_to_screen("Press C to start the game", self.green, 0,
                              size="medium")
            message_to_screen("Press S for setting the theme", self.green, 70,
                              size="medium")
            message_to_screen("Press Q to quit the game", self.red, 140,
                              size="medium")
            pygame.display.flip()
            self.clock.tick(10)

        draw_welcome()
        while True:
            while Gtk.events_pending():
                Gtk.main_iteration()
            for event in pygame.event.get():
                if event.type == pygame.VIDEORESIZE:
                    pygame.display.set_mode(event.size, pygame.RESIZABLE)
                    draw_welcome()

                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        gameLoop()
                    elif event.key == pygame.K_s:
                        settings()
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        quit()
            self.clock.tick(10)


def main():
    pygame.init()
    pygame.display.set_mode((0, 0), pygame.RESIZABLE)
    game = BallAndBrick()
    game.run()


if __name__ == "__main__":
    main()
