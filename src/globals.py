# All imports are included here

import pygame
import random
import time
import tkinter as tk
from tkinter import messagebox
import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator
import threading

import matplotlib
matplotlib.use('Agg')

from constants import *


is_paused = True
total_waiting_time = 0
break_count = 0
global start_time
start_time = None
elapsed_time = 0
simulation_ended = False
paused_time = None
violet_vehicle_spawned = False
settings_opened = False

# Used for the "choose route" functionality
shared_state = {
                "departure_index": None,
                "destination_index": None,
            }