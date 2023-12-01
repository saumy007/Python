import tkinter as tk

def show_selected_options():
    selected_options = [var1.get(), var2.get(), var3.get()]
    print("Selected Options:", selected_options)

# Create the main window
window = tk.Tk()
window.title("Checkbutton Example")

# Variables to store the state of each Checkbutton
var1 = tk.BooleanVar()
var2 = tk.BooleanVar()
var3 = tk.BooleanVar()

# Create Checkbuttons
checkbutton1 = tk.Checkbutton(window, text="Option 1", variable=var1)
checkbutton2 = tk.Checkbutton(window, text="Option 2", variable=var2)
checkbutton3 = tk.Checkbutton(window, text="Option 3", variable=var3)

# Button to show selected options
show_button = tk.Button(window, text="Show Selected Options", command=show_selected_options)

# Pack widgets
checkbutton1.pack()
checkbutton2.pack()
checkbutton3.pack()
show_button.pack()

# Start the main event loop
window.mainloop()
