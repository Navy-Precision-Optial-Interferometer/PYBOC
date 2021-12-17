# erin-projects

# Changelog for offset_calculator_gui-1-5.py and PYBOC.exe

12/17/2021 - all requested features have now been implemented
1. Local data point deletion is now supported; right clicking a data point will prompt the user to confirm whether they want to delete it, and if yes, the point will be removed and the polynomial fit/offset estimate automatically updated. **This point deletion is LOCAL and will only persist in the current session of PYBOC; it must be done again if PYBOC is reopened. To permanently delete a point use the hover annotations to identify its starlog file and obs number and then manually delete it from the file.**
2. Carina now has a starlog archive file that will automatically update once per day. A separately compiled version of PYBOC is available that accomodates for the different directory/file structure of this archive.
3. The plot area now has the ipython navigation toolbar, however at present any zooming/panning/view modifications will be reset every time the hour angle/offset calculation updates.
4. Upon selecting a star all available data for that star in the imported logs will now be displayed; the user can then deselect/select baselines at will. Allows for more immediate confirmation of successful import/overview of data.

10/19/2021
1. Additional input boxes added next to the offset checkboxes to allow for adding an extra "diurnal" offset - e.g., if the offsets you are finding seem to be consistently about 200 microns off from what PYBOC is predicting, you can put that in these boxes and PYBOC will account for it.
2. If you hover over a data point on the plot, it will now display an annotation containing the name of the starlog file the data point came from and its observation number. This is to allow easy idenfitication and manual deletion of outlier points, since programmatic deletion proved very difficult.

10/04/2021

1. Now has automatic hour angle/offset calculation, which will update every 10 seconds.
2. Now filters somewhat better for outlier data points - mainly those "-1.000s." At this point, if you run into a point of legitimate data that appears to be an outlier that is significantly affecting the fit, the best solution is to find it in the starlog files and delete it. This will probably remain the best solution as point and click point deletion is Difficult.  I am working on adding a bit more interactivity/"meta"data to the plot that will make tracking these points down in the starlog files easier.
3. Now handles "empty" star logs - no data, just header - correctly.
4. Now handles missing observation type identifiers - I, C, ., B, etc. - by inserting an 'X'.
5. No more polynomial fits in the plot legend.
6. Updated the offset checkboxes to be more uniform in background color so b4 didn't stand out/seem like you couldn't use it.
7. Now has credit and link to the Confluence documentation page. Instructions in the GUI also updated.
8. If you select a baseline that doesn't have data in the selected starlogs - i.e, it's uniformly -1.000 for every data point - it will no longer plot, and the checkbox will automatically deselect.

08/13/2021

1. Updated histogram capability to instead plot histogram of FSNRs of all targets for a given baseline.
2. Updated data importing to more robustly check for/throw out incoherent scans (was previously only checking baselines 1/4).

08/11/2021

1. Changed flow of layout from vertical to horizontal to address clipping issues.
2. Added ability to plot a histogram of the offsets for a given baseline for all targets in the selected logs.
3. Added some logic to capture/prevent errors caused by reasonable use cases (i.e., selecting baselines before a star is selected) 
4. "Save figure" confirmed to work for whatever the currently displayed figure is.

06/25/2021

1. Fixed issue where starlogs failed to import due to wrong file extension; code now looks for "starLog" in filename regardless of file extension since they are raw text files.
2. Streamlined/refined the GUI design, including

      a. Removed "Plot Offsets" and "Plot Fit" buttons. Selecting a baseline using the colored will now plot - or remove from the plot - the data for that baseline
      
      b. Removed separate calculated offset displays - the text for the baseline checkboxes themselves will now display the calculated offsets if they are selected and an hour angle has been provided. **Baselines can be selected before data import has happened or before an hour angle/star has been provided; nothing should happen**.
         
      c. The checkboxes are the colors of the respective baselines as seen in Scope-Fringecon, and the colored area will gain a 3D appearance when an offset is selected.
      
      d. Clear selection now properly de-selects baselines, clears the plot, and resets the star dropdown/hour angle entry/offset displays to default values.
3. Updated layout to a vertical mostly one-column design.

4. Code has been organized/cleaned up and at least broad comments added to everything
