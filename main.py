import os, subprocess, random, configparser
from functools import partial


from kivy.config import Config
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen

Config.set('kivy', 'keyboard_mode', 'systemanddock')

if os.name=='posix':
    import RPi.GPIO as GPIO
    Config.set('graphics', 'fullscreen', 'auto')
    Config.set('graphics', 'borderless', '1')
else:
    import RPi_test.GPIO as GPIO

import kivy
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.properties import ListProperty,StringProperty,NumericProperty,ColorProperty,OptionProperty,BooleanProperty,ObjectProperty
from kivy.graphics import Rectangle, Color, Line, Bezier
from kivy.graphics import RoundedRectangle
from kivy.uix.screenmanager import SlideTransition,RiseInTransition,CardTransition,WipeTransition,FadeTransition
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.audio import SoundLoader
import time
from os import system

config_path = r'config/fowl.ini'
gray_seperator_line=r'media/line_gray.png'

_music=[
    'audio/music/bossa-in-my-heart-13187.mp3',
    'audio/music/brazil-music-football-carnival-samba-festival-background-intro-theme-260573.mp3',
    'audio/music/carnival-in-bahia-samba-112197.mp3',
    'audio/music/carnival-of-souls-238569.mp3',
    'audio/music/carnival-ride-178900.mp3',
    'audio/music/circus-145017.mp3',
    'audio/music/cute-loot-carnival-246079.mp3',
    'audio/music/festive-joyful-carnival-vibes-232018.mp3',
    'audio/music/joyful-carnival-trumpet-232017.mp3',
    'audio/music/when-the-circus-comes-to-town-accordian-203353.mp3',
    'audio/music/whimsical-fun-slapstick-carnival-226124.mp3',
    'audio/music/world-asian-carnival-china-traditional-music-travel-118593.mp3'
]
music=_music.copy()
start_gong:SoundLoader=SoundLoader.load('audio/effects/single-church-bell-156463.mp3')
end_buzzer=SoundLoader.load('audio/effects/buzzerwav-14908.mp3')
_sound_effects=[
    'audio/effects/an_ominous-crow-call-255173.mp3',
    'audio/effects/an-angry-bird-215811.mp3',
    'audio/effects/baby-chicks-chirp-40102.mp3',
    'audio/effects/bird-3-c-106170.mp3',
    'audio/effects/bird-3-e-106168.mp3',
    'audio/effects/bird-3-f-89236.mp3',
    'audio/effects/bird-call-38512.mp3',
    'audio/effects/chicken-noise-228106.mp3',
    'audio/effects/chicken-single-alarm-call-6056.mp3',
    'audio/effects/cyborg-bird-fx-11483.mp3',
    'audio/effects/door-bell-bird-101898.mp3',
    'audio/effects/duck-quack-112941.mp3',
    'audio/effects/eagle-scream-112940.mp3',
    'audio/effects/krucifix-productions-extinct-bird-chirp-47159.mp3',
    'audio/effects/metal-crunch-263638.mp3',
    'audio/effects/metal-impact-247482.mp3',
    'audio/effects/metal-whoosh-hit-4-201906.mp3',
    'audio/effects/metal-whoosh-hit-9-201909.mp3',
    'audio/effects/owl-hooting-48028.mp3',
    'audio/effects/pigeon-82804.mp3',
    'audio/effects/rooster-cry-173621.mp3',
    'audio/effects/seagull-noise-254410.mp3',
    'audio/effects/short-chick-sound-171389.mp3',
    'audio/effects/sword-hit-7160.mp3'

]
sound_effects=_sound_effects.copy()

def loop_music(*args):
    global music
    if not music:
        music=_music.copy()
    random.shuffle(music)
    sound=SoundLoader.load(music.pop())
    sound.play()
    sound.bind(on_stop=loop_music)
    # Clock.schedule_once(loop_music, sound.length)

class Logic:
    def __init__(self) -> None:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)

        self.target25=8
        self.target50=10
        self.target200=11

        GPIO.setup(self.target25,GPIO.IN,pull_up_down = GPIO.PUD_DOWN)
        GPIO.setup(self.target50,GPIO.IN,pull_up_down = GPIO.PUD_DOWN)
        GPIO.setup(self.target200,GPIO.IN,pull_up_down = GPIO.PUD_DOWN)

        self.active_targets={
            '25':0,
            '50':0,
            '200':0
        }

    def update(self,*args):
        self.active_targets['25']=GPIO.input(self.target25)
        self.active_targets['50']=GPIO.input(self.target50)
        self.active_targets['200']=GPIO.input(self.target200)


logic=Logic()

'''<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>'''


class RoundedButton(Button):
    def __init__(self,**kwargs):
        super(RoundedButton,self).__init__(**kwargs)
        self.bg_color=kwargs["background_color"]
        self.background_color = (self.bg_color[0], self.bg_color[1], self.bg_color[2], 0)  # Invisible background color to regular button

        with self.canvas.before:
            if self.background_normal=="":
                self.shape_color = Color(self.bg_color[0], self.bg_color[1], self.bg_color[2], self.bg_color[3])
            if self.background_down=="":
                self.shape_color = Color(self.bg_color[0]*.5, self.bg_color[1]*.5, self.bg_color[2]*.5, self.bg_color[3])
            self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
            self.bind(pos=self.update_shape, size=self.update_shape,state=self.color_swap)

    def update_shape(self, *args):
        self.shape.pos = self.pos
        self.shape.size = self.size
    def color_swap(self,*args):
        if self.state=="normal":
            if self.background_normal=="":
                self.shape_color.rgba = self.bg_color[0], self.bg_color[1], self.bg_color[2], self.bg_color[3]
            else:
                self.shape_color.rgba = self.bg_color[0]*.5, self.bg_color[1]*.5, self.bg_color[2]*.5, self.bg_color[3]
        if self.state=="down":
            if self.background_down=="":
                self.shape_color.rgba = self.bg_color[0], self.bg_color[1], self.bg_color[2], self.bg_color[3]
            else:
                self.shape_color.rgba = self.bg_color[0]*.5, self.bg_color[1]*.5, self.bg_color[2]*.5, self.bg_color[3]

class WallPaper(Image):
    sources=[
        r'media/360_F_314940210_PKr0mARBpExzn1iK63yphwgGezf3FzqU.jpg',
        r'media/Funny_Rubber_Chickens.jpg',
        r'media/images.jpg',
        r'media/scream.jpg',
        r'media/glass.jpg',
        r'media/grafitti.jpg',
        r'media/pixels.jpg',
        r'media/face_down.jpg',
        r'media/tessallated.jpg',
        r'media/soup.jpg',
        r'media/reading.jpg',
        r'media/doof.jpg',
        r'media/choir.jpg'
    ]

    def __init__(self, **kwargs):
        super(WallPaper,self).__init__(**kwargs)
        self.size_hint=(1,1)
        self.pos_hint={'x':0,'y':0}
        self.change_image()
        Clock.schedule_interval(self.change_image,5)

    def change_image(self,*args):
        rc=random.choice(self.sources)
        while rc==self.source:
            rc=random.choice(self.sources)
        self.source=rc

class RoundedLabelColor(Label):
    bg_color=ColorProperty()
    def __init__(self,bg_color= (.1,.1,.1,.95),**kwargs):
        super(RoundedLabelColor,self).__init__(**kwargs)
        self.bg_color=bg_color


        with self.canvas.before:
            self.shape_color = Color(*self.bg_color)
            self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
            self.bind(pos=self.update_shape, size=self.update_shape)

    def update_shape(self, *args):
        self.shape.pos = self.pos
        self.shape.size = self.size

    def on_bg_color(self, *args):
        #before __init__ is called the bg_color changes, so we wait untill __init__() to proceed
        if hasattr(self,'shape_color'):
            self.shape_color.rgb=self.bg_color

class RoundedColorLayout(FloatLayout):
    bg_color=ColorProperty()
    def __init__(self,bg_color= (.1,.1,.1,.95),**kwargs):
        super(RoundedColorLayout,self).__init__(**kwargs)
        self.bg_color=bg_color

        with self.canvas:#.before:
            self.shape_color = Color(*self.bg_color)
            self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
            self.bind(pos=self.update_shape, size=self.update_shape)

    def update_shape(self, *args):
        self.shape.pos = self.pos
        self.shape.size = self.size

class ExpandableRoundedColorLayout(ButtonBehavior,RoundedColorLayout):

    expanded=BooleanProperty(defaultvalue=False)
    animating=BooleanProperty(defaultvalue=False)

    def __init__(self,**kwargs):
        self._expanded=False
        self.original_pos=kwargs['pos_hint']
        self.original_size=kwargs['size_hint']
        if 'locked' in kwargs:
            self.locked=self._lock_callback=kwargs.pop('locked')
        if 'expanded_pos' in kwargs:
            self.expanded_pos=kwargs.pop('expanded_pos')
        if 'expanded_size' in kwargs:
            self.expanded_size=kwargs.pop('expanded_size')
        if 'modal_dim' in kwargs:
            self.modal_dim=kwargs.pop('modal_dim')
            Clock.schedule_once(self._set_modal_dim)
            self._apply_dim=Animation(rgba=self.modal_dim)
            self._remove_dim=Animation(rgba=(0,0,0,0),d=.2)
        self.move_anim=Animation(pos_hint=self.expanded_pos,d=.15,t='in_out_quad')
        self.move_anim.bind(on_complete=self.set_expanded_true)
        self.return_anim=Animation(pos_hint=self.original_pos,d=.15,t='out_back')
        self.return_anim.bind(on_complete=self.set_expanded_false)
        self.grow_anim=Animation(size_hint=self.expanded_size,d=.15,t='in_out_quad')
        self.grow_anim.bind(on_complete=self.set_expanded_true)
        self.shrink_anim=Animation(size_hint=self.original_size,d=.15,t='out_back')
        self.shrink_anim.bind(on_complete=self.set_expanded_false)
        super(ExpandableRoundedColorLayout,self).__init__(**kwargs)

    def lock(self,*args):
        self.locked=self._lock_callback

    def unlock(self,*args):
        if hasattr(self,'locked'):
            del self.locked

    def _set_modal_dim(self,*args):
        with self.canvas.before:
            self._dim=Color(0,0,0,0)
            self._dim_rect=Rectangle(size=Window.size)

    # def on_touch_down(self, touch):
    #     if not self._expanded:
    #         pass
    #     elif not self.collide_point(*touch.pos):
    #         self.shrink()
    #         super(ExpandableRoundedColorLayout,self).on_touch_down(touch)
    #         return True
    #     return super(ExpandableRoundedColorLayout,self).on_touch_down(touch)

    def on_release(self,*args):
        if hasattr(self,'locked'):
            self.locked(self.expand)
            return
        self.expand()

    def shrink(self,*args):
        if self._expanded:
            Animation.stop_all(self)
            self.animating=not self.animating
            self._expanded=False
            self.shrink_anim.start(self)
            self.return_anim.start(self)

    def expand(self,*args):
        if not self._expanded:
            Animation.stop_all(self)
            self.animating=not self.animating
            parent=self.parent
            parent.remove_widget(self)
            parent.add_widget(self)
            self._expanded=True
            if hasattr(self,'expanded_size'):
                self.grow_anim.start(self)
            if hasattr(self, 'expanded_pos'):
                self.move_anim.start(self)

    def set_expanded_true(self,*args):
        self.expanded=True
        if hasattr(self,'modal_dim'):
            self._remove_dim.cancel_all(self._dim)
            self._apply_dim.start(self._dim)
            self._dim_rect.size=Window.size

    def set_expanded_false(self,*args):
        self.expanded=False
        if hasattr(self,'modal_dim'):
            self._apply_dim.cancel_all(self._dim)
            self._remove_dim.start(self._dim)

class RoundedColorLayoutModal(FloatLayout):
    bg_color=ColorProperty()
    def __init__(self,bg_color= (.1,.1,.1,.95),**kwargs):
        super(RoundedColorLayoutModal,self).__init__(**kwargs)
        self.bg_color=bg_color

        with self.canvas:
            self.shape_color = Color(*self.bg_color)
            self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
            self.bind(pos=self.update_shape, size=self.update_shape)

    def update_shape(self, *args):
        self.shape.pos = self.pos
        self.shape.size = self.size

class MinimumBoundingLabel(Label):
    def __init__(self, **kwargs):
        super(MinimumBoundingLabel,self).__init__(**kwargs)
        self.size_hint=(None,None)
    #uncomment to see bounding boxes
    #     with self.canvas.before:
    #         self.colour = Color(1,0,1,1)
    #         self.rect = Rectangle(size=self.size, pos=self.pos)

    #     self.bg_color=(1,0,1,1)
    #     self.bind(size=self._update_rect, pos=self._update_rect)

    # def _update_rect(self, instance, *args):
    #     self.rect.pos = instance.pos
    #     self.rect.size = instance.size

    # def on_bg_color(self, *args):
    #     self.colour.rgb=self.bg_color

    def on_texture_size(self,*args):
        self.size=self.texture_size

class PinLock(RoundedColorLayoutModal):
    end_point_one=ListProperty([])
    end_point_two=ListProperty([])
    def __init__(self,**kwargs):
        super(PinLock,self).__init__(bg_color=(.15,.15,.15,1),**kwargs)
        self.widgets={}
        self.pin=[]
        self.entry_slots={
            1:None,
            2:None,
            3:None}
        self.size_hint=(.9,.9)
        self.pos_hint={'center_x':.5,'center_y':.5}

        title=Label(
            text='[size=80][color=#ffffff][b]Chicken-Scratch Some Initials',
            markup=True,
            size_hint =(.4, .05),
            pos_hint = {'center_x':.5, 'center_y':.925},)
        self.widgets['title']=title
        title.ref='title'

        seperator=Image(
            source=gray_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.9, .005),
            pos_hint = {'x':.05, 'y':.85})
        self.widgets['seperator']=seperator

        entry_one=MinimumBoundingLabel(
            text='[size=80][b]-',
            markup=True,
            size_hint =(.15, .15),
            pos_hint = {'center_x':.4, 'center_y':.75},)
        self.widgets['entry_one']=entry_one
        self.entry_slots[1]=entry_one

        entry_two=MinimumBoundingLabel(
            text='[size=80][b]-',
            markup=True,
            size_hint =(.15, .15),
            pos_hint = {'center_x':.5, 'center_y':.75},)
        self.widgets['entry_two']=entry_two
        self.entry_slots[2]=entry_two

        entry_three=MinimumBoundingLabel(
            text='[size=80][b]-',
            markup=True,
            size_hint =(.15, .15),
            pos_hint = {'center_x':.6, 'center_y':.75},)
        self.widgets['entry_three']=entry_three
        self.entry_slots[3]=entry_three

        num_pad=FloatLayout(size_hint =(1, .65),
            pos_hint = {'center_x':.5, 'y':0})
        self.widgets['num_pad']=num_pad

        l_a=RoundedButton(text="[size=35][b][color=#000000] A [/color][/b][/size]",
            size_hint =(.09, .15),
            pos_hint = {'x':.005, 'y':.8},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        l_a.value='A'
        self.widgets['l_a']=l_a
        l_a.bind(on_release=self.entry_func)

        l_b=RoundedButton(text="[size=35][b][color=#000000] B [/color][/b][/size]",
            size_hint =(.09, .15),
            pos_hint = {'x':.105, 'y':.8},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        l_b.value='B'
        self.widgets['l_b']=l_b
        l_b.bind(on_release=self.entry_func)

        l_c=RoundedButton(text="[size=35][b][color=#000000] C [/color][/b][/size]",
            size_hint =(.09, .15),
            pos_hint = {'x':.205, 'y':.8},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        l_c.value='C'
        self.widgets['l_c']=l_c
        l_c.bind(on_release=self.entry_func)

        l_d=RoundedButton(text="[size=35][b][color=#000000] D [/color][/b][/size]",
            size_hint =(.09, .15),
            pos_hint = {'x':.305, 'y':.8},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        l_d.value='D'
        self.widgets['l_d']=l_d
        l_d.bind(on_release=self.entry_func)

        l_e=RoundedButton(text="[size=35][b][color=#000000] E [/color][/b][/size]",
            size_hint =(.09, .15),
            pos_hint = {'x':.405, 'y':.8},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        l_e.value='E'
        self.widgets['l_e']=l_e
        l_e.bind(on_release=self.entry_func)

        l_f=RoundedButton(text="[size=35][b][color=#000000] F [/color][/b][/size]",
            size_hint =(.09, .15),
            pos_hint = {'x':.505, 'y':.8},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        l_f.value='F'
        self.widgets['l_f']=l_f
        l_f.bind(on_release=self.entry_func)

        l_g=RoundedButton(text="[size=35][b][color=#000000] G [/color][/b][/size]",
            size_hint =(.09, .15),
            pos_hint = {'x':.605, 'y':.8},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        l_g.value='G'
        self.widgets['l_g']=l_g
        l_g.bind(on_release=self.entry_func)

        l_h=RoundedButton(text="[size=35][b][color=#000000] H [/color][/b][/size]",
            size_hint =(.09, .15),
            pos_hint = {'x':.705, 'y':.8},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        l_h.value='H'
        self.widgets['l_h']=l_h
        l_h.bind(on_release=self.entry_func)

        l_i=RoundedButton(text="[size=35][b][color=#000000] I [/color][/b][/size]",
            size_hint =(.09, .15),
            pos_hint = {'x':.805, 'y':.8},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        l_i.value='I'
        self.widgets['l_i']=l_i
        l_i.bind(on_release=self.entry_func)

        l_j=RoundedButton(text="[size=35][b][color=#000000] J [/color][/b][/size]",
            size_hint =(.09, .15),
            pos_hint = {'x':.905, 'y':.8},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        l_j.value='J'
        self.widgets['l_j']=l_j
        l_j.bind(on_release=self.entry_func)

        l_k=RoundedButton(text="[size=35][b][color=#000000] K [/color][/b][/size]",
            size_hint =(.09, .15),
            pos_hint = {'x':.05, 'y':.63},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        l_k.value='K'
        self.widgets['l_k']=l_k
        l_k.bind(on_release=self.entry_func)

        l_l=RoundedButton(text="[size=35][b][color=#000000] L [/color][/b][/size]",
            size_hint =(.09, .15),
            pos_hint = {'x':.15, 'y':.63},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        l_l.value='L'
        self.widgets['l_l']=l_l
        l_l.bind(on_release=self.entry_func)

        l_m=RoundedButton(text="[size=35][b][color=#000000] M [/color][/b][/size]",
            size_hint =(.09, .15),
            pos_hint = {'x':.25, 'y':.63},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        l_m.value='M'
        self.widgets['l_m']=l_m
        l_m.bind(on_release=self.entry_func)

        l_n=RoundedButton(text="[size=35][b][color=#000000] N [/color][/b][/size]",
            size_hint =(.09, .15),
            pos_hint = {'x':.35, 'y':.63},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        l_n.value='N'
        self.widgets['l_n']=l_n
        l_n.bind(on_release=self.entry_func)

        l_o=RoundedButton(text="[size=35][b][color=#000000] O [/color][/b][/size]",
            size_hint =(.09, .15),
            pos_hint = {'x':.45, 'y':.63},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        l_o.value='O'
        self.widgets['l_o']=l_o
        l_o.bind(on_release=self.entry_func)

        l_p=RoundedButton(text="[size=35][b][color=#000000] P [/color][/b][/size]",
            size_hint =(.09, .15),
            pos_hint = {'x':.55, 'y':.63},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        l_p.value='P'
        self.widgets['l_p']=l_p
        l_p.bind(on_release=self.entry_func)

        l_q=RoundedButton(text="[size=35][b][color=#000000] Q [/color][/b][/size]",
            size_hint =(.09, .15),
            pos_hint = {'x':.65, 'y':.63},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        l_q.value='Q'
        self.widgets['l_q']=l_q
        l_q.bind(on_release=self.entry_func)

        l_r=RoundedButton(text="[size=35][b][color=#000000] R [/color][/b][/size]",
            size_hint =(.09, .15),
            pos_hint = {'x':.75, 'y':.63},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        l_r.value='R'
        self.widgets['l_r']=l_r
        l_r.bind(on_release=self.entry_func)

        l_s=RoundedButton(text="[size=35][b][color=#000000] S [/color][/b][/size]",
            size_hint =(.09, .15),
            pos_hint = {'x':.85, 'y':.63},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        l_s.value='S'
        self.widgets['l_s']=l_s
        l_s.bind(on_release=self.entry_func)

        l_t=RoundedButton(text="[size=35][b][color=#000000] T [/color][/b][/size]",
            size_hint =(.09, .15),
            pos_hint = {'x':.1, 'y':.46},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        l_t.value='T'
        self.widgets['l_t']=l_t
        l_t.bind(on_release=self.entry_func)

        l_u=RoundedButton(text="[size=35][b][color=#000000] U [/color][/b][/size]",
            size_hint =(.09, .15),
            pos_hint = {'x':.2, 'y':.46},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        l_u.value='U'
        self.widgets['l_u']=l_u
        l_u.bind(on_release=self.entry_func)

        l_v=RoundedButton(text="[size=35][b][color=#000000] V [/color][/b][/size]",
            size_hint =(.09, .15),
            pos_hint = {'x':.3, 'y':.46},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        l_v.value='V'
        self.widgets['l_v']=l_v
        l_v.bind(on_release=self.entry_func)

        l_w=RoundedButton(text="[size=35][b][color=#000000] W [/color][/b][/size]",
            size_hint =(.09, .15),
            pos_hint = {'x':.4, 'y':.46},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        l_w.value='W'
        self.widgets['l_w']=l_w
        l_w.bind(on_release=self.entry_func)

        l_x=RoundedButton(text="[size=35][b][color=#000000] X [/color][/b][/size]",
            size_hint =(.09, .15),
            pos_hint = {'x':.5, 'y':.46},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        l_x.value='X'
        self.widgets['l_x']=l_x
        l_x.bind(on_release=self.entry_func)

        l_y=RoundedButton(text="[size=35][b][color=#000000] Y [/color][/b][/size]",
            size_hint =(.09, .15),
            pos_hint = {'x':.6, 'y':.46},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        l_y.value='Y'
        self.widgets['l_y']=l_y
        l_y.bind(on_release=self.entry_func)

        l_z=RoundedButton(text="[size=35][b][color=#000000] Z [/color][/b][/size]",
            size_hint =(.09, .15),
            pos_hint = {'x':.7, 'y':.46},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        l_z.value='Z'
        self.widgets['l_z']=l_z
        l_z.bind(on_release=self.entry_func)

        backspace=RoundedButton(text="[size=35][b][color=#000000] Del [/color][/b][/size]",
            size_hint =(.09, .15),
            pos_hint = {'x':.8, 'y':.46},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        self.widgets['backspace']=backspace
        backspace.bind(on_release=self.backspace_func)

        enter=RoundedButton(text="[size=80][b][color=#000000] Enter\n[size=40](Count Your Eggs, They've Hatched!) [/color][/b][/size]",
            size_hint =(.75, .33),
            pos_hint = {'center_x':.5, 'y':.11},
            background_down='',
            background_color=(100/255, 255/255, 100/255,.85),
            markup=True,
            halign='center')
        self.widgets['enter']=enter
        enter.bind(on_release=self.enter_func)

        self.add_widget(title)
        self.add_widget(seperator)
        self.add_widget(entry_one)
        self.add_widget(entry_two)
        self.add_widget(entry_three)
        self.add_widget(num_pad)
        num_pad.add_widget(l_a)
        num_pad.add_widget(l_b)
        num_pad.add_widget(l_c)
        num_pad.add_widget(l_d)
        num_pad.add_widget(l_e)
        num_pad.add_widget(l_f)
        num_pad.add_widget(l_g)
        num_pad.add_widget(l_h)
        num_pad.add_widget(l_i)
        num_pad.add_widget(l_j)
        num_pad.add_widget(l_k)
        num_pad.add_widget(l_l)
        num_pad.add_widget(l_m)
        num_pad.add_widget(l_n)
        num_pad.add_widget(l_o)
        num_pad.add_widget(l_p)
        num_pad.add_widget(l_q)
        num_pad.add_widget(l_r)
        num_pad.add_widget(l_s)
        num_pad.add_widget(l_t)
        num_pad.add_widget(l_u)
        num_pad.add_widget(l_v)
        num_pad.add_widget(l_w)
        num_pad.add_widget(l_x)
        num_pad.add_widget(l_y)
        num_pad.add_widget(l_z)
        num_pad.add_widget(backspace)
        num_pad.add_widget(enter)


    def entry_func(self,button):
        if len(self.pin)>=3:
            return
        val=button.value
        self.pin.append(val)
        for i,v in enumerate(self.pin):
            self.entry_slots[i+1].text=f'[size=80][b]{v}'

    def backspace_func(self,button):
        if len(self.pin)<1:
            return
        del self.pin[-1]
        self.entry_slots[len(self.pin)+1].text='[size=80][b]-'

    def enter_func(self,button):
        if len(self.pin)<3:
            return
        pin=''.join(str(x) for x in self.pin)
        self.pin_to_set=pin
        self.pin=[]
        self.clear_with_success()

    def clear_with_success(self,*args):
        self.check_one_start=[self.center_x-500,self.center_y-250]
        self.check_one_end  =[self.center_x,self.center_y-625]
        self.check_two_start=[self.center_x,self.center_y-625]
        self.check_two_end  =[self.center_x+500,self.center_y+375]
        fade=Animation(opacity=0,d=.25)
        fade.start(self.widgets['num_pad'])
        for i in self.entry_slots.values():
            fade.start(i)
        with self.canvas.after:
            Color(0,1,0)
            self.check_one=Line(width=3)
            self.check_two=Line(width=3)
        self.end_point_one=self.check_one_start
        self.end_point_two=self.check_two_start
        down=Animation(end_point_one=self.check_one_end,d=.25,t='out_sine')
        down+=Animation(end_point_two=self.check_two_end,d=.25,t='in_cubic')
        down.start(self)
        self.schedule_clear()

    def on_end_point_one(self,*args):
        points = self.check_one_start
        points.extend(self.end_point_one)

        # remove the old line
        self.canvas.after.remove(self.check_one)

        # draw the updated line
        with self.canvas.after:
            self.check_one = Line(points=points, width=3)

    def on_end_point_two(self,*args):
        if self.end_point_one!=self.check_one_end:
            return
        points = self.check_two_start
        points.extend(self.end_point_two)

        # remove the old line
        self.canvas.after.remove(self.check_two)

        # draw the updated line
        with self.canvas.after:
            self.check_two = Line(points=points, width=3)

    def schedule_clear(self,*args):
        Clock.schedule_once(self.save_initials,.85)

    def save_initials(self,*args):
        root=App.get_running_app()
        b=root.sm.get_screen('brag')
        b.initials=self.pin_to_set
        b.save_score()
        root.sm.transition = FadeTransition()
        root.sm.current='scores'

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
        super(PinLock, self).on_touch_down(touch)
        return True

    def on_touch_up(self, touch):
        if not self.collide_point(*touch.pos):
            return
            if touch.grab_current is self:
                touch.ungrab(self)
            self.clear()
        super(PinLock, self).on_touch_up(touch)
        return True

class InsultLabel(Label):
    def __init__(self, **kwargs):
        super(InsultLabel,self).__init__(**kwargs)
        self.markup=True
        self.size_hint=(1,.8)
        self.pos_hint={'center_x':.5,'center_y':.4}
        self.text=self.generate_insult()

    def generate_insult(self,*args):
        markup='[b][size=150][color=#000000]'
        insults=[
            'You lay eggs like a rooster!',
            'You achieved a poultry score!',
            'Chicken soup can\'t save you!',
            'You\'re a fowl player!',
            'What a scrambled attempt!',
            'Not so harboiled now!',
            'You\'re one egg short of a dozen!',
            'That round was a yolk!',
            'Maybe you could win the chicken dance.',
            'Ugly duckling award.',
            'A score like chicken feathers, its down!',
            'The trick is don\'t throw like a chick.',
            'You couldn\t hit the broadside of a barn.'
        ]
        return markup+random.choice(insults)


#<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>#



class MainScreen(Screen):
    def __init__(self, **kw):
        super(MainScreen,self).__init__(**kw)
        self.widgets={}
        self.event_log={}
        self.time_remaining=60
        self.paused=False
        self.round_score=130
        self.last_score=0
        Clock.schedule_interval(self.get_score,.01)
        self.playing=False

        bg_image=WallPaper(allow_stretch=True,keep_ratio=False)

        score_button=RoundedButton(
            text='[b][size=30]High Score:',
            size_hint =(.35, .2),
            pos_hint = {'center_x':.2, 'center_y':.85},
            background_normal='',
            background_color=(.5, .35, .7,.95),
            markup=True,
            halign='center')
        self.widgets['score_button']=score_button
        score_button.bind(on_release=self.score_func)

        last_score_label=RoundedLabelColor(
            text='[b][size=30][color=#000000]Last Round Score: ',
            markup=True,
            size_hint =(.3, .1),
            pos_hint = {'center_x':.5, 'center_y':.1},
            bg_color=(.85, .85, .7,.95))
        self.widgets['last_score_label']=last_score_label

        start_button=RoundedButton(
            text='[b][size=90][color=#000000]Start Round, You Chicken!',
            size_hint =(.9, .3),
            pos_hint = {'center_x':.5, 'center_y':.4},
            background_normal='',
            background_color=(247/255, 136/255, 25/255,.9),
            markup=True)
        self.widgets['start_button']=start_button
        start_button.bind(on_release=self.timer_box_expand_button_func)
        start_anim=Animation(pos_hint={'center_x':.5, 'center_y':.45},t='out_quart')
        start_anim+=Animation(pos_hint={'center_x':.5, 'center_y':.35},t='in_quart')
        start_anim.repeat=True
        start_anim.start(start_button)

        timer_box=ExpandableRoundedColorLayout(
            size_hint =(.35, .2),
            pos_hint = {'center_x':.8, 'center_y':.85},
            expanded_size=(.9,.9),
            expanded_pos = {'center_x':.5, 'center_y':.5},
            bg_color=(151/255, 247/255, 25/255,.9),
            modal_dim=(0,0,0,.975))
        self.widgets['timer_box']=timer_box
        timer_box.widgets={}
        timer_box.bind(state=self.bg_color)
        timer_box.bind(expanded=self.timer_box_populate)
        timer_box.bind(animating=lambda *x,**_x:timer_box.clear_widgets())

        timer_box_title=Label(
            text='[b][size=100][color=#000000][i]1:00',
            markup=True,
            size_hint =(1, 1),
            pos_hint = {'center_x':.5, 'center_y':.5},)
        self.widgets['timer_box_title']=timer_box_title

        count_down=Label(
            text='[b][size=150][color=#000000][i]1:00',
            markup=True,
            size_hint =(.4, .15),
            pos_hint = {'center_x':.5, 'center_y':.9},)
        self.widgets['count_down']=count_down

        round_label=Label(
            text='[b][size=250][i]0',
            markup=True,
            size_hint =(.8, .75),
            pos_hint = {'center_x':.5, 'center_y':.55},)
        self.widgets['round_label']=round_label

        pause_button=RoundedButton(
            text='[b][size=70]Pause',
            size_hint =(.35, .2),
            pos_hint = {'center_x':.25, 'center_y':.15},
            background_normal='',
            background_color=(247/255, 136/255, 125/255,.9),
            markup=True)
        self.widgets['pause_button']=pause_button
        pause_button.bind(on_release=self.pause_func)

        quit_button=RoundedButton(
            text='[b][size=70]Quit, BAWK!',
            size_hint =(.35, .2),
            pos_hint = {'center_x':.75, 'center_y':.15},
            background_normal='',
            background_color=(.5, .35, .7,.95),
            markup=True)
        self.widgets['quit_button']=quit_button
        quit_button.bind(on_release=self.quit_func)

        timer_box.add_widget(timer_box_title)
        self.add_widget(bg_image)
        self.add_widget(score_button)
        self.add_widget(start_button)
        self.add_widget(timer_box)
        self.add_widget(last_score_label)

    def timer_box_expand_button_func(self,*args):
        tb=self.widgets['timer_box']
        if tb.expanded:
            tb.shrink()
        if not tb.expanded:
            tb.expand()

    def timer_box_populate(self,*args):
        darken=Animation(rgba=(151/255, 247/255, 25/255,1))
        lighten=Animation(rgba=(151/255, 247/255, 25/255,.9))
        timer_box=self.widgets['timer_box']
        timer_box.clear_widgets()
        if timer_box.expanded:
            for i in logic.active_targets.values():
                i=0
            self.round_score=0
            self.time_remaining=60
            self.remove_widget(timer_box)
            self.add_widget(timer_box)#needed to draw children on top
            darken.start(timer_box.shape_color)
            self.start_count_down_clock()
            w=self.widgets
            w['round_label'].pos_hint = {'center_x':.5, 'center_y':.55}
            all_widgets=[
                w['count_down'],
                w['round_label'],
                w['pause_button'],
                w['quit_button']
                ]
            for i in all_widgets:
                timer_box.add_widget(i)
        elif not timer_box.expanded:
            lighten.start(timer_box.shape_color)
            w=self.widgets
            all_widgets=[
                w['timer_box_title']]
            for i in all_widgets:
                timer_box.add_widget(i)

    def start_count_down_clock(self,*args):
        start_gong.play()
        # to auto increment score for testing uncomment line below.
        # self.event_log['count_down']=Clock.schedule_interval(lambda *args:setattr(logic,'active_targets',{'25':1,'50':0,'200':0}),.1)
        self.playing=True
        timer_box=self.widgets['timer_box']
        self.widgets['count_down'].text=f'[b][size=150][color=#000000][i]{self.time_remaining}'
        def update_time(*args):
            self.time_remaining-=1
            if self.time_remaining==40:
                Animation(rgba=(247/255, 203/255, 25/255,1)).start(timer_box.shape_color)
            if self.time_remaining==20:
                Animation(rgba=(247/255, 121/255, 25/255,1)).start(timer_box.shape_color)
            if self.time_remaining==10:
                Animation(rgba=(247/255, 29/255, 25/255,1)).start(timer_box.shape_color)
            if self.time_remaining==5:
                Animation(rgba=(1,1,1,1)).start(timer_box.shape_color)
            if self.time_remaining<=4:
                Animation(rgba=(247/255, 29/255, 25/255,1)).start(timer_box.shape_color)
            if self.time_remaining<=0:
                self.game_over()
            self.widgets['count_down'].text=f'[b][size=150][color=#000000][i]{self.time_remaining}'
        self.event_log['count_down']=Clock.schedule_interval(update_time,1)

    def stop_count_down_clock(self,*args):
        self.widgets['count_down'].text=f'[b][size=150][color=#000000][i]Paused    {self.time_remaining}    Paused'
        Clock.unschedule(self.event_log['count_down'])

    def bg_color(self,button,*args):
        if hasattr(button,'expanded'):
            if button.expanded:
                return
        if button.state=='normal':
            button.shape_color.rgba=(151/255, 247/255, 25/255,.9)
        if button.state=='down':
            button.shape_color.rgba=(151/350, 247/350, 25/350,.9)

    def game_over(self,*args):
        end_buzzer.play()
        self.preserve_last_round(self.round_score)
        Clock.unschedule(self.event_log['count_down'])
        self.time_remaining=0
        self.playing=False
        w=self.widgets
        tb=w['timer_box']
        all_widgets=[
            w['count_down'],
            w['pause_button'],
            w['quit_button']]
        for i in all_widgets:
            tb.remove_widget(i)
        Animation(pos_hint={'center_x':.5, 'center_y':.85},d=.75,t='out_expo').start(w['round_label'])
        if self.check_score():
            tb.add_widget(Label(
                size_hint=(1,1),
                pos_hint={'x':0,'y':0},
                text='[b][size=200]NICE!\nNICE!\nNICE!',
                markup=True))
            Clock.schedule_once(self.get_initials,5)
        else:
            tb.add_widget(InsultLabel())
            Clock.schedule_once(self.timer_box_expand_button_func,5)

    def get_score(self,*args):
        if self.paused or not self.playing:
            return
        for target,hit in logic.active_targets.items():
            if hit:
                audio=SoundLoader.load(random.choice(sound_effects))
                audio.play()
                self.round_score+=int(target)
            hit = 0
        self.widgets['round_label'].text='[b][size=250][i]'+str(self.round_score)



    def check_score(self,*args):
        config=App.get_running_app()._config
        config.read(config_path)
        scores=config['scores'].values()
        for i in scores:
            if int(i)<self.round_score:
                App.get_running_app().sm.get_screen('brag').score=self.round_score
                return True

    def get_initials(self,*args):
        App.get_running_app().sm.transition = FadeTransition()
        App.get_running_app().sm.current='brag'
        self.timer_box_expand_button_func()

    def pause_func(self,*args):
        if self.paused:
            self.widgets['pause_button'].text='[b][size=70]Pause'
            self.start_count_down_clock()
        else:
            self.widgets['pause_button'].text='[b][size=70]Resume'
            self.stop_count_down_clock()
        self.paused = not self.paused

    def quit_func(self,*args):
        self.timer_box_expand_button_func()
        self.stop_count_down_clock()
        self.widgets['pause_button'].text='[b][size=70]Pause'
        self.paused = False
        self.time_remaining=60
        self.round_score=0

    def score_func(self,*args):
        App.get_running_app().sm.transition = FadeTransition()
        App.get_running_app().sm.current='scores'

    def load_score(self,*args):
        hs=self.widgets['score_button']
        config=App.get_running_app()._config
        config.read(config_path)
        initial=config.get('initials','first')
        score=config.get('scores','first')
        hs.text=f'[b][size=30][u]          High Score          [/u]\n[i][size=80]{initial} {score}'

    def preserve_last_round(self,score,*args):
        self.widgets['last_score_label'].text=f'[b][size=30][color=#000000]Last Round Score: {score}'


    def on_pre_enter(self, *args):
        self.load_score()
        return super(MainScreen,self).on_pre_enter(*args)

class ScoreScreen(Screen):
    def __init__(self, **kw):
        super(ScoreScreen,self).__init__(**kw)
        self.widgets={}

        bg_image=WallPaper(allow_stretch=True,keep_ratio=False)

        back_button=RoundedButton(
            text='[b][size=40]Back to the Chicken Coop',
            size_hint =(.6, .15),
            pos_hint = {'center_x':.5, 'y':.015},
            background_down='',
            background_color=(200/250, 200/250, 200/250,.85),
            markup=True)
        self.widgets['back_button']=back_button
        back_button.bind(on_release=self.back_func)

        score_sheet=RoundedLabelColor(
            bg_color=(.5, .35, .7,.95),
            text='[b][size=40]Score',
            markup=True,
            halign='center',
            size_hint =(.85, .8),
            pos_hint = {'center_x':.5, 'center_y':.585})
        self.widgets['score_sheet']=score_sheet

        self.add_widget(bg_image)
        self.add_widget(back_button)
        self.add_widget(score_sheet)

    def back_func(self,*args):
        App.get_running_app().sm.transition = FadeTransition()
        App.get_running_app().sm.current='main'

    def load_scores(self,*args):
        ss=self.widgets['score_sheet']
        config=App.get_running_app()._config
        config.read(config_path)
        initials=config['initials'].values()
        scores=config['scores'].values()
        mashed_scores=sorted(list(zip(initials,scores)),key=lambda x: int(x[1]),reverse=True)
        scores=[str(' '*15 + i[0] + ' '*35 + i[1]+ ' '*15) for i in mashed_scores]

        markup='[b][size=50][u]'
        _prepared_scores=''.join(markup+i+'\n' for i in scores)
        _prepared_scores=_prepared_scores.strip('\n')
        ss.text=_prepared_scores

    def on_pre_enter(self, *args):
        self.load_scores()
        return super(ScoreScreen,self).on_pre_enter(*args)

class BragScreen(Screen):
    def __init__(self, **kw):
        super(BragScreen,self).__init__(**kw)
        self.widgets={}
        self.score=0
        self.initials=''

        self.bg_image=WallPaper(allow_stretch=True,keep_ratio=False)

    def save_score(self,*args):
        config=App.get_running_app()._config
        config.read(config_path)
        initials=config['initials'].values()
        scores=config['scores'].values()
        mixed_list=list(zip(initials,scores))
        mixed_list.append((self.initials,str(self.score)))
        mashed_scores=sorted(mixed_list,key=lambda x: int(x[1]),reverse=True)
        mashed_scores.pop()
        order=[
            'first',
            'second',
            'third',
            'fourth',
            'fifth',
            'sixth',
            'seventh',
            'eighth',
            'ninth',
            'tenth']
        for place,items in zip(order,mashed_scores):
            config['initials'][place]=items[0]
            config['scores'][place]=items[1]
        with open(config_path,'w') as configfile:
                config.write(configfile)

    def on_leave(self,*args):
        self.clear_widgets()

    def on_pre_enter(self,*args):
        self.add_widget(self.bg_image)
        self.add_widget(PinLock())

class ChickenRun(App):
    def build(self):
        self._config = configparser.ConfigParser()
        self._config.read(config_path)
        self.sm=sm=ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(BragScreen(name='brag'))
        sm.add_widget(ScoreScreen(name='scores'))
        Clock.schedule_interval(logic.update,.01)
        loop_music()
        return self.sm

ChickenRun().run()