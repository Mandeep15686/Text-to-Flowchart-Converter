import tkinter as tk
from tkinter import filedialog, messagebox
from pyflowchart import Flowchart
from graphviz import Digraph
import os
import re

class FlowchartApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text to Flowchart Converter")

        # Text widget for code input
        self.text_area = tk.Text(root, wrap=tk.WORD, height=20, width=70)
        self.text_area.pack(padx=10, pady=10)

        # Buttons frame
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=(0,10))

        tk.Button(btn_frame, text="Load from File",       command=self.load_file).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Convert to Flowchart", command=self.convert_to_flowchart).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Save as PNG",          command=lambda: self.save_flowchart_format('png')).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Save as SVG",          command=lambda: self.save_flowchart_format('svg')).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Save as PDF",          command=lambda: self.save_flowchart_format('pdf')).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Save as HTML",         command=lambda: self.save_flowchart_format('html')).pack(side=tk.LEFT, padx=5)

        self.gv: Digraph = None  # will hold our Graphviz object

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if path:
            with open(path, "r") as f:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, f.read())

    def convert_to_flowchart(self):
        code = self.text_area.get(1.0, tk.END)
        try:
            # Generate DSL and split
            fc  = Flowchart.from_code(code)
            dsl = fc.flowchart().strip()
            parts      = dsl.split("\n\n", 1)
            node_lines = parts[0].splitlines()
            edge_lines = parts[1].splitlines() if len(parts) > 1 else []

            # Build Graphviz Digraph
            g = Digraph("G", format="png")
            g.attr("graph", rankdir="TB")
            g.attr("node", fontname="Courier", fontsize="10", shape="box")

            shape_map = {
                "start":       ("oval", "lightgreen"),
                "end":         ("oval", "lightcoral"),
                "operation":   ("box", "lightblue"),
                "condition":   ("diamond", "lightyellow"),
                "inputoutput": ("parallelogram", "lightpink"),
                "subroutine":  ("rectangle", "lightgray")
            }

            # Parse & add nodes
            for line in node_lines:
                m = re.match(r"(\w+)=>(\w+)\s*:\s*(.+)", line)
                if not m: continue
                node_id, dsl_type, label = m.groups()
                shape, color = shape_map.get(dsl_type, ("box", "white"))
                g.node(node_id.strip(), label=label.strip(), shape=shape, style="filled", color=color)

            # Parse & add edges
            for line in edge_lines:
                m = re.match(r"(\w+)(?:\(([^)]*)\))?->(\w+)", line)
                if not m: continue
                src, cond, dst = m.groups()
                if cond:
                    g.edge(src.strip(), dst.strip(), label=cond.strip())
                else:
                    g.edge(src.strip(), dst.strip())

            # Add watermark
            g.node("watermark", label="Made by Mandeep Singh", shape="plaintext", fontcolor="gray", style="italic")

            self.gv = g
            # Render & open default PNG
            out_png = g.render("generated_flowchart", cleanup=True)
            os.startfile(out_png)

        except Exception as e:
            messagebox.showerror("Error", f"Conversion failed:\n{e}")

    def save_flowchart_format(self, fmt: str):
        if not self.gv:
            messagebox.showwarning("Warning", "Please convert to flowchart first.")
            return
        # ask for filename without extension
        path = filedialog.asksaveasfilename(defaultextension=f".{fmt}", filetypes=[(f"{fmt.upper()} files", f"*.{fmt}")])
        if not path:
            return
        base, ext = os.path.splitext(path)
        ext = ext.lower()
        if fmt == 'html':
            # render PNG then wrap
            self.gv.render(filename=base, format='png', cleanup=True)
            with open(f"{base}.html", "w") as html_file:
                html_file.write(f'<html><body><img src="{os.path.basename(base)}.png" alt="Flowchart"></body></html>')
        else:
            self.gv.render(filename=base, format=fmt, cleanup=True)
        messagebox.showinfo("Saved", f"Flowchart saved as:\n{path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FlowchartApp(root)
    root.mainloop()
