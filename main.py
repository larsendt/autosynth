#!/usr/bin/env python

import ao
import math
import struct
import random
from matplotlib import pyplot

SAMPLE_RATE = 44100

def floats_to_buf(floats):
    count = len(floats)
    i16max = (2**15) - 1
    data = map(lambda x: int(x * i16max), floats)
    return struct.pack("%dh" % count, *data)

def normalize(orig_data):
    outdata = []
    _max = max(map(abs, orig_data))
    for d in orig_data:
        outdata.append(d / _max)
    return outdata

def tri(t, a):
    t += (0.25 * a)
    return 2 * abs(2 * ((t/a) - math.floor((t/a) + 0.5))) - 1

def saw(t, a):
    return 2 * ((t/a) - math.floor(0.5 + (t/a)))

def sin(t, a):
    a = (2 * math.pi) / a
    return math.sin(t * a)

def sq(t, a):
    return 1 if sin(t, a) > 0 else -1

def null(t, a):
    return 0

def noise(t, a):
    return random.uniform(-1, 1)

def wave(function, frequency, sample_rate, seconds):
    period = 1.0 / frequency
    inc = 1.0 / sample_rate
    return [function(i*inc, period) for i in range(sample_rate * seconds)]

def add(wave1, wave2):
    outdata = []
    for a,b in zip(wave1, wave2):
        outdata.append(a+b)
    return outdata

def append(wave1, wave2):
    return wave1 + wave2

def volume(wave, vol):
    outdata = []
    for d in wave:
        outdata.append(vol*d)
    return outdata

d1 = wave(tri, 100, SAMPLE_RATE, 2)
d2 = wave(tri, 93, SAMPLE_RATE, 2)

d3 = wave(tri, 80, SAMPLE_RATE, 2)
d4 = wave(tri, 70, SAMPLE_RATE, 2)

data = d1 + d2 + d3 + d4
data = normalize(data)
data = volume(data, 0.25)
raw_data = floats_to_buf(data)

dev = ao.AudioDevice(ao.driver_id("pulse"), bits=16, rate=SAMPLE_RATE, channels=1)
dev.play(raw_data)
