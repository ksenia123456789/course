import ttkbootstrap as ttk
from gui.app import PlannerApp

if __name__ == "__main__":
    root = ttk.Window(themename="flatly")
    app = PlannerApp(root)
    root.mainloop()