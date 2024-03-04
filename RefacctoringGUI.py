import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter import Label
from tkinter import Button

from CodeSmellDetector import CodeSmellDetector

code = ""
def open_file_dialog():
    file_path = tk.filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
    code_smell_detector = CodeSmellDetector(file_path)


window = tk.Tk()
window.geometry("1000x1000")
window.title("Code Smell Detector")
Label(window, text="Start by selecting a python file").pack()
Button(window, text="Open File", command=open_file_dialog).pack()
window.mainloop()

