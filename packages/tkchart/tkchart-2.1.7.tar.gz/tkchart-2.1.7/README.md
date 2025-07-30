[![Chinese](https://img.shields.io/badge/Language-中文-red)](https://github.com/Thisal-D/tkchart/blob/main/README_zh.md)


<div align="center">

[![tkchart](https://snyk.io/advisor/python/tkchart/badge.svg)](https://snyk.io/advisor/python/tkchart)

# tkchart 

### `v 2.1.7`

[![Downloads](https://static.pepy.tech/badge/tkchart)](https://pepy.tech/project/tkchart) ![Downloads last 6 month](https://static.pepy.tech/personalized-badge/tkchart?period=total&units=international_system&left_color=grey&right_color=BLUE&left_text=downloads%20last%206%20month) [![Downloads](https://static.pepy.tech/badge/tkchart/month)](https://pepy.tech/project/tkchart) [![Downloads](https://static.pepy.tech/badge/tkchart/week)](https://pepy.tech/project/tkchart)

![PyPI - License](https://img.shields.io/badge/license-MIT-blue)
![LOC](https://tokei.rs/b1/github/Thisal-D/tkchart?category=lines)
</div>

**<li>tkchart is a Python library for creating live updating line charts in tkinter.</li>**

---

### Features

- **Live Update**: Display live data with line charts.
- **Multiple Lines**: Support for plotting multiple lines on the same chart for easy comparison.
- **Color Customization**: Customize colors to match your application's design or data representation.
- **Font Customization**: Adjust fonts for text elements to enhance readability.
- **Dimension Customization**: Customize chart dimensions to fit various display sizes and layouts.

[**Check out what's new | Changes**](https://github.com/Thisal-D/tkchart/blob/main/CHANGES_en.md)

---

### Importing & Installation
* **Installation**
    ```
    pip install tkchart
    ```

* **Importing**
    ``` python
    import tkchart
    ```

---

### Simple Guide
- **import package**
    ``` python
    import tkchart
    ```

- **Create Line Chart and place the chart**
  ``` python
  chart = tkchart.LineChart(
      master=root,
      x_axis_values=("a", "b", "c", "d", "e", "f"),
      y_axis_values=(100, 900)
  )
  chart.place(x=10, y=10)
  ```

- **Create Line**
  ``` python
  line = tkchart.Line(master=chart)
  ```

- **Display Data**
  display data using a loop
    ``` python
    def loop():
        while True:
            random_data = random.choice(range(100, 900))
            chart.show_data(line=line, data=[random_data])
            time.sleep(1)
    
    #call the loop as thead
    theading.Thread(target=loop).start()
    ```

---

### Full Code Example
``` python
import tkchart #  <- import the package
import tkinter
import random
import threading
import time

#create window
root = tkinter.Tk()

#create chart
chart = tkchart.LineChart(
    master=root,
    x_axis_values=("a", "b", "c", "d", "e", "f"),
    y_axis_values=(100, 900)
)
chart.place(x=10, y=10) #place chrt

#create line
line = tkchart.Line(master=chart)

def loop():
    while True:
        random_data = random.choice(range(100, 900)) #get random data
        chart.show_data(line=line, data=[random_data]) # <- display data using chart 
        time.sleep(1) #wait 1 sec
        
#call the loop as thead
threading.Thread(target=loop).start()

root.mainloop()
```

---

### Links

- [**Documentation**](https://github.com/Thisal-D/tkchart/blob/main/documentation/)
    - [English](https://github.com/Thisal-D/tkchart/blob/main/documentation/DOCUMENTATION_en.md)
    - [chinese](https://github.com/Thisal-D/tkchart/blob/main/documentation/DOCUMENTATION_zh.md)
- **GitHub Repository :** [tkchart](https://github.com/Thisal-D/tkchart)

---

### Contributors
- [<img src="https://github.com/childeyouyu.png?size=25" width="25">](https://github.com/childeyouyu) [youyu](https://github.com/childeyouyu)
