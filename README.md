# erin-projects

# Changelog for baseline_offset_gui.py

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
