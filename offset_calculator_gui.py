# -*- coding: utf-8 -*-
"""
Created on Wed Jun 23 19:15:07 2021

@author: erinr
"""


import numpy as np
import matplotlib.pyplot as plt
import itertools
import os
import ipywidgets as widgets
from tkinter import *
import tkinter.messagebox as box
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure

months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
unique_stars = [None]

stardir = r'C:\Users\erinr\Desktop\starlogs'
os.chdir(stardir)

window = Tk()
window.title( 'Baseline Offset Calculator' )

frame = Frame( window)
bottomframe = Frame(window)
buttonframe = Frame(window)
star_offset_frame = Frame(window)
buttonframe2 = Frame(window)
plot_frame = Frame(window)

files = []
for file in os.listdir(stardir):
    if '.txt' in file:
        files.append(file)
years = list(set([files[i][0:4] for i in range(len(files))]))
years.sort()
years.reverse()
print(years)

yearvar = StringVar(frame)
yearvar2 = StringVar(frame)
monthvar = StringVar(frame)
monthvar2 = StringVar(frame)
yearvar.set('Year (Begin)')
yearvar2.set('Year (End)')
monthvar.set('Month (Begin)')
monthvar2.set('Month (End)')

def selected_baselines(*args):
   selected = []
   if bvar1.get() == 1:
       selected.append(1)
   if bvar2.get() == 2:
       selected.append(2)
   if bvar3.get() == 3:
       selected.append(3)
   if bvar4.get() == 4:
       selected.append(4)
   if bvar5.get() == 5:
       selected.append(5)
    
   return selected


bvar1 = IntVar(star_offset_frame)
bvar2 = IntVar(star_offset_frame)
bvar3 = IntVar(star_offset_frame)
bvar4 = IntVar(star_offset_frame)
bvar5 = IntVar(star_offset_frame)

starvar = StringVar(star_offset_frame)
starvar.set('Pick a star')

dropdown_stars = OptionMenu(star_offset_frame,starvar,*unique_stars)

R1 = Checkbutton(star_offset_frame, text="Baseline 1", variable=bvar1, onvalue=1,
                  command=selected_baselines)
R2 = Checkbutton(star_offset_frame, text="Baseline 2", variable=bvar2, onvalue=2,
                  command=selected_baselines)
R3 = Checkbutton(star_offset_frame, text="Baseline 3", variable=bvar3, onvalue=3,
                  command=selected_baselines)
R4 = Checkbutton(star_offset_frame, text="Baseline 4", variable=bvar4, onvalue=4,
                  command=selected_baselines)
R5 = Checkbutton(star_offset_frame, text="Baseline 5", variable=bvar5, onvalue=5,
                  command=selected_baselines)

bvar1.trace('w', selected_baselines)
bvar2.trace('w', selected_baselines)
bvar3.trace('w', selected_baselines)
bvar4.trace('w', selected_baselines)
bvar5.trace('w', selected_baselines)


dropdown_year = OptionMenu(frame, yearvar, *years)
dropdown_months = OptionMenu(frame, monthvar, *months)
dropdown_year2 = OptionMenu(frame, yearvar2, *years)
dropdown_months2 = OptionMenu(frame, monthvar2, *months)

listbox = Listbox(bottomframe, width=35, height=10, selectmode='extended')
listbox2 = Listbox(bottomframe,width=35, height=10)

def show_date(*args):

    if yearvar.get() != 'Year (Begin)' and monthvar.get() != 'Month (Begin)' and yearvar2.get() != 'Year (End)' and monthvar2.get() != 'Month (End)':
        year1 = yearvar.get()
        month1 = monthvar.get()
        date_begin = year1 + '-' + month1

        year2 = yearvar2.get()
        month2 = monthvar2.get()
        date_end = year2 + '-' + month2
        
        year_range = np.arange(int(year1), int(year2) + 1)
        month_range = np.arange(int(month1), int(month2) + 1)
        date_range = []
        for year in year_range:
            if len(year_range) > 1:
                if year == year_range[0]:
                    for month in np.arange(month_range[0], 13):
                        date_range.append(str(year) + '-' + months[month-1])
                elif year == year_range[-1]:
                    for month in np.arange(1, month_range[-1] + 1):
                        date_range.append(str(year) + '-' + months[month-1])
                else:
                    for month in np.arange(12):
                        date_range.append(str(year) + '-' + months[month])
            else:
                for month in month_range:
                    date_range.append(str(year) + '-' + months[month-1])
        
        logs = []
        for date in date_range:
            for file in files:
                if date in file:
                    logs.append(file)
        logs.reverse()
        listbox.delete(0, 'end')
        for log in logs:
            listbox.insert('end', log)
    else:
        pass
    
 
yearvar.trace('w', show_date)
monthvar.trace('w', show_date)
yearvar2.trace('w', show_date)
monthvar2.trace('w', show_date)

def onselect_logs(event):
    # Note here that Tkinter passes an event object to onselect()
    w = event.widget
    indices = w.curselection()
    selected_logs = []
    for index in indices:
        value = w.get(index)
        selected_logs.append(value)
    selected_logs.sort()
    listbox2.delete(0, 'end')
    for log in selected_logs:
        listbox2.insert('end', log)


listbox.bind('<<ListboxSelect>>', onselect_logs)
    

def import_logs():
    starlogs = list(listbox2.get(0,'end'))
    data = []

    # Pull in starlog data, skipping the header and also skipping the fsnr lines. Does not
    # work for a file which has multiple headers at the moment.
    
    for starlog in starlogs:
        with open(starlog, 'r') as f:
            content = f.read().split('\nUT_date: ')[1:]
            for c in content:
                data.append(c.split('\n')[17::2])
    
    #print(data)
    #Combine all the starlogs into one list of entries, then split each entry
    #which is a single string containing the entire entry into a list of the individual column entries
    for i in range(len(data)):
        data[i] = [data[i][j].split() for j in range(len(data[i]))]
        for j in range(len(data)):
            if data[j][-1] == []:
                data[j] = data[j][0:-1]
    
    # Pull out only the coherent scans
    data_clean = []
    for i in range(len(data)):
        for j in range(len(data[i])):
            if data[i][j][1] != 'I' and data[i][j][9] != '-1.000' and data[i][j][12] != '-1.000': # the and statements are in case a non-coherent entry was under a different label
                data_clean.append(data[i][j])
    
    # Make arrays of the star names, hour angles, and offsets for each individual entry
    stars = np.array([data_clean[i][2] for i in range(len(data_clean))])
    angles = np.array([data_clean[i][4] for i in range(len(data_clean))]).astype(np.float)
    b1 = np.array([data_clean[i][9] for i in range(len(data_clean))]).astype(np.float)
    b2 = np.array([data_clean[i][10] for i in range(len(data_clean))]).astype(np.float)
    b3 = np.array([data_clean[i][11] for i in range(len(data_clean))]).astype(np.float)
    b4 = np.array([data_clean[i][12] for i in range(len(data_clean))]).astype(np.float)
    b5 = np.array([data_clean[i][13] for i in range(len(data_clean))]).astype(np.float)
    
    # Dictionaries to contain the hour angles and offsets for each observation for each unique star
    unique_stars = list(set(stars))
    global b1_dict; global b2_dict; global b3_dict; global b4_dict; global b5_dict; global angles_dict
    b1_dict = {star: [] for star in unique_stars}
    b2_dict = {star: [] for star in unique_stars}
    b3_dict = {star: [] for star in unique_stars}
    b4_dict = {star: [] for star in unique_stars}
    b5_dict = {star: [] for star in unique_stars}
    angles_dict = {star: [] for star in unique_stars}
    
    
    # Sort the starlog entries into the dictionaries
    for star in unique_stars:
        for i in range(len(stars)):
            if stars[i] == star:
                b1_dict[star].append(b1[i])
                b2_dict[star].append(b2[i])
                b3_dict[star].append(b3[i])
                b4_dict[star].append(b4[i])
                b5_dict[star].append(b5[i])
                angles_dict[star].append(angles[i])
                
    # calculate polynomial fits
    global polydict
    polydict = {star: [] for star in unique_stars}
    for star in unique_stars:
        polydict[star].append(np.polyfit(angles_dict[star], b1_dict[star],2))
        polydict[star].append(np.polyfit(angles_dict[star], b2_dict[star],2))
        polydict[star].append(np.polyfit(angles_dict[star], b3_dict[star],2))
        polydict[star].append(np.polyfit(angles_dict[star], b4_dict[star],2))
        polydict[star].append(np.polyfit(angles_dict[star], b5_dict[star],2))
     
    dropdown_stars['menu'].delete(0,'end')
    for star in unique_stars:
        dropdown_stars['menu'].add_command(label=star,command=lambda value=star: starvar.set(value))       
        
def clear_selection():
    dropdown_stars['menu'].delete(0,'end')
    listbox2.delete(0, 'end')
  
# the figure that will contain the plot
fig = Figure(figsize=(8,5), dpi=100)

# creating the Tkinter canvas
# containing the Matplotlib figure
canvas = FigureCanvasTkAgg(fig, master = plot_frame)

# placing the canvas on the Tkinter window
canvas.get_tk_widget().configure(highlightbackground='black',highlightthickness=2)
  
def plot_offsets():

    fig.clear()
    global plot1
    plot1 = fig.add_subplot(111)

    baselines = selected_baselines()
    star = starvar.get()
    print(baselines)
    print(star)
    
    # Scatter plot the hour angles and offsets for the star
    if 1 in baselines:
        plot1.scatter(angles_dict[star], b1_dict[star], label='b1',c='lime')
    if 2 in baselines:
        plot1.scatter(angles_dict[star], b2_dict[star], label='b2',c='red')
    if 3 in baselines:
        plot1.scatter(angles_dict[star], b3_dict[star], label='b3',c='orange')
    if 4 in baselines:
        plot1.scatter(angles_dict[star], b4_dict[star], label='b4',c='blue')
    if 5 in baselines:
        plot1.scatter(angles_dict[star], b5_dict[star], label='b5',c='pink')    
    
    
    ylims = plot1.axes.get_ylim()
    # Other plot setup
    plot1.set_ylim([ylims[0]-0.5, ylims[1]+0.5])
    plot1.set_xlim([np.amin(angles_dict[star]) - 0.75,np.amax(angles_dict[star]) + 0.75])
    plot1.set_title(star,fontsize=12)
    plot1.set_ylabel('Baseline Offset (mm)',fontsize=12)
    plot1.set_xlabel('Hour Angle', fontsize=12)
    plot1.axes.tick_params(labelsize=10)
    global leg
    leg = plot1.axes.legend(fontsize=10,loc='upper left')
    
    canvas.draw()
    
def plot_fits():
    baselines = selected_baselines()
    star = starvar.get()
    xs=np.linspace(np.amin(angles_dict[star]) - 0.5, np.amax(angles_dict[star]) + 0.5, 1000)
    
    # Scatter plot the hour angles and offsets for the star
    leg_text = leg.get_texts()
    leg_text_strings = [leg.get_texts()[i].get_text() for i in range(len(leg.get_texts()))]
    print(leg_text)
    if 1 in baselines:
        leg_text[leg_text_strings.index('b1')].set_text('b1, y=%.4fx^2 + %.4fx + %.4f' % (polydict[star][0][0], polydict[star][0][1], polydict[star][0][2]))
        plot1.plot(xs, (polydict[star][0][0] * (xs**2)) + (polydict[star][0][1]* xs) + polydict[star][0][2],c='lime')
    if 2 in baselines:
        leg_text[leg_text_strings.index('b2')].set_text('b2, y=%.4fx^2 + %.4fx + %.4f' % (polydict[star][1][0], polydict[star][1][1], polydict[star][1][2]))
        plot1.plot(xs, (polydict[star][1][0] * (xs**2)) + (polydict[star][1][1]* xs) + polydict[star][1][2],c='red')
    if 3 in baselines:
        leg_text[leg_text_strings.index('b3')].set_text('b3, y=%.4fx^2 + %.4fx + %.4f' % (polydict[star][2][0], polydict[star][2][1], polydict[star][2][2]))
        plot1.plot(xs, (polydict[star][2][0] * (xs**2)) + (polydict[star][2][1]* xs) + polydict[star][2][2],c='orange')
    if 4 in baselines:
        leg_text[leg_text_strings.index('b4')].set_text('b4, y=%.4fx^2 + %.4fx + %.4f' % (polydict[star][3][0], polydict[star][3][1], polydict[star][3][2]))
        plot1.plot(xs, (polydict[star][3][0] * (xs**2)) + (polydict[star][3][1]* xs) + polydict[star][3][2],c='blue')
    if 5 in baselines:
        leg_text[leg_text_strings.index('b5')].set_text('b5, y=%.4fx^2 + %.4fx + %.4f' % (polydict[star][4][0], polydict[star][4][1], polydict[star][4][2]))
        plot1.plot(xs, (polydict[star][4][0] * (xs**2)) + (polydict[star][4][1]* xs) + polydict[star][4][2],c='magenta') 

    canvas.draw()       
    
    
import_button = Button(buttonframe, text = 'Import Logs', command=import_logs, width=15)
clear_button = Button(buttonframe, text = 'Clear Selection', command=clear_selection,width=15)
plot_button = Button(buttonframe2, text = 'Plot Offsets', command=plot_offsets,width=15)
plotfit_button = Button(buttonframe2, text = 'Plot Fits',command=plot_fits,width=15)
#btn.pack( side = RIGHT , padx = 5 )
#listbox_year.pack( side = LEFT )
#listbox2.pack(side= LEFT,padx=20)
frame.pack(side=TOP,padx = 10, pady = 5, expand=True)
buttonframe.pack(side=TOP,pady=5)
bottomframe.pack(side=TOP, pady=15)
star_offset_frame.pack(side=TOP, pady=5)
buttonframe2.pack(side=TOP, pady=5)
plot_frame.pack(side=TOP)
dropdown_year.pack(side=LEFT, fill='x',padx=5)
dropdown_months.pack(side=LEFT, fill='x',padx=5)
dropdown_year2.pack(side=LEFT, fill='x',padx=5)
dropdown_months2.pack(side=LEFT, fill='x',padx=5)

listbox.pack(side=LEFT)
listbox2.pack(side=LEFT)
import_button.pack(side=LEFT,fill='both',expand=True,padx=5)
clear_button.pack(side=LEFT,fill='both',expand=True,padx=5)
dropdown_stars.pack(side=LEFT, fill='x', padx=5)
R1.pack(side=LEFT,pady=5)
R2.pack(side=LEFT)
R3.pack(side=LEFT)
R4.pack(side=LEFT)
R5.pack(side=LEFT)
plot_button.pack(side=LEFT,padx=5)
plotfit_button.pack(side=LEFT,padx=5)
canvas.get_tk_widget().pack(side=BOTTOM,pady=15,fill='both')


dropdown_year.config(width=12)
dropdown_year2.config(width=12)
dropdown_months.config(width=12)
dropdown_months2.config(width=12)
dropdown_stars.config(width=10)
window.mainloop()