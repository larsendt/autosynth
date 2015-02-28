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

def brown_noise(sample_rate, seconds):
    a = 0
    step = 0.01
    noise = []
    for i in range(int(sample_rate * seconds)):
        p = (a + 1) / 2.0
        if random.uniform(0, 1) > p:
            s = step
        else:
            s = -step
        a += s
        noise.append(a)
    return normalize(noise)

def wave(function, frequency, sample_rate, seconds):
    period = 1.0 / frequency
    inc = 1.0 / sample_rate
    return [function(i*inc, period) for i in range(int(sample_rate * seconds))]

def add(wave1, wave2):
    outdata = []
    for a,b in zip(wave1, wave2):
        outdata.append(a+b)
    return outdata

def smooth(wave, sample_window):
    out = []
    window = [None] * sample_window
    
    def avg(win):
        s = 0
        c = 0
        for w in win:
            if w != None:
                s += w
                c += 1
        return s / float(c)

    for i in range(len(wave)):
        idx = i % sample_window
        window[idx] = wave[i]
        out.append(avg(window))
    return out

def append(wave1, wave2):
    return wave1 + wave2

def scale(wave, vol):
    outdata = []
    for d in wave:
        outdata.append(vol*d)
    return outdata

def clip(wave, amp):
    outdata = []
    for d in wave:
        if d < -amp:
            outdata.append(-amp)
        elif d > amp:
            outdata.append(amp)
        else:
            outdata.append(d)
    return outdata

def cdak_noise(minfreq, maxfreq, seconds, nsamples):
    data = []
    s = 1 / float(nsamples)
    n = seconds / s
    for i in range(int(n)):
        freq = random.randint(minfreq, maxfreq)
        d = wave(tri, freq, SAMPLE_RATE, s)
        data += d
    return data


data = []
for i in range(10):
    s = (i+1) * 5
    print s
    data.extend(smooth(brown_noise(SAMPLE_RATE, 1), s))

pyplot.plot(data[:1000])
pyplot.show()

data = normalize(data)
data = scale(data, 1.0)
raw_data = floats_to_buf(data)

dev = ao.AudioDevice(ao.driver_id("pulse"), bits=16, rate=SAMPLE_RATE, channels=1)
dev.play(raw_data)
