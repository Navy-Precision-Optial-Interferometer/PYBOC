 
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
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import webbrowser
from astropy.time import Time
import astropy.units as u
from itertools import repeat
import astropy.coordinates as coords

colors = ['black', 'lime', 'red', 'orange', 'blue', 'magenta']

##### FIND LOGS AND THEIR TIME RANGE #####

stardir = 'Z:\\'
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
window.title('PyBOC')
    
date_frame = Frame( window)
selection_frame = Frame(window)
sel_button_frame = Frame(window)
star_ha_frame = Frame(window)
offset_frame = Frame(window)
plot_frame = Frame(window)
credit_frame = Frame(window)

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
        
        # clear and redraw the plotting canvas
        fig.clear()
        canvas.draw()
    
        # Get list of selected starlogs from box
        starlogs = list(listbox2.get(0,'end'))
        
        # Begin data import
        data = []
        fsnr_data = []
        ut_dates = []
    
        # Pull in starlog data, skipping the header. Should work even for starlogs
        # with multiple headers.
        
        for starlog in starlogs:
            with open(starlog, 'r') as f:
                content = f.read().split('\nUT_date: ')[1:]
                for c in content:
                    data.append(c.split('\n')[17::2])
                    date_reps = []
                    date_reps.extend(repeat(starlog[0:16],len(c.split('\n')[17::2])))
                    ut_dates.append(date_reps)
                    date_reps=[]
                    fsnr_data.append(c.split('\n')[18::2])
                    
        # Combine all the starlogs into one list of entries, then split each entry
        # which is a single string containing the entire entry into a list of the individual column entries
        for i in range(len(data)):
            data[i] = [data[i][j].split() for j in range(len(data[i]))]
            fsnr_data[i] = [fsnr_data[i][j].split() for j in range(len(fsnr_data[i]))]
            for j in range(len(data)):
                if len(data[j]) == 0:
                    pass
                elif data[j][-1] == []:
                    data[j] = data[j][0:-1]
                    fsnr_data[j] = fsnr_data[j][0:-1]
        
        # Pull out only the coherent scans
        data_clean = []
        fsnr_data_clean = []
        ut_dates_clean = []
        
        for i in range(len(data)):
            for j in range(len(data[i])):
                if len(data[i][j][1]) != 1:
                    data[i][j].insert(1, 'X')
                    print(data[i][j])
                offset_mean = np.mean([float(data[i][j][k]) for k in np.arange(9,14)])
                if data[i][j][1] != 'I' and offset_mean != -1.0: # as long as a fringe was recorded on at least one baseline the mean of the offsets won't be -1.0
                    data_clean.append(data[i][j])
                    fsnr_data_clean.append(fsnr_data[i][j])
                    ut_dates_clean.append(ut_dates[i][j])

        # Make arrays of the star names, hour angles, and offsets for each individual entry
        stars = np.array([data_clean[i][2] for i in range(len(data_clean))])
        unique_stars = list(set(stars))
        
        
        # Get right ascension values for all stars in the imported logs, to use
        # for automated calculation of hour angles/offsets
        global star_ra
        star_ra ={}
        
        for star in unique_stars:
            if star[0:3] == 'FKV':
                star_query = 'fk5 ' + star[3:]
            elif star[0:3] == 'BSC':
                star_query = 'HR ' + star[3:]

            ra_hour = coords.SkyCoord.from_name(star_query).ra.hour            
            star_ra[star] = ra_hour
            
        # Populate star dropdown    
        dropdown_stars['menu'].delete(0,'end')
        for star in unique_stars:
            dropdown_stars['menu'].add_command(label=star,command=lambda value=star: starvar.set(value))       
        
        # Pull out hour angles for all coherent observations
        angles = np.array([float(data_clean[i][4]) for i in range(len(data_clean))])
        
        # Pull out obs numbers for all coherent observations and attach them to
        # their starlog filename, for annotating points on plots to tell
        # which log they came from
        obs_numbers = np.array([int(data_clean[i][0]) for i in range(len(data_clean))])
        dates_obsnum = list(zip(ut_dates_clean, obs_numbers))
        
        # Sort all coherent observation offsets into dictionary by baseline
        global all_offsets
        all_offsets = {1: np.array([float(data_clean[i][9]) for i in range(len(data_clean))]),
                       2: np.array([float(data_clean[i][10]) for i in range(len(data_clean))]),
                       3: np.array([float(data_clean[i][11]) for i in range(len(data_clean))]),
                       4: np.array([float(data_clean[i][12]) for i in range(len(data_clean))]),
                       5: np.array([float(data_clean[i][13]) for i in range(len(data_clean))])}
        
        # Sort all coherent observation fsnrs into dictionary by baseline
        global all_fsnrs
        all_fsnrs = {1: np.array([float(fsnr_data_clean[i][0]) for i in range(len(fsnr_data_clean))]),
                     2: np.array([float(fsnr_data_clean[i][1]) for i in range(len(fsnr_data_clean))]),
                     3: np.array([float(fsnr_data_clean[i][2]) for i in range(len(fsnr_data_clean))]),
                     4: np.array([float(fsnr_data_clean[i][3]) for i in range(len(fsnr_data_clean))]),
                     5: np.array([float(fsnr_data_clean[i][4]) for i in range(len(fsnr_data_clean))])}

        # Dictionaries to contain the hour angles, offsets
        # fsnrs, and the starlog name/obsnum tuples
        # for each observation for each unique star
        # Also a dictionary for the quadratic fit coefficients
        # for the baseline offsets per baseline and star

        global offset_dict
        offset_dict = {1: {star: [] for star in unique_stars},
                         2: {star: [] for star in unique_stars},
                         3: {star: [] for star in unique_stars},
                         4: {star: [] for star in unique_stars},
                         5: {star: [] for star in unique_stars}}
        
        global angles_dict
        angles_dict = {1: {star: [] for star in unique_stars},
                         2: {star: [] for star in unique_stars},
                         3: {star: [] for star in unique_stars},
                         4: {star: [] for star in unique_stars},
                         5: {star: [] for star in unique_stars}}

        global fsnr_dict
        fsnr_dict = {1: {star: [] for star in unique_stars},
                         2: {star: [] for star in unique_stars},
                         3: {star: [] for star in unique_stars},
                         4: {star: [] for star in unique_stars},
                         5: {star: [] for star in unique_stars}}
        
        global dates_obsnum_dict
        dates_obsnum_dict = {1: {star: [] for star in unique_stars},
                         2: {star: [] for star in unique_stars},
                         3: {star: [] for star in unique_stars},
                         4: {star: [] for star in unique_stars},
                         5: {star: [] for star in unique_stars}}
                            
        global polydict
        polydict = {1: {star: [] for star in unique_stars},
                    2: {star: [] for star in unique_stars},
                    3: {star: [] for star in unique_stars},
                    4: {star: [] for star in unique_stars},
                    5: {star: [] for star in unique_stars}}

        # Sort the data into the dictionaries by baseline and star
        for star in unique_stars:
            for i in range(len(stars)):
                if stars[i] == star:
                    for j in np.arange(1,6):
                        if all_offsets[j][i] != -1.0 or all_fsnrs[j][i] != -1.0:
                            offset_dict[j][star].append(all_offsets[j][i])
                            angles_dict[j][star].append(angles[i])
                            fsnr_dict[j][star].append(all_fsnrs[j][i])
                            dates_obsnum_dict[j][star].append(dates_obsnum[i])
        
        # Calculate quadratic fits to the baseline offsets, store coefficients
        # by star and baseline
        for star in unique_stars:
            for i in np.arange(1,6):
                try:
                    polydict[i][star] = np.polyfit(angles_dict[i][star], offset_dict[i][star],2)
                except TypeError:
                    pass
    else:
        pass
    
def poly_calc(a, b, c, x):
    '''Quadratic function for calculating offsets based on coefficients'''
    return (a * x**2) + (b*x) + c

def clear_selection():
    '''Clear all selections except date range.'''
    
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
   the checkbox and reset text to default'''

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
    selected baseline, or plot histograms of the fsnrs
    for a target if the option is selected'''

    # Clear the figure
    fig.clear()
    
    # Get selected baselines and star
    baselines = selected_baselines()
    star = starvar.get()

    try:
        if len(baselines) == 0: # clear figure if no baselines selected
            fig.clear()
        else: 
            # Offsets plot
            if histvar.get() == 0 and starvar.get() != 'Pick a Star':
                global plot1
                plot1 = fig.add_subplot(111)
                
                global annot # annotate point mouse is hovering over with starlog file name/obs number
                annot = plot1.annotate("", xy=(0,0), xytext=(-75,-45),textcoords="offset points", fontsize=12,
                bbox=dict(boxstyle="round", fc="w"),
                arrowprops=dict(arrowstyle="->"))
                annot.set_visible(False)
                
                global plot_objects
                plot_objects = {}
        
                # Scatter plot the hour angles and offsets for the star, also plot quadratic fit
                for i in np.arange(1,6):
                    if i in baselines:
                        try:
                            xs = np.linspace(np.amin(angles_dict[i][star]) - 0.5, np.amax(angles_dict[i][star]) + 0.5, 1000)
                            global sc
                            sc = plot1.scatter(angles_dict[i][star], offset_dict[i][star], label='b' + str(i), c=colors[i],s=40)
                            plot_objects[i] = sc
                            plot1.plot(xs, poly_calc(polydict[i][star][0], polydict[i][star][1], polydict[i][star][2], xs),c=colors[i])
                        except ValueError:
                            pass
                        except RuntimeWarning:
                            check_list[i-1].deselect()
                            pass
                    else:
                        pass
                
                # Other plot setup
                ylims = plot1.axes.get_ylim()
                xlims = plot1.axes.get_xlim()
                plot1.set_ylim([ylims[0]-0.5, ylims[1]+0.5])
                plot1.set_xlim([xlims[0] - 1.0, xlims[1] + 1.0])
                plot1.set_title(star,fontsize=12)
                plot1.set_ylabel('Baseline Offset (mm)',fontsize=12)
                plot1.set_xlabel('Hour Angle', fontsize=12)
                plot1.axes.tick_params(labelsize=10)
                plot1.axes.legend(fontsize=8,frameon=False)
                
            # fsnr histograms    
            elif histvar.get() == 1:
                global plot2
                plot2 = fig.add_subplot(111)
    
                # Histograms of fsnrs for each baseline
                if len(baselines) == 1: # make bars partially transparent if there is more than one baseline selected
                    alp = 1
                else:
                    alp = 0.25
                    
                for i in np.arange(1,6):
                    if i in baselines:
                        if len(fsnr_dict[i][star]) != 0:
                            try:
                                plot2.hist(fsnr_dict[i][star], label='b' + str(i) + ', mean = %.1f' % np.mean(fsnr_dict[i][star]), color=colors[i],alpha=alp)
                            except ValueError:
                                pass
                        else:
                            pass
                    else:
                        pass
                
                # Other plot setup
                plot2.set_title(star, fontsize=12)
                plot2.set_xlabel('FSNR', fontsize=12)
                plot2.axes.tick_params(labelsize=10)
                plot2.axes.legend(fontsize=8,frameon=False)
                
    except NameError or KeyError:
        fig.clear()
        pass
    
    # redraw the canvas with updated plot
    canvas.draw()    
        
def calculate_offsets(*args):
    '''Calculate and display the offset for a given star,
    hour angle, and selected baseline'''
    
    # Get current star and baselines
    baselines = selected_baselines()
    star = starvar.get()
    
    plot_offsets()
    
    if ha_var.get() == 'Hour Angle' or ha_var.get() == '' or star=='Pick a Star' or len(baselines) == 0: # do nothing if no hour angle supplied yet
        pass
    else: # calculate and display current offset value for selected baselines
        hour_angle = float(ha_var.get())
        plot1.axvline(x=hour_angle,c='black')
        for i in np.arange(1,6):
            if i in baselines:
                try:
                    try:
                        current_offset = (poly_calc(polydict[i][star][0],polydict[i][star][1],polydict[i][star][2],hour_angle)) + (int(off_list[i-1].get())/1000)
                    except ValueError:
                        current_offset = poly_calc(polydict[i][star][0],polydict[i][star][1],polydict[i][star][2],hour_angle)
                    check_list[i-1].configure(text='b' + str(i) + ': %.3f' % current_offset)
                    
                except IndexError:
                    check_list[i-1].deselect()
                    pass
     
    canvas.draw()
    
def get_hour_angle(*args):
    '''Calculate current hour angle of selected star
       based on current time and its right ascension
       and display it. Updates every 10 seconds'''
    
    star = starvar.get()
    
    if star != 'Pick a Star':
        t = Time(Time.now(),location=coords.EarthLocation(lon=-111.535*u.deg,lat=35.09666*u.deg,height=2200.66))
        LST = coords.Angle(t.sidereal_time('apparent')).hour
        ra = star_ra[star]
        hour_angle = LST - ra
        
        if hour_angle < -12:
            hour_angle += 24
        elif hour_angle > 12:
            hour_angle -= 24
            
        ha_var.set(str(round(hour_angle, 3)))
        
        ha_entry_box.after(10000,get_hour_angle)
        
def hover(event):
    '''Identify the data point being hovered over on the plot by
    baseline and index in the array of offsets for that baseline
    for that star'''
    
    selected_point = []
    try:
        vis = annot.get_visible()
        if event.inaxes == plot1:
            cont_ind = []
            
            for i in list(plot_objects.keys()):
                cont, ind = plot_objects[i].contains(event)
                cont_ind.append((cont,ind,int(i)))
    
            for item in cont_ind:
                if item[0] == True:
                    update_annot(item[1],item[2])
                    selected_point.append((item[1],item[2]))
                    annot.set_visible(True)
                    canvas.draw_idle()
                else:
                    if vis:
                        annot.set_visible(False)
                        canvas.draw_idle()
    except NameError:
        pass
    if len(selected_point) == 0:
        pass
    else:
        return selected_point
        
def update_annot(ind,baseline):
    '''Annotate point being hovered over with
       its starlog file name and obs number'''
    
    star = starvar.get()
    
    ind_val = ind['ind'][0]
    pos = plot_objects[baseline].get_offsets()[ind_val]
    annot.xy = pos
    text = dates_obsnum_dict[baseline][star][ind_val] 
    
    if baseline == 4:
        annot.set_text(text)
        annot.set_color('white')
    else:
        annot.set_text(text)
        annot.set_color('black')
        
    annot.get_bbox_patch().set_facecolor(colors[baseline])
    annot.get_bbox_patch().set_alpha(0.5)


def delete_confirm(event):
    '''Bring up a popup asking the user to confirm whether they
       want to delete a point from the plot after right clicking it'''
    points = hover(event)
    
    if event.button == 3 and points != None: 
        popup = Tk()
        popup.wm_title("!")
        label = Label(popup, text="Delete this point?")
        label.pack(side="top", fill="x", pady=10)
        B1 = Button(popup, text="Yes", command = lambda: delete_and_replot(points) or popup.destroy())
        B1.pack()
        B2 = Button(popup, text="No", command = popup.destroy)
        B2.pack()
        popup.mainloop()
    else:
        pass
    
def delete_and_replot(points):
    '''Delete selected point from the data dictionaries 
    - NOT from the starlog data file -
    recalculate the associated polynomial fits and current offsets,
    and redraw the plot'''
    
    star = starvar.get()

    for point in points:
        
        offset_dict[point[1]][star] = np.delete(offset_dict[point[1]][star], point[0]['ind'][0])
        angles_dict[point[1]][star] = np.delete(angles_dict[point[1]][star], point[0]['ind'][0])
        polydict[point[1]][star] = np.polyfit(angles_dict[point[1]][star], offset_dict[point[1]][star],2)

    plot_offsets()
    calculate_offsets()
    
def save_plot():
    '''Open file dialog to allow user to save currently displayed plot'''
    
    a = asksaveasfilename(filetypes=(("PNG Image", "*.png"),("All Files", "*.*")), 
    defaultextension='.png', title="Save File")
    if a:
        fig.savefig(a)
        
def creditlink(url):
    '''Open Confluence documentation page in web browser'''
    webbrowser.open_new(url)
        
##### CREATE GUI WIDGETS AND THEIR FUNCTION CALLBACKS #####
instructions = """Welcome to PyBOC, the Python Baseline Offset Calculator tool for NPOI. To use, follow the instructions below:\n
1. Select the date range containing the starLogs you wish to use.
2. Add or remove starLogs from your selection using the buttons, then click 'Import Logs.'
3. Select the star and baselines to calculate offsets for.
5. The current hour angle and selected offsets will be calculated/displayed, and will update every 10 seconds.
6. Hover over a point to display its starlog file name and observation number;\nright click a point to delete it and recalculate the fits/offsets.
7. Select 'Display FSNR Histograms' to show a histogram of the FSNRs for a target on the selected baselines.
8. Use 'Save Figure' to save the currently displayed figure."""

T1 = Label(date_frame,height=11,width=95,text=instructions,borderwidth=2,relief='solid')

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
listbox2 = Listbox(selection_frame,width=35, height=10, selectmode='multiple')
    
creditlabel = Label(credit_frame, text='PYBOC developed 2021 by Erin Maier. For documentation/help, see the NPOI Confluence space:', font=('',9,'italic'))

link1 = Label(credit_frame, text="(X)", fg="blue", cursor="hand2",font=('',9))
link1.bind("<Button-1>", lambda e: creditlink("https://jumar.lowell.edu/confluence/pages/viewpage.action?pageId=69960593"))

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

global startrace; global startrace_offset
startrace = starvar.trace('w',plot_offsets)
startrace_offset = starvar.trace('w',calculate_offsets)
startrace_hour = starvar.trace('w',get_hour_angle)

dropdown_stars = OptionMenu(star_ha_frame,starvar,*unique_stars)
dropdown_stars.config(width=10)

ha_var = StringVar(star_ha_frame)
ha_var.set('Hour Angle')
ha_var.trace('w',calculate_offsets)

ha_entry_box = Entry(star_ha_frame,textvariable=ha_var,width=15)

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

R1 = Checkbutton(offset_frame, text="b1: -1.000", variable=bvar1, onvalue=1, offvalue=0,
                  command=calculate_offsets,activebackground='lime',bg='lime',fg='black',selectcolor='silver',bd=5,width=10)
R2 = Checkbutton(offset_frame, text="b2: -1.000", variable=bvar2, onvalue=2, offvalue=0,
                  command=calculate_offsets,activebackground='red',bg='red', fg='black',selectcolor='silver',bd=5,width=10)
R3 = Checkbutton(offset_frame, text="b3: -1.000", variable=bvar3, onvalue=3, offvalue=0,
                  command=calculate_offsets,activebackground='orange',bg='orange',fg='black',selectcolor='silver',bd=5,width=10)
R4 = Checkbutton(offset_frame, text="b4: -1.000", variable=bvar4, onvalue=4, offvalue=0,
                  command=calculate_offsets,bg='blue',fg='white',activeforeground='white',activebackground='blue',selectcolor='gray',bd=5,width=10)
R5 = Checkbutton(offset_frame, text="b5: -1.000", variable=bvar5, onvalue=5, offvalue=0,
                  command=calculate_offsets,activebackground='magenta',bg='magenta', fg='black',selectcolor='silver',bd=5,width=10)

offlabel = Label(offset_frame, text="Calculated\nOffsets\n(mm)")

# Entry boxes for user-defined additional offsets per baseline
offlabel2 = Label(offset_frame, text="Additional\nOffset\n(microns)")

off1 = StringVar(offset_frame)
off1.set('0')
off1.trace('w',calculate_offsets)
offset1box = Entry(offset_frame,textvariable=off1,width=5)

off2 = StringVar(offset_frame)
off2.set('0')
off2.trace('w',calculate_offsets)
offset2box = Entry(offset_frame,textvariable=off2,width=5)

off3 = StringVar(offset_frame)
off3.set('0')
off3.trace('w',calculate_offsets)
offset3box = Entry(offset_frame,textvariable=off3,width=5)

off4 = StringVar(offset_frame)
off4.set('0')
off4.trace('w',calculate_offsets)
offset4box = Entry(offset_frame,textvariable=off4,width=5)

off5 = StringVar(offset_frame)
off5.set('0')
off5.trace('w',calculate_offsets)
offset5box = Entry(offset_frame,textvariable=off5,width=5)

# Lists of checkbox and entry box objects for selection/deselection purposes
check_list = [R1, R2, R3, R4, R5]
off_list = [off1, off2, off3, off4, off5]

# Histogram checkbox 
histvar=IntVar(offset_frame)
hist_trace = histvar.trace('w',plot_offsets)

histo_button = Checkbutton(offset_frame, text='Display FSNR\nHistograms', variable=histvar, command=plot_offsets,width=15,onvalue=1,offvalue=0)

# Plotting area
# the figure that will contain the plot
fig = Figure(figsize=(6,5),dpi=100)
canvas = FigureCanvasTkAgg(fig, master = plot_frame)
toolbar = NavigationToolbar2Tk(canvas, plot_frame)
toolbar.update()

# Callbacks to hover annotation and point deletion functions
canvas.mpl_connect("motion_notify_event", hover)
canvas.mpl_connect("button_release_event", delete_confirm)

# placing the canvas on the Tkinter window
canvas.get_tk_widget().configure(highlightbackground='black',highlightthickness=2)

##### ARRANGE WIDGETS IN WINDOW #####

date_frame.grid(row=0,column=0,columnspan=4,pady=5,padx=5)
T1.grid(row=0,column=0,columnspan=4,padx=5,pady=5)
dropdown_year.grid(row=1,column=0,pady=5)
dropdown_months.grid(row=1,column=1)
dropdown_year2.grid(row=1,column=2)
dropdown_months2.grid(row=1,column=3)

selection_frame.grid(row=1, column=0,columnspan=4,padx=5)
label_avail.grid(row=0,column=0,padx=5)
label_select.grid(row=0,column=2,padx=5)
listbox.grid(row=1,rowspan=5,column=0,padx=5)
listbox2.grid(row=1,rowspan=5,column=2,padx=5)

add_button.grid(row=1,column=1,padx=5,pady=5)
addall_button.grid(row=2,column=1,padx=5,pady=5)
remove_button.grid(row=3,column=1,padx=5,pady=5)
clear_button.grid(row=4,column=1,padx=5,pady=5)
import_button.grid(row=5,column=1,padx=5,pady=5)

credit_frame.grid(row=2,column=0,columnspan=4,padx=5,pady=5)
creditlabel.grid(row=0,column=0)
link1.grid(row=0,column=1)

plot_frame.grid(row=0,rowspan=4,column=4,columnspan=1,padx=5,pady=5)
canvas.get_tk_widget().pack()

star_ha_frame.grid(row=0,column=5,columnspan=2,padx=5,pady=5)
dropdown_stars.grid(row=0,column=0)
ha_entry_box.grid(row=1,column=0,padx=5,pady=5)
export_button.grid(row=2,column=0,padx=5,pady=5)

offset_frame.grid(row=1, rowspan=2,column=5,columnspan=2,padx=5,pady=5)
offlabel.grid(row=0, column=0, padx=5, pady=5)
R1.grid(row=1,column=0,padx=5,pady=5)
R2.grid(row=2,column=0,padx=5,pady=5)
R3.grid(row=3,column=0,padx=5,pady=5)
R4.grid(row=4,column=0,padx=5,pady=5)
R5.grid(row=5,column=0,padx=5,pady=5)
offlabel2.grid(row=0,column=1, padx=5,pady=5)
offset1box.grid(row=1, column=1, padx=5,pady=5)
offset2box.grid(row=2, column=1, padx=5,pady=5)
offset3box.grid(row=3, column=1, padx=5,pady=5)
offset4box.grid(row=4, column=1, padx=5,pady=5)
offset5box.grid(row=5, column=1, padx=5,pady=5)
histo_button.grid(row=6,column=0,columnspan=2,padx=5,pady=10)

##### RUN #####
window.mainloop()