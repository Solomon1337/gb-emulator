import sdl2
import sdl2.ext
import sdl2.ext.draw


class Graphic():
    def __init__(self, width=256, height=256):
        sdl2.ext.init()

        self.window = sdl2.ext.Window(title="Gameboy", size=(width, height))

        self.renderer = sdl2.ext.Renderer(self.window,
                logical_size = (width, height),
                flags = sdl2.SDL_RENDERER_ACCELERATED |
                        sdl2.SDL_RENDERER_PRESENTVSYNC)

    def pump_events(self, display):
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                raise StopIteration("SDL quit")
            elif event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == ord('t'):
                    if display.tile_window.shown:
                        display.tile_window.hide()
                    else:
                        display.tile_window.show()

    def put(self, x, y, color):
        self.renderer.draw_point((x,y), color)

    def show(self):
        self.window.show()

    def hide(self):
        self.window.hide()

    def update(self):
        self.renderer.present()

    def clear(self, color):
        self.renderer.clear(color)

    def box(self, x, y, w, h):
        c = 0x00cc44
        self.renderer.draw_line([x,y,x+w,y,x+w,y+h,x,y+h,x,y], c)

    def put_pixels(self, positions, color):
        self.renderer.draw_point(positions, color)
