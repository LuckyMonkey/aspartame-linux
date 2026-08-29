# -*- coding: utf-8 -*-

import os
import math
import cairo
import logging

import gi
gi.require_version('PangoCairo', '1.0')
from gi.repository import Gtk, Gdk, GObject
from gi.repository import Pango
from gi.repository import PangoCairo

from sugar3.activity import activity
from sugar3.graphics.icon import _IconBuffer
from sugar3.graphics import style

ANCHO_LINEAS_CONTROLES = 2
SIZE_RESIZE_AREA = style.GRID_CELL_SIZE // 2

DIR_ABAJO = "abajo"
DIR_ARRIBA = "arriba"
DIR_IZQ = "izq"
DIR_DER = "der"

DEFAULT_FONT = 'Sans'
DEFAULT_GLOBE_WIDTH = style.GRID_CELL_SIZE * 1.5
DEFAULT_GLOBE_HEIGHT = style.GRID_CELL_SIZE // 2


def _get_screen_dpi():
    xft_dpi = Gtk.Settings.get_default().get_property('gtk-xft-dpi')
    dpi = float(xft_dpi // 1024)
    return dpi


def _set_screen_dpi():
    dpi = _get_screen_dpi()
    font_map_default = PangoCairo.font_map_get_default()
    font_map_default.set_resolution(dpi)


_set_screen_dpi()


class Globo:

    def __init__(self, box, x, y, ancho=DEFAULT_GLOBE_WIDTH,
                 alto=DEFAULT_GLOBE_HEIGHT, modo="normal",
                 direccion=DIR_ABAJO, font_name=DEFAULT_FONT):

        self.globe_type = "GLOBE"
        self.box = box
        # determina tamanio minimo
        self.radio = 30
        # dimensiones de la elipse
        self.ancho = ancho
        self.alto = alto
        self.punto = [ancho / 2, alto * 2]
        # determina si esta seleccionado
        # TODO: make private
        self.selec = False
        self.direccion = direccion
        # 2 tipos de globos: "normal" o "despacio"
        self.modo = modo
        # Centro de la elipse
        self.x = x * self.ancho / (self.radio * 1.0)
        self.y = y * self.alto / (self.radio * 1.0)

        ancho_text, alto_text = self.calc_area_texto(self.ancho, self.alto)
        # es el contenedor del texto
        self.texto = CuadroTexto(self, ancho_text, alto_text,
                                 font_name)

    def set_selected(self, selected):
        logging.debug('Set selected %s (%s)', selected, self.texto.text)
        self.selec = selected
        if self.texto is not None:
            if selected and self.texto.get_edition_mode():
                # if already is in edit mode, do nothing
                return
            self.texto.set_edition_mode(selected)

    def imprimir(self, context):
        # dibujo al globo de dialogo

        context.save()

        context.set_line_width(2)
        scale_x = self.ancho / (self.radio * 1.0)
        scale_y = self.alto / (self.radio * 1.0)

        context.scale(scale_x, scale_y)

        x = self.x / scale_x
        y = self.y / scale_y

        if self.direccion == DIR_ABAJO:

            context.arc(x, y, self.radio, 100 / (180.0) * math.pi,
                        80 / (180.0) * math.pi)
            context.line_to(
                x + self.punto[0] / scale_x,
                y + self.radio + self.punto[1] / scale_y)

        elif self.direccion == DIR_DER:
            context.arc(x, y, self.radio,
                        10 / 180.0 * math.pi, 350 / 180.0 * math.pi)
            context.line_to(x + self.radio + self.punto[0] / scale_x,
                            y + self.punto[1] / scale_y)

        elif self.direccion == DIR_IZQ:
            context.arc(x, y, self.radio, 190 / 180.0 * math.pi,
                        530 / 180.0 * math.pi)
            context.line_to(x - self.radio - self.punto[0] / scale_x,
                            y + self.punto[1] / scale_y)

        else:
            context.arc(x, y, self.radio,
                        280 / 180.0 * math.pi, 620 / 180.0 * math.pi)
            context.line_to(
                x + self.punto[0] / scale_x,
                y - self.radio -
                self.punto[1] / scale_y)

        context.close_path()
        context.set_source_rgb(1, 1, 1)
        context.fill_preserve()
        context.set_source_rgb(0, 0, 0)
        if self.modo != "normal":
            context.set_dash([2])
        context.stroke()
        context.restore()

        # se dibuja el correspondiente texto
        if self.texto is not None:
            self.texto.imprimir(context)
        self.dibujar_controles(context)

    def dibujar_controles(self, context):

        # si esta seleccionado se dibujan los controles
        if self.selec:
            context.save()
            context.set_line_width(ANCHO_LINEAS_CONTROLES)

            x = self.x * self.radio / (self.ancho * 1.0)

            # rectangulo alrededor del globo
            context.set_source_rgb(1, 1, 1)
            context.rectangle(self.x - self.ancho, self.y - self.alto,
                              2 * self.ancho, 2 * self.alto)
            context.stroke_preserve()
            context.set_source_rgb(0, 0, 0)
            context.set_dash([2])
            context.stroke()
            context.restore()

            # cuadrado esquina superior izq
            context.save()
            context.set_line_width(ANCHO_LINEAS_CONTROLES)
            context.set_source_rgb(1, 1, 1)
            context.rectangle(self.x - self.ancho - (SIZE_RESIZE_AREA // 2),
                              self.y - self.alto - (SIZE_RESIZE_AREA // 2),
                              SIZE_RESIZE_AREA, SIZE_RESIZE_AREA)
            context.stroke_preserve()
            context.set_source_rgb(0, 0, 0)
            context.set_dash([2])
            context.stroke()
            context.restore()

            # circulo en la punta del globo
            context.save()
            context.set_line_width(ANCHO_LINEAS_CONTROLES)
            context.set_source_rgb(1, 1, 1)

            x_circle, y_circle = self.get_circle_position()
            context.arc(x_circle, y_circle,
                        (SIZE_RESIZE_AREA / 2), 0, x * math.pi)
            context.stroke_preserve()
            context.set_source_rgb(0, 0, 0)
            context.set_dash([2])
            context.stroke()
            context.restore()

    def get_circle_position(self):
        if self.direccion == DIR_ABAJO:
            return self.x + self.punto[0], self.y + self.alto + self.punto[1]
        elif self.direccion == DIR_DER:
            return self.x + self.ancho + self.punto[0], self.y + self.punto[1]
        elif self.direccion == DIR_IZQ:
            return self.x - self.ancho - self.punto[0], self.y + self.punto[1]
        else:
            return self.x + self.punto[0], self.y - self.alto - self.punto[1]

    def mover_a(self, x, y, rect):
        if self.dx + x > (self.ancho):
            if self.dx + x < (rect.width - self.ancho):
                self.x = self.dx + x
            else:
                self.x = rect.width - self.ancho
        else:
            self.x = self.ancho

        if self.dy + y > (self.alto):
            if self.dy + y < (rect.height - self.alto):
                self.y = self.dy + y
            else:
                self.y = rect.height - self.alto
        else:
            self.y = self.alto

        if self.texto is not None:
            self.texto.mover_a(self.x, self.y)

    def get_cursor_type(self, x, y):
        cursor = None
        sensibility = 2
        if abs((self.x - self.ancho) - x) < sensibility:
            cursor = Gdk.CursorType.LEFT_SIDE
            if abs((self.y - self.alto) - y) < sensibility:
                cursor = Gdk.CursorType.TOP_LEFT_CORNER
            if abs((self.y + self.alto) - y) < sensibility:
                cursor = Gdk.CursorType.BOTTOM_LEFT_CORNER
        elif abs((self.x + self.ancho) - x) < sensibility:
            cursor = Gdk.CursorType.RIGHT_SIDE
            if abs((self.y - self.alto) - y) < sensibility:
                cursor = Gdk.CursorType.TOP_RIGHT_CORNER
            if abs((self.y + self.alto) - y) < sensibility:
                cursor = Gdk.CursorType.BOTTOM_RIGHT_CORNER
        elif abs((self.y - self.alto) - y) < sensibility:
            cursor = Gdk.CursorType.TOP_SIDE
        elif abs((self.y + self.alto) - y) < sensibility:
            cursor = Gdk.CursorType.BOTTOM_SIDE
        return cursor

    def is_selec(self, x, y):
        # devuelve True si es seleccionado
        if (self.x - self.ancho) < x < (self.x + self.ancho) and \
                (self.y - self.alto) < y < (self.y + self.alto):

            self.selec = True
            if self.texto is not None:
                self.texto.mostrar_cursor = True

            # Obtiene la posicion donde se selecciono con el mouse
            self.dx = self.x - x
            self.dy = self.y - y
            return True
        else:
            # self.selec=False
            return False

    def is_selec_tam(self, x, y):
        width = SIZE_RESIZE_AREA // 2
        if self.x - self.ancho - width < x < self.x - self.ancho + width and \
                self.y - self.alto - width < y < self.y - self.alto + width:
            return True
        else:
            return False

    def is_selec_punto(self, x, y):
        width = SIZE_RESIZE_AREA // 2
        x_circle, y_circle = self.get_circle_position()
        return x_circle - width < x < x_circle + width and \
            y_circle - width < y < y_circle + width

    def mover_punto(self, x, y, rect):
        if self.direccion == DIR_ABAJO:
            if 0 < x < rect.width:
                self.punto[0] = x - self.x
            elif x <= 0:
                self.punto[0] = - self.x
            else:
                self.punto[0] = rect.width - self.x

            if self.y + self.alto < y < rect.height:
                self.punto[1] = y - (self.y + self.alto)
            elif self.y + self.alto >= y:
                self.punto[1] = 0
            else:
                self.punto[1] = rect.height - (self.y + self.alto)

        elif self.direccion == DIR_DER:
            if self.x + self.ancho < x < rect.width:
                self.punto[0] = x - (self.x + self.ancho)
            elif self.x + self.ancho >= x:
                self.punto[0] = 0
            else:
                self.punto[0] = rect.width - (self.x + self.ancho)

            if 0 < y < rect.height:
                self.punto[1] = y - self.y
            elif self.y + self.alto >= y:
                self.punto[1] = - self.y
            else:
                self.punto[1] = rect.height - self.y

        elif self.direccion == DIR_IZQ:
            if 0 < x < self.x - self.ancho:
                self.punto[0] = (self.x - self.ancho) - x
            elif self.x - self.ancho <= x:
                self.punto[0] = 0
            else:
                self.punto[0] = self.x - self.ancho

            if 0 < y < rect.height:
                self.punto[1] = y - self.y
            elif self.y + self.alto >= y:
                self.punto[1] = - self.y
            else:
                self.punto[1] = rect.height - self.y

        else:
            if 0 < x < rect.width:
                self.punto[0] = x - self.x
            elif x <= 0:
                self.punto[0] = - self.x
            else:
                self.punto[0] = rect.width - self.x

            if 0 < y < self.y - self.alto:
                self.punto[1] = (self.y - self.alto) - y
            elif self.y - self.alto <= y:
                self.punto[1] = 0
            else:
                self.punto[1] = (self.y - self.alto)

    def set_dimension(self, x, y, rect):
        # set the text in edition mode to use the textview
        # to meassure the minimal size needed
        if self.texto is not None:
            self.texto.set_edition_mode(True)

        # if I am changing the size from the right or from the bottom
        # change x / y to calculate like if changing from
        # top and left
        if x > self.x:
            x = 2 * self.x - x
        if y > self.y:
            y = 2 * self.y - y

        if (2 * self.x - x) < rect.width:
            if 0 < x < (self.x - self.radio):
                new_width = self.x - x
            elif x <= 0:
                new_width = self.x
            else:
                new_width = self.radio

        elif self.x - self.ancho != 0:
            new_width = rect.width - self.x

        if (2 * self.y - y) < rect.height:
            if 0 < y < (self.y - self.radio):
                new_height = self.y - y
            elif y <= 0:
                new_height = self.y
            else:
                new_height = self.radio
        elif self.y - self.alto != 0:
            new_height = rect.height - self.y

        # try resize the text object
        if self.texto is not None:
            ancho_text, alto_text = self.calc_area_texto(new_width, new_height)
            self.texto.set_dimension(ancho_text, alto_text)
        else:
            # if there are not text object, the size can be changed
            self.ancho = new_width
            self.alto = new_height

    def calc_area_texto(self, width, height):
        """
        Calculate the size available to the text, based in the globe size
        """
        ancho_text = width - 12 * width / (self.radio * 1.0)
        alto_text = height - 12 * height / (self.radio * 1.0)
        return (ancho_text, alto_text)

    def calc_area(self, ancho_text, alto_text):
        """
        Calculate the min globe size, based in the text size
        """
        if self.texto is not None:
            self.ancho = self.texto.ancho / (1 - 12 / (self.radio * 1.0))
            self.alto = self.texto.alto / (1 - 12 / (self.radio * 1.0))

    def girar(self):
        if (self.__class__ == Rectangulo):
            return False

        if (self.direccion == DIR_ABAJO):
            self.direccion = DIR_IZQ

        elif (self.direccion == DIR_IZQ):
            self.direccion = DIR_ARRIBA

        elif (self.direccion == DIR_ARRIBA):
            self.direccion = DIR_DER

        elif (self.direccion == DIR_DER):
            self.direccion = DIR_ABAJO
        self.punto[0], self.punto[1] = self.punto[1], self.punto[0]

        if (self.__class__ == Imagen):
            self.ancho, self.alto = self.alto, self.ancho

        return True


class Rectangulo(Globo):

    def __init__(self, box, x, y, ancho=DEFAULT_GLOBE_WIDTH,
                 alto=DEFAULT_GLOBE_HEIGHT / 2,
                 font_name=DEFAULT_FONT):

        self.globe_type = "RECTANGLE"
        self.box = box
        # determina tamanio minimo
        self.radio = 15
        # dimensiones del rectangulo
        self.ancho = ancho
        self.alto = alto
        self.punto = None
        self.direccion = None
        self.selec = False

        # Centro del rectangulo
        self.x = x
        self.y = y

        ancho_text, alto_text = self.calc_area_texto(self.ancho, self.alto)
        self.texto = CuadroTexto(self, ancho_text, alto_text,
                                 font_name)

    def imprimir(self, context):
        # imprimimos el rectangulo
        context.set_line_width(3)
        context.rectangle(self.x - self.ancho, self.y - self.alto,
                          2 * self.ancho, 2 * self.alto)
        context.set_source_rgb(1, 1, 1)
        context.fill_preserve()
        context.set_source_rgb(0, 0, 0)
        context.stroke()

        # se dibuja el correspondiente texto
        self.texto.imprimir(context)
        self.dibujar_controles(context)

    def dibujar_controles(self, context):
        # Si esta seleccionado pintamos un recuadro alrededor del globo
        # y un par de controles
        if self.selec:
            context.save()
            context.set_line_width(ANCHO_LINEAS_CONTROLES)
            context.set_source_rgb(1, 1, 1)
            context.rectangle(self.x - self.ancho - 2, self.y - self.alto - 2,
                              2 * self.ancho + 4, 2 * self.alto + 4)
            context.stroke_preserve()
            context.set_source_rgb(0, 0, 0)
            context.set_dash([2])
            context.stroke()

            context.set_source_rgb(1, 1, 1)
            context.rectangle(
                self.x - self.ancho - (SIZE_RESIZE_AREA // 2),
                self.y - self.alto - (SIZE_RESIZE_AREA // 2),
                SIZE_RESIZE_AREA, SIZE_RESIZE_AREA)
            context.stroke_preserve()
            context.set_source_rgb(0, 0, 0)
            context.set_dash([2])
            context.stroke()
            context.restore()

    def mover_punto(self, x, y, rect):
        pass

    def is_selec_punto(self, x, y):
        return False

    def calc_area_texto(self, width, height):
        ancho_text = width - 5
        alto_text = height - 5
        return (ancho_text, alto_text)

    def calc_area(self, ancho_text, alto_text):
        self.ancho = self.texto.ancho + 5
        self.alto = self.texto.alto + 5


class Nube(Globo):

    def __init__(self, box, x, y, ancho=DEFAULT_GLOBE_WIDTH,
                 alto=DEFAULT_GLOBE_HEIGHT, direccion=DIR_ABAJO,
                 font_name=DEFAULT_FONT):

        self.globe_type = "CLOUD"
        self.radio = 30
        self.box = box

        # dimensiones de la elipse
        self.ancho = ancho
        self.alto = alto

        self.punto = [ancho // 2, alto * 2]
        # determina si esta seleccionado
        self.selec = False

        self.direccion = direccion

        self.x = x
        self.y = y

        ancho_text, alto_text = self.calc_area_texto(self.ancho, self.alto)
        self.texto = CuadroTexto(self, ancho_text, alto_text,
                                 font_name)

    def imprimir(self, context):

        self.draw(context)

        x_circle, y_circle = self.get_second_circle_position()

        context.arc(x_circle, y_circle, 7, 0, 2 * math.pi)
        context.set_source_rgb(1, 1, 1)
        context.fill_preserve()
        context.set_source_rgb(0, 0, 0)
        context.stroke()

        x_circle, y_circle = self.get_circle_position()
        context.arc(x_circle, y_circle, 5, 0, 2 * math.pi)
        context.set_source_rgb(1, 1, 1)
        context.fill_preserve()
        context.set_source_rgb(0, 0, 0)
        context.stroke()

        # se dibuja el correspondiente texto
        self.texto.imprimir(context)

        self.dibujar_controles(context)

    def draw(self, cr):

        x_cen = self.x
        y_cen = self.y

        steps = 36

        ancho_int = self.ancho * 0.8
        alto_int = self.alto * 0.8

        x = x_cen + self.ancho
        y = y_cen
        cr.move_to(x, y)

        state = 0

        for i in range(steps):
            alpha = 2.0 * i * (math.pi / steps)
            sinalpha = math.sin(alpha)
            cosalpha = math.cos(alpha)

            if state == 0:
                x1 = x_cen + (1.0 * self.ancho * cosalpha)
                y1 = y_cen + (1.0 * self.alto * sinalpha)
            elif state == 1:
                x2 = x_cen + (1.0 * self.ancho * cosalpha)
                y2 = y_cen + (1.0 * self.alto * sinalpha)
            elif state == 2:
                x3 = x_cen + (1.0 * ancho_int * cosalpha)
                y3 = y_cen + (1.0 * alto_int * sinalpha)

            if state == 2:
                cr.curve_to(x1, y1, x2, y2, x3, y3)

            state += 1
            if state == 3:
                state = 0

        x1 = x_cen + (1.0 * self.ancho * cosalpha)
        y1 = y_cen + (1.0 * self.alto * sinalpha)
        x2 = x_cen + (1.0 * self.ancho)
        y2 = y_cen
        x3 = x_cen + (1.0 * self.ancho)
        y3 = y_cen
        cr.curve_to(x1, y1, x2, y2, x3, y3)

        cr.set_source_rgb(1, 1, 1)
        cr.fill_preserve()
        cr.set_source_rgba(0, 0, 0, 1)
        cr.set_line_width(4)
        cr.stroke()

    def get_circle_position(self):
        if self.direccion == DIR_ABAJO:
            return self.x + self.punto[0], self.y + self.alto + self.punto[1]
        elif self.direccion == DIR_DER:
            return self.x + self.ancho + self.punto[0], self.y + self.punto[1]
        elif self.direccion == DIR_IZQ:
            return self.x - self.ancho - self.punto[0], self.y + self.punto[1]
        else:
            return self.x + self.punto[0], self.y - self.alto - self.punto[1]

    def get_second_circle_position(self):
        if self.direccion == DIR_ABAJO:
            return self.x + self.punto[0] // 2, \
                self.y + self.alto + self.punto[1] // 2
        elif self.direccion == DIR_DER:
            return self.x + self.ancho + self.punto[0] / 2, \
                self.y + self.punto[1] // 2
        elif self.direccion == DIR_IZQ:
            return self.x - self.ancho - self.punto[0] // 2, \
                self.y + self.punto[1] // 2
        else:
            return self.x + self.punto[0] // 2, \
                self.y - self.alto - self.punto[1] / 2


class Grito(Globo):

    def __init__(self, box, x, y, ancho=DEFAULT_GLOBE_WIDTH,
                 alto=DEFAULT_GLOBE_HEIGHT, direccion=DIR_ABAJO,
                 font_name=DEFAULT_FONT):

        self.globe_type = "EXCLAMATION"
        self.radio = 30
        self.box = box

        self.ancho = ancho
        self.alto = alto

        self.punto = [ancho // 2, alto * 2]
        self.selec = False

        self.direccion = direccion

        self.x = x
        self.y = y

        ancho_text, alto_text = self.calc_area_texto(self.ancho, self.alto)
        self.texto = CuadroTexto(self, ancho_text, alto_text,
                                 font_name)

    def imprimir(self, context):
        self.draw_exclamation(context, self.x, self.y, self.ancho, self.alto,
                              self.direccion, self.punto)
        # se dibuja el correspondiente texto
        self.texto.imprimir(context)
        self.dibujar_controles(context)

    def draw_exclamation(self, cr, x_cen, y_cen, width, height, direction,
                         punto):

        steps = 24

        width_int = width * 0.8
        height_int = height * 0.8

        x = x_cen + width
        y = y_cen
        cr.move_to(x, y)

        for i in range(steps):
            alpha = 2.0 * i * (math.pi / steps)
            sinalpha = math.sin(alpha)
            cosalpha = math.cos(alpha)

            if i % 2 > 0:
                x = x_cen + (1.0 * width_int * cosalpha)
                y = y_cen + (1.0 * height_int * sinalpha)
            else:
                x = x_cen + (1.0 * width * cosalpha)
                y = y_cen + (1.0 * height * sinalpha)

            if (direction == DIR_ABAJO and i == 6) or \
               (direction == DIR_DER and i == 0) or \
               (direction == DIR_IZQ and i == 12) or \
               (direction == DIR_ARRIBA and i == 18):

                if direction == DIR_ABAJO:
                    x = x_cen + punto[0]
                    y = y_cen + height + punto[1]
                elif direction == DIR_DER:
                    x = x_cen + width + punto[0]
                    y = y_cen + punto[1]
                elif direction == DIR_IZQ:
                    x = x_cen - width - punto[0]
                    y = y_cen + punto[1]
                else:
                    x = x_cen + punto[0]
                    y = y_cen - height - punto[1]

            cr.line_to(x, y)
        cr.close_path()
        cr.set_source_rgb(1, 1, 1)
        cr.fill_preserve()
        cr.set_source_rgba(0, 0, 0, 1)
        cr.set_line_width(4)
        cr.stroke()

    def calc_area_texto(self, width, height):
        ancho_text = width - 12 * width / (self.radio * 1.0)
        alto_text = height - 20 * height / (self.radio * 1.0)
        return (ancho_text, alto_text)


class Imagen(Globo):

    def __init__(self, box, imagen, x, y, ancho=50, alto=30,
                 direccion=DIR_ABAJO, font_name=DEFAULT_FONT):

        self.globe_type = "IMAGE"
        self.box = box
        self.radio = 30
        self.ancho = ancho
        self.alto = alto
        self.image_name = imagen

        self.selec = False

        self.x = x
        self.y = y
        self.direccion = direccion
        self.punto = [0, 0]  # fake, but needed for persistence

        appdir = os.path.join(activity.get_bundle_path())
        self.icon_buffer = _IconBuffer()
        self.icon_buffer.file_name = os.path.join(appdir, imagen)
        self.icon_buffer.stroke_color = '#000000'
        self.texto = None

    def set_selected(self, selected):
        self.selec = selected

    def imprimir(self, context):

        context.save()

        if self.direccion in (DIR_ARRIBA, DIR_ABAJO):
            self.icon_buffer.width = self.ancho * 2
            self.icon_buffer.height = self.alto * 2
        else:
            self.icon_buffer.width = self.alto * 2
            self.icon_buffer.height = self.ancho * 2

        surface = self.icon_buffer.get_surface()
        x = self.x - surface.get_width() // 2
        y = self.y - surface.get_height() // 2

        context.translate(x, y)

        if self.direccion != DIR_ABAJO:
            if self.direccion == DIR_ARRIBA:
                context.rotate(3.14)  # 180 degrees
                context.translate(-self.icon_buffer.width,
                                  -self.icon_buffer.height)

            elif self.direccion == DIR_IZQ:
                context.rotate(3.14 / 2.0)  # 90 degrees
                context.translate(
                    (self.icon_buffer.height - self.icon_buffer.width) // 2,
                    -(self.icon_buffer.width + self.icon_buffer.height) // 2)

            elif self.direccion == DIR_DER:
                context.rotate(3.0 * 3.14 / 2.0)  # 270 degrees
                context.translate(
                    -(self.icon_buffer.height + self.icon_buffer.width) // 2,
                    (self.icon_buffer.width - self.icon_buffer.height) // 2)

        context.set_source_surface(surface, 0, 0)

        context.paint()
        context.restore()

        # si esta seleccionado se dibujan los controles
        if self.selec:
            context.set_line_width(ANCHO_LINEAS_CONTROLES)
            context.set_source_rgb(1, 1, 1)
            context.rectangle(self.x - self.ancho, self.y - self.alto,
                              2 * self.ancho, 2 * self.alto)
            context.stroke_preserve()
            context.set_source_rgb(0, 0, 0)
            context.set_dash([2])
            context.stroke()

    def calc_area_texto(self, width, height):
        return (20, 20)

    def calc_area(self, ancho_text, alto_text):
        pass

    def mover_punto(self, x, y, rect):
        pass

    def is_selec_punto(self, x, y):
        return False


class CuadroTexto:

    "Es un cuadro de texto con alineacion centralizada"

    def __init__(self, globe, ancho=50, alto=30, font_name=DEFAULT_FONT):

        # Ancho del cuadro = 2*self.ancho
        self._globe = globe
        self._box = globe.box
        self.ancho = ancho
        self.alto = alto

        self.text = ''

        # Caracteristicas de la tipografia
        self.font_description = '%s 10' % font_name
        self.bold = False
        self.italic = False
        self.color = (0, 0, 0)
        self.font_size = '10'
        self.font_type = font_name
        self._in_edition = False

        # image surface used to draw the text
        self._text_surface = None

        # textview
        self.textviewbox = Gtk.VBox()
        self.textview = Gtk.TextView()
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.textview.set_justification(Gtk.Justification.CENTER)
        self.textview.modify_bg(Gtk.StateType.NORMAL,
                                style.COLOR_WHITE.get_gdk_color())
        self._textview_x = 0
        self._textview_y = 0
        self._box.fixed.put(self.textviewbox, 0, 0)
        self.textviewbox.pack_start(self.textview, True, False, 0)
        self.textviewbox.connect(
            'size_allocate', self._textview_size_allocate)

        # avoid race condition between imprimir and _finalize_text methods
        self.set_dimension(self.ancho, self.alto)

    def move_textview(self, x, y):
        if self._textview_x != x or self._textview_y != y:
            self._textview_x = x
            self._textview_y = y
            self._box.fixed.move(self.textviewbox, x, y)
            self.textviewbox.show_all()

    def set_font_description(self, fd, parse=True):
        self.font_description = fd
        if self._in_edition:
            self.textview.modify_font(Pango.FontDescription(fd))
        if parse:
            self._parse_font_description()

    def get_edition_mode(self):
        return self._in_edition

    def set_edition_mode(self, in_edition):
        if self._in_edition == in_edition:
            return
        self._in_edition = in_edition
        tbuffer = self.textview.get_buffer()
        if self._in_edition:
            self.textview.set_cursor_visible(True)

            self.textview.modify_font(Pango.FontDescription(
                self.font_description))
            self.set_dimension(self.ancho, self.alto)

            self.mover_a(self._globe.x, self._globe.y)
            self.textviewbox.show_all()
            self.textview.grab_focus()
        else:
            start, end = tbuffer.get_start_iter(), tbuffer.get_end_iter()
            self.text = tbuffer.get_text(start, end, True)
            self.textview.set_cursor_visible(False)
            # need wait until the cursor is hidden
            GObject.idle_add(self._finalize_text)

    def _finalize_text(self):
        alloc = Gdk.Rectangle()
        alloc.width = self.ancho * 2
        alloc.height = self.alto * 2

        self._text_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                                alloc.width,
                                                alloc.height)
        context = cairo.Context(self._text_surface)

        self.textview.size_allocate(alloc)
        self.textview.draw(context)

        self._box.redraw()

    def initialize_textview(self, ctx):
        tbuffer = self.textview.get_buffer()
        tbuffer.set_text(self.text)
        self.textview.set_cursor_visible(False)
        self.textview.modify_font(Pango.FontDescription(
            self.font_description))
        self.set_dimension(self.ancho, self.alto)
        self.mover_a(self._globe.x, self._globe.y)
        self.textviewbox.show_all()
        GObject.idle_add(self._finalize_text)

    def imprimir(self, ctx):
        self._update_font()

        x = self._globe.x - self.ancho
        y = self._globe.y - self.alto

        if not self._in_edition:
            if self._text_surface is None:
                self.initialize_textview(ctx)
            else:
                ctx.save()
                ctx.set_source_surface(self._text_surface, x, y)
                ctx.paint()
                ctx.restore()
        else:
            ctx.save()
            ctx.translate(x, y)
            self.textview.draw(ctx)
            ctx.restore()

    def mover_a(self, x, y):
        "Mueve el centro del cuadro a la posicion (x,y)"
        x = self._globe.x - self.ancho
        y = self._globe.y - self.alto
        self.move_textview(x, y)

    def set_text(self, text):
        self.text = text
        self._box.redraw()

    def set_dimension(self, ancho, alto):
        """
        Establece las dimensiones del cuadro siendo
        el ancho del cuadro = 2*ancho
        y el alto del cuadro=2*alto
        """
        self.ancho = ancho
        self.alto = alto
        self.textview.set_size_request(self.ancho * 2,
                                       self.alto * 2)

    def _textview_size_allocate(self, widget, alloc):
        # recalculate size and position with the real size allocated
        self.ancho = alloc.width // 2
        self.alto = alloc.height // 2

        self._globe.calc_area(self.ancho, self.alto)
        x = self._globe.x - self.ancho
        y = self._globe.y - self.alto
        self.move_textview(x, y)

    def _update_font(self):
        fd = self.font_type

        if self.italic:
            fd += ' italic'

        if self.bold:
            fd += ' bold'

        fd += ' %s' % self.font_size

        if fd != self.font_description:
            self.set_font_description(fd, False)

        self.textview.modify_fg(Gtk.StateType.NORMAL,
                                Gdk.Color(*self.color))

    def _parse_font_description(self):
        fd = self.font_description.split()

        self.font_type = fd[0]
        self.font_size = fd[-1]
        self.bold = 'bold' in fd
        self.italic = 'italic' in fd
