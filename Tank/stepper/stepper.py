'''
Module contains top-level generators.
'''
from itertools import izip
import format as fmt
from info import progress
from config import ComponentFactory
from collections import namedtuple


class AmmoFactory(object):

    '''
    A generator that produces ammo.
    '''

    def __init__(self, factory):
        '''
        Factory parameter is a configured ComponentFactory that
        is able to produce load plan and ammo generator.
        '''
        self.factory = factory
        self.load_plan = factory.get_load_plan()
        self.ammo_generator = factory.get_ammo_generator()
        self.filter = lambda missile: True
        self.marker = factory.get_marker()

    def __iter__(self):
        '''
        Returns a generator of (timestamp, marker, missile) tuples
        where missile is in a string representation. Load Plan (timestamps
        generator) and ammo generator are taken from the previously
        configured ComponentFactory, passed as a parameter to the
        __init__ method of this class.
        '''
        return (
            (timestamp, marker or self.marker(missile), missile)
            for timestamp, (missile, marker)
            in izip(self.load_plan, self.ammo_generator)
        )

    def __len__(self):
        '''
        Should return the length of ammo based on load plan,
        loop count, ammo limit and the number of missiles in
        the ammo file.

        ONLY WORKS WHEN GENERATION IS OVER
        '''
        ammo_len = len(self.ammo_generator)
        if hasattr(self.load_plan, '__len__'):
            return min(len(self.load_plan), ammo_len)
        else:
            return ammo_len

    def get_loop_count(self):
        '''
        Returns loop count from ammo_generator
        '''
        return self.ammo_generator.loop_count()

    def get_steps(self):
        '''
        Return the list of (rps, duration) tuples which represents
        the regions of constant load.
        '''
        return self.load_plan.get_rps_list()

    def get_duration(self):
        '''Get overall duration in seconds (based on load plan).'''
        return self.load_plan.get_duration() / 1000


StepperInfo = namedtuple(
    'StepperInfo',
    'loop_count,steps,loadscheme,duration,ammo_count'
)


class Stepper(object):

    def __init__(self, **kwargs):
        self.af = AmmoFactory(ComponentFactory(**kwargs))
        self.rps_schedule = kwargs['rps_schedule']
        self.ammo = fmt.Stpd(progress(self.af, 'Ammo: '))

    def write(self, f):
        for missile in self.ammo:
            f.write(missile)
        self.info = StepperInfo(
            loop_count=self.af.get_loop_count(),
            steps=self.af.get_steps(),
            loadscheme=self.rps_schedule,
            duration=self.af.get_duration(),
            ammo_count=len(self.af),
        )
