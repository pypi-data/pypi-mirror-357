# nicegui-pdf
A NiceGUI PDF component (using pdf.js) to nicely integrate PDFs without the need for iframes without having any control on which page is shown or without the possibility to read the seelcted text. Install with

`pip install nicegui-pdf`


A quick example on how to use the component is given next:

```python
from nicegui import ui, app
from nicegui_pdf import PdfViewer

# [...] 

state = {
    "current_page": 1,
}

# [...]

ui.number().bind_value(state, "current_page")

path = app.add_static_file(local_file="example/paper.pdf")
PdfViewer(path).classes("w-full").style(
    "border: solid 1px gray;"
).bind_current_page(
    state
)
```


# Features
- Full integration of PDF files into NiceGUI
- Two-way binding of `current_page`
- One-way binidng of `num_pages`, `is_rendering` and `selected_text`


A full example demonstrating all features is given in `example/main.py`:
<p align="center">
    <img src="https://raw.githubusercontent.com/peerdavid/nicegui-pdf/main/assets/screenshot.png" alt="table" width="700"/>
</p> 



## ToDo's
- [x] Integrate pdf.js and add a basic PDF viewer
- [x] Bind current page
- [x] Implement text overlay for selected text
- [x] Bind to selected text
- [x] Bind number of pages
- [x] Binding for is rendering
- [x] Resize PDF on window resize
- [ ] Bind path (load new pdf document)

Optional
- [ ] Highlight text
- [ ] Show outline 


## Disclaimer
I'm neither a JS, NiceGUI or VUE expert. I simply tested a few things and found that an older version of PDF.js can be integrated as a custom NiceGUI component. Therefore, I cannot give any warranty etc. but still I'm trying to maintain this code. If you find any bugs or have feature requests, please open an issue or a pull request.


## Donate
If you like it and want to buy me a coffee:

[![](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/donate/?hosted_button_id=Y4PDJU84LC3N2)

Thank you so much!

## References
- PDF.js (https://mozilla.github.io/pdf.js/)
