from tkflu import *


root = FluWindow()

theme_manager = FluThemeManager(root)

btn = FluButton(root, text="Button", mode="light", style="standard", command=lambda: theme_manager.toggle())
btn.pack()

root.mainloop()