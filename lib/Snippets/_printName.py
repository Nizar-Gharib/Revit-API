# -*- coding: utf-8 -*-
from pyrevit import script
output = script.get_output()

def button_name_click(btn_name):
    # 👀 Print Message
    output.print_md('## ✅️ {btn_name} was Clicked ✨'.format(btn_name=btn_name))  # <- Print MarkDown Heading 2
    output.print_md('---')
    output.print_md('My name is Nizar')  # <- Print MarkDown Heading 2
    output.print_md('*You can Duplicate, or use this placeholder for your own script.*')