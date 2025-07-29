# SAUI 1.04
Documentation:
To call the main GUI client:
`from SAUIGEO import SAU`

---
`SAU.check()`
- Calling this ensures that the GUI has the .json configuration file with the theme elements. If not it will install the .json file.

---
`SAU.verify({Version})`
- This is a simple Dev Testing tool to ensure that your program SAU version matches the one that is installed on your PC.

---
`SAU.start()`
- This call returns all the Theme elements.
- Currently it returns a list with all the theme elements.

---
`SAU.set({Theme Style Nr})`
- This is going to select the themes that are pre made in the program.
- Currently doesn't work.  

---
`SAU.start()`<br>
This command provides a list.
var[i] = [default, button, combo, cred, scale, title, window_ui]<br>
If you need the button you would do this:
```
var = SAU.start()
button = var[1]

b1 = tk.Button({window name}, **button)
b1.pack()
```

---
## Example Code
```
from SAUIGEO import SAU
import tkinter as tk

#Verify function is not neccessary but if you want to ensure new UI elements work correctly this could be useful.
SAU_Version = 1.03
verify = SAU.verify(SAU_Version)

SAU.check()
a = SAU.start()
title = a[1]

window = tk.Tk()
l1.Label(window, text="test", **title)
l1.pack()

window.mainloop()
```