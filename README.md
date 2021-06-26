# erin-projects

# Changelog for baseline_offset_gui.py

06/25/2021

1. Fixed issue where starlogs failed to import due to wrong file extension; code now looks for "starLog" in filename regardless of file extension since they are raw text files.
2. Streamlined/refined the GUI design, including

      a. Removed "Plot Offsets" and "Plot Fit" buttons. Selecting a baseline using the colored will now plot - or remove from the plot - the data for that baseline
      
      b. Removed separate calculated offset displays - the text for the baseline checkboxes themselves will now display the calculated offsets if they are selected and an hour angle has been provided. **Baselines can be selected before data import has happened or before an hour angle/star has been provided; nothing should happen**.
         
      c. The checkboxes are the colors of the respective baselines as seen in Scope-Fringecon, and the colored area will gain a 3D appearance when an offset is selected.
      
      d. Clear selection now properly de-selects baselines, clears the plot, and resets the star dropdown/hour angle entry/offset displays to default values.
3. Updated layout to a vertical mostly one-column design.
