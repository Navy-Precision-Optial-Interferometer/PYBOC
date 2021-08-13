# -*- coding: utf-8 -*-
"""
Created on Wed Jun 23 19:15:07 2021

@author: erinr
"""
##### LIBRARY IMPORTS #####

import numpy as np
import os
from tkinter import *
from tkinter.filedialog import asksaveasfilename
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

##### FIND LOGS AND THEIR TIME RANGE #####

app_path = os.getcwd()
stardir = app_path + '/starlogs'
os.chdir(stardir)

files = []
for file in os.listdir(stardir):
    if 'starLog' in file:
        files.append(file)
years = list(set([files[i][0:4] for i in range(len(files))]))
years.sort()
years.reverse()

months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
unique_stars = [None]

##### GUI WINDOW SETUP #####

window = Tk()
window.title('Baseline Offset Calculator')
    
date_frame = Frame( window)
selection_frame = Frame(window)
sel_button_frame = Frame(window)
star_ha_frame = Frame(window)
offset_frame = Frame(window)
plot_frame = Frame(window)

##### FUNCTIONS #####

def show_date(*args):

    if yearvar.get() != 'Year (Begin)' and monthvar.get() != 'Month (Begin)' and yearvar2.get() != 'Year (End)' and monthvar2.get() != 'Month (End)':
        year1 = yearvar.get()
        month1 = monthvar.get()

        year2 = yearvar2.get()
        month2 = monthvar2.get()
        
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
    
def addlog():
    # Note here that Tkinter passes an event object to onselect()
    indices = listbox.curselection()
    selected_logs = list(listbox2.get(0,END))
    for index in indices:
        value = listbox.get(index)
        selected_logs.append(value)
    selected_logs.sort()
    selected_logs.reverse()
    listbox2.delete(0, 'end')
    for log in selected_logs:
        listbox2.insert('end', log)
    
def addall():
    listbox2.delete(0,END)
    logs = list(listbox.get(0,END))
    logs.sort()
    logs.reverse()
    for log in logs:
        listbox2.insert(END,log)

def remove():
    indices = listbox2.curselection()
    for index in indices:
        listbox2.delete(index)
    
        
    

def import_logs():
    '''Import selected starlogs and sort data by star and offset,
    and calculate the polynomial fits for each one'''
    if len(listbox2.get(0,END)) != 0:
        import_button.configure(text='Logs Imported!', bg='green')
        
        # Reset baseline selections and text display
        R1.deselect()
        R2.deselect()
        R3.deselect()
        R4.deselect()
        R5.deselect()
        
        starvar.set('Pick a Star')
        R1.configure(text="b1: -1.000")
        R2.configure(text="b2: -1.000")
        R3.configure(text="b3: -1.000")
        R4.configure(text="b4: -1.000")
        R5.configure(text="b5: -1.000")
        ha_var.set('Hour Angle')
        
        # Activate function callbacks for the offset checkboxes and star dropdown
        # global trace1; global trace2; global trace3; global trace4; global trace5
        # trace1 = bvar1.trace('w', plot_offsets)
        # trace2 = bvar2.trace('w', plot_offsets)
        # trace3 = bvar3.trace('w', plot_offsets)
        # trace4 = bvar4.trace('w', plot_offsets)
        # trace5 = bvar5.trace('w', plot_offsets)
        
        # global startrace;global startrace_offset
        # startrace = starvar.trace('w',plot_offsets)
        # startrace_offset = starvar.trace('w',calculate_offsets)
        
        # clear and redraw the plotting canvas
        fig.clear()
        canvas.draw()
    
        # Get list of selected starlogs from box
        starlogs = list(listbox2.get(0,'end'))
        
        # Begin data import
        data = []
        fsnr_data = []
    
        # Pull in starlog data, skipping the header and also skipping the fsnr lines. Does not
        # work for a file which has multiple headers at the moment.
        
        for starlog in starlogs:
            with open(starlog, 'r') as f:
                content = f.read().split('\nUT_date: ')[1:]
                for c in content:
                    data.append(c.split('\n')[17::2])
                    fsnr_data.append(c.split('\n')[18::2])
                    
    
        #Combine all the starlogs into one list of entries, then split each entry
        #which is a single string containing the entire entry into a list of the individual column entries
        for i in range(len(data)):
            data[i] = [data[i][j].split() for j in range(len(data[i]))]
            fsnr_data[i] = [fsnr_data[i][j].split() for j in range(len(fsnr_data[i]))]
            for j in range(len(data)):
                if data[j][-1] == []:
                    data[j] = data[j][0:-1]
                    fsnr_data[j] = fsnr_data[j][0:-1]
        
        # Pull out only the coherent scans
        data_clean = []
        fsnr_data_clean = []
        for i in range(len(data)):
            for j in range(len(data[i])):
                offset_mean = np.mean([float(data[i][j][k]) for k in np.arange(9,14)])
                if data[i][j][1] != 'I' and offset_mean != -1.0: #the and statements are in case a non-coherent entry was under a different label
                    data_clean.append(data[i][j])
                    fsnr_data_clean.append(fsnr_data[i][j])

        # Make arrays of the star names, hour angles, and offsets for each individual entry
        global b1; global b2; global b3; global b4; global b5
        stars = np.array([data_clean[i][2] for i in range(len(data_clean))])
        angles = np.array([data_clean[i][4] for i in range(len(data_clean))]).astype(np.float)
        b1 = np.array([data_clean[i][9] for i in range(len(data_clean))]).astype(np.float)
        b2 = np.array([data_clean[i][10] for i in range(len(data_clean))]).astype(np.float)
        b3 = np.array([data_clean[i][11] for i in range(len(data_clean))]).astype(np.float)
        b4 = np.array([data_clean[i][12] for i in range(len(data_clean))]).astype(np.float)
        b5 = np.array([data_clean[i][13] for i in range(len(data_clean))]).astype(np.float)
        
        global b1_fsnr; global b2_fsnr; global b3_fsnr; global b4_fsnr; global b5_fsnr
        b1_fsnr = np.array([fsnr_data_clean[i][0] for i in range(len(fsnr_data_clean)) if fsnr_data_clean[i][0] != '-1.000']).astype(np.float)
        b2_fsnr = np.array([fsnr_data_clean[i][1] for i in range(len(fsnr_data_clean)) if fsnr_data_clean[i][1] != '-1.000']).astype(np.float)
        b3_fsnr = np.array([fsnr_data_clean[i][2] for i in range(len(fsnr_data_clean)) if fsnr_data_clean[i][2] != '-1.000']).astype(np.float)
        b4_fsnr = np.array([fsnr_data_clean[i][3] for i in range(len(fsnr_data_clean)) if fsnr_data_clean[i][3] != '-1.000']).astype(np.float)
        b5_fsnr = np.array([fsnr_data_clean[i][4] for i in range(len(fsnr_data_clean)) if fsnr_data_clean[i][4] != '-1.000']).astype(np.float)

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
                    
        # Calculate polynomial fits
        global polydict
        polydict = {star: [] for star in unique_stars}
        for star in unique_stars:
            polydict[star].append(np.polyfit(angles_dict[star], b1_dict[star],2))
            polydict[star].append(np.polyfit(angles_dict[star], b2_dict[star],2))
            polydict[star].append(np.polyfit(angles_dict[star], b3_dict[star],2))
            polydict[star].append(np.polyfit(angles_dict[star], b4_dict[star],2))
            polydict[star].append(np.polyfit(angles_dict[star], b5_dict[star],2))
         
        # Populate star dropdown    
        dropdown_stars['menu'].delete(0,'end')
        for star in unique_stars:
            dropdown_stars['menu'].add_command(label=star,command=lambda value=star: starvar.set(value))       
    else:
        pass
    
def poly_calc(a, b, c, x):
    '''Quadratic function for calculating offsets based on coefficients'''
    return (a * x**2) + (b*x) + c

def clear_selection():
    
    '''Clear all selections except date range.'''
    
    # Remove the value tracers for the offset displays and star dropdown
    # so they don't call any functions when their text is reset to default
    # bvar1.trace_remove('write',trace1)
    # bvar2.trace_remove('write',trace2)
    # bvar3.trace_remove('write',trace3)
    # bvar4.trace_remove('write',trace4)
    # bvar5.trace_remove('write',trace5)
    # starvar.trace_remove('write',startrace)
    # starvar.trace_remove('write',startrace_offset)
    
    # Deselect all offset checkboxes and reset text to default
    R1.deselect()
    R2.deselect()
    R3.deselect()
    R4.deselect()
    R5.deselect()
    R1.configure(text='b1: -1.000')
    R2.configure(text='b2: -1.000')
    R3.configure(text='b3: -1.000')
    R4.configure(text='b4: -1.000')
    R5.configure(text='b5: -1.000')
    histo_button.deselect()
    
    # Reset import button
    import_button.configure(text='Import Logs', bg='black')
    
    # Clear dropdown and HA entry box
    dropdown_stars['menu'].delete(0,'end')
    starvar.set('Pick a Star')
    ha_var.set('Hour Angle')
    
    # Clear the selected logs box
    listbox2.delete(0, 'end')
    
    # Clear the plotting frame and redraw it
    fig.clear()
    canvas.draw()
    window.focus()
    
def selected_baselines(*args):

   '''Keep track of which offsets are selected. If one is,
   give a raised relief to the checkbox. If one isn't, flatten
   it and reset text to default'''

   selected = []
   if bvar1.get() == 1:
       selected.append(1)
       R1.configure(relief='raised')
   else:
       R1.configure(text='b1: -1.000', relief='flat')
   if bvar2.get() == 2:
       selected.append(2)
       R2.configure(relief='raised')
   else:
       R2.configure(text='b2: -1.000', relief='flat')
   if bvar3.get() == 3:
       selected.append(3)
       R3.configure(relief='raised')
   else:
       R3.configure(text='b3: -1.000',relief='flat')
   if bvar4.get() == 4:
       selected.append(4)
       R4.configure(relief='raised')
   else:
       R4.configure(text='b4: -1.000', relief='flat')
   if bvar5.get() == 5:
       selected.append(5)
       R5.configure(relief='raised')
   else:
       R5.configure(text='b5: -1.000', relief='flat')
    
   return selected

def plot_offsets(*args):
    
    '''Plot the offset data and quadratic fits for each
    selected baseline'''

    # Clear the figure
    fig.clear()
    
    # Get selected baselines and star
    baselines = selected_baselines()
    star = starvar.get()

    try:
        if len(baselines) == 0: # clear figure if no baselines selected
            fig.clear()
        else: 
            # create plot
            if histvar.get() == 0 and starvar.get() != 'Pick a Star':
                global plot1
                plot1 = fig.add_subplot(111)
                
                # hour angles for plotting fit: from minimum angle in data - 0.5 to max angle in data + 0.5
                xs=np.linspace(np.amin(angles_dict[star]) - 0.5, np.amax(angles_dict[star]) + 0.5, 1000)
        
                # Scatter plot the hour angles and offsets for the star, also plot quadratic fit
                if 1 in baselines:
                    plot1.scatter(angles_dict[star], b1_dict[star], label='b1, y=%.3fx^2 + %.3fx + %.3f' % (polydict[star][0][0], polydict[star][0][1], polydict[star][0][2]),c='lime')
                    plot1.plot(xs, poly_calc(polydict[star][0][0], polydict[star][0][1], polydict[star][0][2], xs),c='lime')
                    R1.configure()
                if 2 in baselines:
                    plot1.scatter(angles_dict[star], b2_dict[star], label='b2, y=%.3fx^2 + %.3fx + %.3f' % (polydict[star][1][0], polydict[star][1][1], polydict[star][1][2]),c='red')
                    plot1.plot(xs, poly_calc(polydict[star][1][0], polydict[star][1][1], polydict[star][1][2], xs),c='red')
                if 3 in baselines:
                    plot1.scatter(angles_dict[star], b3_dict[star], label='b3, y=%.3fx^2 + %.3fx + %.3f' % (polydict[star][2][0], polydict[star][2][1], polydict[star][2][2]),c='orange')
                    plot1.plot(xs, poly_calc(polydict[star][2][0], polydict[star][2][1], polydict[star][2][2], xs),c='orange')
                if 4 in baselines:
                    plot1.scatter(angles_dict[star], b4_dict[star], label='b4, y=%.3fx^2 + %.3fx + %.3f' % (polydict[star][3][0], polydict[star][3][1], polydict[star][3][2]),c='blue')
                    plot1.plot(xs, poly_calc(polydict[star][3][0], polydict[star][3][1], polydict[star][3][2], xs),c='blue')
                if 5 in baselines:
                    plot1.scatter(angles_dict[star], b5_dict[star], label='b5, y=%.3fx^2 + %.3fx + %.3f' % (polydict[star][4][0], polydict[star][4][1], polydict[star][4][2]),c='magenta')    
                    plot1.plot(xs, poly_calc(polydict[star][4][0], polydict[star][4][1], polydict[star][4][2], xs),c='magenta') 
                
                # Other plot setup
                ylims = plot1.axes.get_ylim()
                plot1.set_ylim([ylims[0]-0.5, ylims[1]+0.5])
                plot1.set_xlim([np.amin(angles_dict[star]) - 1.0, np.amax(angles_dict[star]) + 1.0])
                plot1.set_title(star,fontsize=12)
                plot1.set_ylabel('Baseline Offset (mm)',fontsize=12)
                plot1.set_xlabel('Hour Angle', fontsize=12)
                plot1.axes.tick_params(labelsize=10)
                plot1.axes.legend(fontsize=8,frameon=False)
            elif histvar.get() == 1:
                global plot2
                plot2 = fig.add_subplot(111)
    
                # Histograms of fsnrs for each baseline
                if len(baselines) == 1:
                    alp = 1
                else:
                    alp = 0.25

                if 1 in baselines:
                    plot2.hist(b1_fsnr, label='b1, mean = %.1f' % np.mean(b1_fsnr), color='lime',alpha=alp)
                if 2 in baselines:
                    plot2.hist(b2_fsnr, label='b2, mean = %.1f' % np.mean(b2_fsnr), color='red', alpha=alp)
                if 3 in baselines:
                    plot2.hist(b3_fsnr, label='b3, mean = %.1f' % np.mean(b3_fsnr), color='orange', alpha=alp)
                if 4 in baselines:
                    plot2.hist(b4_fsnr, label='b4, mean = %.1f' % np.mean(b4_fsnr), color='blue', alpha=alp)
                if 5 in baselines:
                    plot2.hist(b5_fsnr, label='b5, mean = %.1f' % np.mean(b5_fsnr), color='magenta', alpha=alp)
                    
                plot2.set_title('FSNRs for Targets in Selected Logs')
                plot2.set_xlabel('FSNR', fontsize=12)
                plot2.axes.tick_params(labelsize=10)
                plot2.axes.legend(fontsize=8,frameon=False)
    except NameError or KeyError:
        fig.clear()
        pass
    # redraw the canvas with plots on it
    canvas.draw()
        
def calculate_offsets(*args):
    '''Calculate and display the offset for a given star,
    hour angle, and selected baseline'''
    
    # Get current star and baselines
    baselines = selected_baselines()
    star = starvar.get()
    
    plot_offsets()
    
    if ha_var.get() == 'Hour Angle' or ha_var.get() == '' or star=='Pick a Star': # do nothing if no hour angle supplied yet
        pass
    else:
        hour_angle = float(ha_var.get())
        line1 = plot1.axvline(x=hour_angle,c='black')
        if 1 in baselines:
            R1.configure(text='b1: %.3f' % poly_calc(polydict[star][0][0],polydict[star][0][1],polydict[star][0][2],hour_angle))
        if 2 in baselines:
            R2.configure(text='b2: %.3f' % poly_calc(polydict[star][1][0],polydict[star][1][1],polydict[star][1][2],hour_angle))
        if 3 in baselines:
            R3.configure(text='b3: %.3f' % poly_calc(polydict[star][2][0],polydict[star][2][1],polydict[star][2][2],hour_angle))
        if 4 in baselines:
            R4.configure(text='b4: %.3f' % poly_calc(polydict[star][3][0],polydict[star][3][1],polydict[star][3][2],hour_angle))
        if 5 in baselines:
            R5.configure(text='b5: %.3f' % poly_calc(polydict[star][4][0],polydict[star][4][1],polydict[star][4][2],hour_angle))
     
    canvas.draw()
    
def ha_focus(event):
    '''Remove text from HA entry box when it is clicked into'''
    ha_var.set('')
    ha_entry_box.focus_set()

def ha_outfocus(event):
    '''Reset HA entry box text'''
    ha_var.set('Hour Angle')
    
def save_plot():
    a = asksaveasfilename(filetypes=(("PNG Image", "*.png"),("All Files", "*.*")), 
    defaultextension='.png', title="Save File")
    if a:
        fig.savefig(a)

##### CREATE GUI WIDGETS AND THEIR FUNCTION CALLBACKS #####
instructions = """Welcome to PyBOC, the Python Baseline Offset Calculator Tool for NPOI. To use, follow the instructions below:\n
1. Select the date range containing the starLogs you wish to use.
2. Add or remove starLogs from your selection using the buttons, then click 'Import Logs.'
3. Select the star and baselines to calculate offsets for.
5. Input the hour angle and hit 'Enter.' The calculated offsets will be displayed in the colored boxes.
6. Select 'Display FSNR Histograms' to show histograms of the FSNRs on a baseline for all targets
   in the selected logs.
7. Use 'Save Figure' to save the currently displayed figure."""

    
T1 = Label(date_frame,height=10,width=95,text=instructions,borderwidth=2,relief='solid')

# logo= PhotoImage('banner_logos.png')
# T2 = Label(image=logo)

# Date range dropdowns    
yearvar = StringVar(date_frame)
yearvar2 = StringVar(date_frame)
monthvar = StringVar(date_frame)
monthvar2 = StringVar(date_frame)

yearvar.set('Year (Begin)')
yearvar2.set('Year (End)')
monthvar.set('Month (Begin)')
monthvar2.set('Month (End)')

yearvar.trace('w', show_date)
monthvar.trace('w', show_date)
yearvar2.trace('w', show_date)
monthvar2.trace('w', show_date)

label_avail = Label(selection_frame,text='Available StarLogs')
label_select = Label(selection_frame,text='Selected Starlogs')


dropdown_year = OptionMenu(date_frame, yearvar, *years)
dropdown_months = OptionMenu(date_frame, monthvar, *months)
dropdown_year2 = OptionMenu(date_frame, yearvar2, *years)
dropdown_months2 = OptionMenu(date_frame, monthvar2, *months)
dropdown_year.config(width=12)
dropdown_year2.config(width=12)
dropdown_months.config(width=12)
dropdown_months2.config(width=12)

# Boxes for all logs in date range and then selected logs in range
listbox = Listbox(selection_frame, width=35, height=10, selectmode='extended')
#listbox.bind('<<ListboxSelect>>', onselect_logs)
listbox2 = Listbox(selection_frame,width=35, height=10, selectmode='multiple')

# Import logs and clear selection buttons
add_button = Button(selection_frame,text='Add >',command=addlog,width=15)
addall_button = Button(selection_frame,text='Add All >>', command=addall,width=15)
remove_button = Button(selection_frame,text='Remove <', command=remove,width=15)
import_button = Button(selection_frame, text = 'Import Logs', command=import_logs, width=15,bg='black',fg='white')
clear_button = Button(selection_frame, text = 'Remove All <<', command=clear_selection,width=15)
export_button = Button(star_ha_frame,text='Save Figure',command=save_plot,width=15) 
# Star selection dropdown and hour angle entry box  
starvar = StringVar(star_ha_frame)
starvar.set('Pick a Star')

global startrace;global startrace_offset
startrace = starvar.trace('w',plot_offsets)
startrace_offset = starvar.trace('w',calculate_offsets)

dropdown_stars = OptionMenu(star_ha_frame,starvar,*unique_stars)
dropdown_stars.config(width=10)

ha_var = StringVar(star_ha_frame)
ha_var.set('Hour Angle')

ha_entry_box = Entry(star_ha_frame,textvariable=ha_var,width=15)
ha_entry_box.bind("<Return>", calculate_offsets)
ha_entry_box.bind("<FocusIn>", ha_focus)
ha_entry_box.bind("<FocusOut>", ha_outfocus)

# Baseline offset checkboxes/value display
bvar1 = IntVar(offset_frame)
bvar2 = IntVar(offset_frame)
bvar3 = IntVar(offset_frame)
bvar4 = IntVar(offset_frame)
bvar5 = IntVar(offset_frame)

global trace1; global trace2; global trace3; global trace4; global trace5
trace1 = bvar1.trace('w', plot_offsets)
trace2 = bvar2.trace('w', plot_offsets)
trace3 = bvar3.trace('w', plot_offsets)
trace4 = bvar4.trace('w', plot_offsets)
trace5 = bvar5.trace('w', plot_offsets)

histvar=IntVar(offset_frame)
hist_trace = histvar.trace('w',plot_offsets)

R1 = Checkbutton(offset_frame, text="b1: -1.000", variable=bvar1, onvalue=1, offvalue=0,
                  command=calculate_offsets,activebackground='lime',bg='lime',fg='black',bd=5,width=10)
R2 = Checkbutton(offset_frame, text="b2: -1.000", variable=bvar2, onvalue=2, offvalue=0,
                  command=calculate_offsets,activebackground='red',bg='red', fg='black',bd=5,width=10)
R3 = Checkbutton(offset_frame, text="b3: -1.000", variable=bvar3, onvalue=3, offvalue=0,
                  command=calculate_offsets,activebackground='orange',bg='orange',fg='black',bd=5,width=10)
R4 = Checkbutton(offset_frame, text="b4: -1.000", variable=bvar4, onvalue=4, offvalue=0,
                  command=calculate_offsets,bg='blue',fg='white',activeforeground='white',activebackground='blue',selectcolor='gray',bd=5,width=10)
R5 = Checkbutton(offset_frame, text="b5: -1.000", variable=bvar5, onvalue=5, offvalue=0,
                  command=calculate_offsets,activebackground='magenta',bg='magenta', fg='black',bd=5,width=10)

histo_button = Checkbutton(offset_frame, text='Display FSNR\nHistograms', variable=histvar, command=plot_offsets,width=15,onvalue=1,offvalue=0)
# Plotting area
# the figure that will contain the plot
fig = Figure(figsize=(6,5),dpi=100)

# creating the Tkinter canvas
# containing the Matplotlib figure
canvas = FigureCanvasTkAgg(fig, master = plot_frame )

# placing the canvas on the Tkinter window
canvas.get_tk_widget().configure(highlightbackground='black',highlightthickness=2)

##### ARRANGE WIDGETS IN WINDOW #####

date_frame.grid(row=0,column=0,columnspan=4,pady=5,padx=5)
T1.grid(row=0,column=0,columnspan=4,padx=5,pady=5)
# T2.grid(row=0,column=1,columnspan=2,padx=5,pady=5)
dropdown_year.grid(row=1,column=0,pady=5)
dropdown_months.grid(row=1,column=1)
dropdown_year2.grid(row=1,column=2)
dropdown_months2.grid(row=1,column=3)

selection_frame.grid(row=1, column=0,columnspan=4,pady=5,padx=5)
label_avail.grid(row=0,column=0,padx=5,pady=5)
label_select.grid(row=0,column=2,padx=5,pady=5)
listbox.grid(row=1,rowspan=5,column=0,padx=5)
add_button.grid(row=1,column=1,padx=5,pady=5)
addall_button.grid(row=2,column=1,padx=5,pady=5)
remove_button.grid(row=3,column=1,padx=5,pady=5)
clear_button.grid(row=4,column=1,padx=5,pady=5)
import_button.grid(row=5,column=1,padx=5,pady=5)

listbox2.grid(row=1,rowspan=5,column=2,padx=5,pady=10)

#sel_button_frame.grid(row=2,column=0,columnspan=2,pady=10,padx=10)
plot_frame.grid(row=0,rowspan=4,column=4,columnspan=1,padx=5,pady=5)
canvas.get_tk_widget().grid(row=0,column=0)

star_ha_frame.grid(row=0,rowspan=1,column=5,padx=5,pady=5)
dropdown_stars.grid(row=0,column=0)
ha_entry_box.grid(row=1,column=0,padx=5,pady=5)
export_button.grid(row=2,column=0,padx=5,pady=5)

offset_frame.grid(row=1, rowspan=2,column=5,padx=5,pady=5)
R1.grid(row=0,column=0,padx=5,pady=5)
R2.grid(row=1,column=0,padx=5,pady=5)
R3.grid(row=2,column=0,padx=5,pady=5)
R4.grid(row=3,column=0,padx=5,pady=5)
R5.grid(row=4,column=0,padx=5,pady=5)
histo_button.grid(row=5,column=0,padx=5,pady=10)



##### RUN #####
window.mainloop()
