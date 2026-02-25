# -*- coding: utf-8 -*-
"""
Created on Sun Dec 20 22:39:00 2015

@author: anna
"""

import numpy as np
import grass.script as gscript
from grass.script import array as garray


def main(elevation, dxn, dyn):
    elev = garray.array()
    elev.read(elevation)
    dx = garray.array()
    dx.read(dxn)
    dy = garray.array()
    dy.read(dyn)
    new = garray.array()
    for row in new:
        row = np.zeros(new.shape[1])

    # sampling
    region = gscript.region()
    walkers_x = np.arange(region['w'], region['e'] - region['ewres'])
    walkers_x += np.random.rand() * region['ewres']
    walkers_y = np.arange(region['n'], region['s'] + region['nsres'], -region['nsres'])
    walkers_y -= np.random.rand() * region['nsres']

    man = 0.1
    time = 600  # s
    vx = (1 / man) * dx * (1 / np.sqrt(np.sqrt(dx*dx + dy*dy)))
    vy = (1 / man) * dy * (1 / np.sqrt(np.sqrt(dx*dx + dy*dy)))
    step_s = np.sqrt(region['nsres'] * region['ewres']) / np.mean(np.sqrt(vx*vx + vy*vy))
    step_s *= 0.25
    vx *= step_s
    vy *= step_s

    rain_inten = 30  # mm/h
    rain_inten *= 2.78e-6
    nwalkers = 500000.
    diffusion = 0.8

    sigma = np.sqrt(step_s *4)

    walkers_x = np.array([])
    walkers_y = np.array([])
    walker_per_cell = nwalkers / region['cells']
    weight = walker_per_cell / np.ceil(walker_per_cell)
    for row in range(region['rows']):
        for col in range(region['cols']):
            pos = region['s'] + row * region['nsres'] + \
                region['nsres'] * np.random.rand(int(np.ceil(walker_per_cell)))
            walkers_y = np.append(walkers_y, pos)
            pos = region['w'] + col * region['ewres'] + \
                region['ewres'] * np.random.rand((np.int(np.ceil(walker_per_cell))))
            walkers_x = np.append(walkers_x, pos)
    t = 0
    nwalkers = walkers_x.shape[0]
    print weight
    weight *= rain_inten * step_s * region['cells'] / nwalkers
    print weight

    while t < time:
        inside = (walkers_x > region['w']) & (walkers_x < region['e']) & (walkers_y > region['s']) & (walkers_y < region['n'])
        walkers_y = walkers_y[inside]
        walkers_x = walkers_x[inside]
        # get cell coordinate
        x_index = np.floor((walkers_x - region['w']) / region['ewres']).astype(int)
        y_index = np.floor((region['n'] - walkers_y) / region['nsres']).astype(int)

        # save depth
        xedges = np.arange(region['w'], region['e'] + region['ewres']/2., region['ewres'])
        yedges = np.arange(region['s'], region['n'] + region['nsres']/2., region['nsres'])
        H, xedges, yedges = np.histogram2d(walkers_y, walkers_x,  bins=(yedges, xedges))
        i = H.shape[0] - 1
        for row in H:
            new[i] += row * weight
            i -= 1
        # compute jump
        sx = vx[y_index, x_index]
        sy = vy[y_index, x_index]

        walkers_x += sx + sigma * np.random.randn(sx.shape[0]) * diffusion
        walkers_y += sy + sigma * np.random.randn(sy.shape[0]) * diffusion
        t += 4 * step_s

    for i in range(new.shape[0]):
        new[i] = np.power(new[i], 3./5)
    new.write(mapname="new", overwrite=True)

if __name__ == '__main__':
    main(elevation='elev_lid792_1m', dxn='dx', dyn='dy')
