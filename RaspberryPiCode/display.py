import tkinter as tk
import numpy as np
import pyttsx3
import weights_parser as wp # type: ignore
import uart_com as uc # type: ignore 

class NeuralNetExplainerApp:
    def __init__(self):
        # --- Color palette ---
        self.C_BG             = "#2D3794"   # main window background
        self.C_BUTTON_ORANGE  = "#F59E0B"   # orange fill for enabled nodes
        self.C_BUTTON_OUTLINE = "#FFFFFF"   # white outline/text for all nodes
        self.C_TEXT           = "#FFFFFF"   # text color (always white)
        self.C_ENTRY_BG       = "#F0F3F5"   # entry background (light gray)
        self.C_ENTRY_FG       = "#1E3F6F"   # entry text color (dark accent)
        self.C_DISABLED_FILL  = self.C_BG   # disabled buttons use BG color

        # --- Setup TTS engine ---
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)

        # --- Setup main window ---
        self.root = tk.Tk()
        self.root.title("NeuroMachina")
        self.root.configure(bg=self.C_BG)
        self.root.attributes('-fullscreen', True)
        self.root.resizable(False, False)

        # --- Fonts ---
        self.font_entry = ("Segoe UI", 18)
        self.font_node  = ("Segoe UI", 14, "bold")

        # --- Title label ---
        title_label = tk.Label(
            self.root,
            text="NeuroMachina",
            font=("Segoe UI", 32, "bold"),
            bg=self.C_BG,
            fg=self.C_BUTTON_ORANGE
        )
        title_label.place(x=500, y=20)

        # --- Entry display ---
        entry_frame = tk.Frame(self.root, bg=self.C_BG, bd=2, relief="groove")
        entry_frame.place(x=230, y=80, width=800, height=60)

        self.entry = tk.Entry(
            entry_frame,
            font=self.font_entry,
            justify="center",
            bg=self.C_ENTRY_BG,
            fg=self.C_ENTRY_FG,
            bd=0,
            highlightthickness=0,
            insertbackground=self.C_ENTRY_FG
        )
        self.entry.place(x=5, y=5, width=790, height=50)

        # --- Canvas for all nodes & connecting lines ---
        self.canvas = tk.Canvas(
            self.root,
            bg=self.C_BG,
            highlightthickness=0
        )
        self.canvas.place(x=0, y=160, width=1000, height=540)

        # --- Coordinates for each layer ---
        input_x = 340
        A_y     = 120
        B_y     = 220
        LPAR_y  = 320  # ( button
        RPAR_y  = 420  # ) button

        layer2_x = 540
        L2_ys    = [40, 160, 280, 400]

        layer3_x = 740
        L3_ys    = [80, 250, 420]

        output_x = 940
        EX_y     = 250

        # --- Draw connecting lines ---
        for y2 in L2_ys:
            # Connect A, B, (, ) to layer 2
            self.canvas.create_line(input_x + 44, A_y, layer2_x - 44, y2, fill=self.C_BUTTON_OUTLINE, width=2)
            self.canvas.create_line(input_x + 44, B_y, layer2_x - 44, y2, fill=self.C_BUTTON_OUTLINE, width=2)
            self.canvas.create_line(input_x + 44, LPAR_y, layer2_x - 44, y2, fill=self.C_BUTTON_OUTLINE, width=2)
            self.canvas.create_line(input_x + 44, RPAR_y, layer2_x - 44, y2, fill=self.C_BUTTON_OUTLINE, width=2)

        for y2 in L2_ys:
            for y3 in L3_ys:
                self.canvas.create_line(layer2_x + 44, y2, layer3_x - 44, y3, fill=self.C_BUTTON_OUTLINE, width=2)

        for y3 in L3_ys:
            self.canvas.create_line(layer3_x + 44, y3, output_x - 44, EX_y, fill=self.C_BUTTON_OUTLINE, width=2)

        # --- Store button references for updating states ---
        self.buttons = {}

        # --- Helper to draw and track buttons ---
        def draw_node(center_x, center_y, label, callback, is_filled):
            left   = center_x - 44
            top    = center_y - 28
            right  = center_x + 44
            bottom = center_y + 28

            # All buttons start as disabled (white outline, no fill)
            fill_color = self.C_DISABLED_FILL
            outline_color = self.C_BUTTON_OUTLINE
            outline_width = 2
            text_color = self.C_TEXT

            # Draw the oval background/outline
            oval_id = self.canvas.create_oval(
                left, top, right, bottom,
                fill=fill_color,
                outline=outline_color,
                width=outline_width
            )
            # Draw the text label
            text_id = self.canvas.create_text(
                center_x, center_y,
                text=label,
                font=self.font_node,
                fill=text_color
            )
            
            # Store button info for state management
            self.buttons[label] = {
                'oval_id': oval_id,
                'text_id': text_id,
                'callback': callback,
                'center_x': center_x,
                'center_y': center_y,
                'enabled': False  # Start disabled, will be updated
            }
            
            # Bind mouse‐click on both oval and text to the callback
            self.canvas.tag_bind(oval_id, "<Button-1>", lambda e, lbl=label: self._button_click(lbl))
            self.canvas.tag_bind(text_id, "<Button-1>", lambda e, lbl=label: self._button_click(lbl))

        # --- Create small helper for inserting text into entry ---
        def make_insert_fn(txt):
            return lambda: self._insert(txt)

        # --- Layer 1 node definitions and coords (now with parentheses) ---
        layer1_defs   = [
            ("A", make_insert_fn("A"), True),
            ("B", make_insert_fn("B"), False),
            ("(", make_insert_fn("("), True),
            (")", make_insert_fn(")"), False)
        ]
        layer1_coords = [
            (input_x, A_y),
            (input_x, B_y),
            (input_x, LPAR_y),
            (input_x, RPAR_y)
        ]

        # --- Layer 2 node definitions and coords ---
        layer2_defs   = [
            ("AND", make_insert_fn("AND"), True),
            ("OR",  make_insert_fn("OR"),  False),
            ("NOT", make_insert_fn("NOT"),  True),
            ("XOR", make_insert_fn("XOR"), False)
        ]
        layer2_coords = [(layer2_x, y) for y in L2_ys]

        # --- Layer 3 node definitions and coords ---
        layer3_defs   = [
            ("←",      self._backspace,    True),
            ("CLEAR",  self._clear,        False),
            ("ENTER",  self._load_weights, True)
        ]
        layer3_coords = [(layer3_x, y) for y in L3_ys]

        # --- Layer 4 node definition and coord ---
        layer4_defs   = [
            ("EXPLAIN", self._explain, False)
        ]
        layer4_coords = [
            (output_x, EX_y)
        ]

        # --- Combine defs and coords for all layers ---
        all_defs   = layer1_defs + layer2_defs + layer3_defs + layer4_defs
        all_coords = layer1_coords + layer2_coords + layer3_coords + layer4_coords

        # --- Draw each node (oval + label) by zipping defs with coords ---
        for (lbl, cmd, _), (cx, cy) in zip(all_defs, all_coords):
            draw_node(
                center_x=cx,
                center_y=cy,
                label=lbl,
                callback=cmd,
                is_filled=False  # All start as outline-only
            )

        # Placeholder for loaded weights
        self.weights = None
        # List to store button inputs
        self.expression_parts = []
        
        # Initial button state update
        self._update_button_states()

    def _button_click(self, label):
        if self.buttons[label]['enabled']:
            self.buttons[label]['callback']()
            self._update_button_states()

    def _update_button_states(self):
        """Update the enabled state and appearance of all buttons based on current input"""
        last_part = self.expression_parts[-1] if self.expression_parts else None
        
        # Backspace is enabled when there's input
        self._set_button_state("←", bool(self.expression_parts))
        
        # A/B are enabled when:
        # - input is empty, or 
        # - last part is an operator (AND, OR, XOR, NOT), or
        # - last part is (
        vars_enabled = (not self.expression_parts) or (last_part in ["AND", "OR", "XOR", "NOT", "("])
        self._set_button_state("A", vars_enabled)
        self._set_button_state("B", vars_enabled)
        
        # Operators (AND, OR, XOR) are enabled after a variable (A, B) or )
        ops_enabled = last_part in ["A", "B", ")"]
        self._set_button_state("AND", ops_enabled)
        self._set_button_state("OR", ops_enabled)
        self._set_button_state("XOR", ops_enabled)
        
        # NOT is enabled when:
        # - input is empty, or
        # - last part is an operator (AND, OR, XOR, NOT), or
        # - last part is (
        not_enabled = (not self.expression_parts) or (last_part in ["AND", "OR", "XOR", "NOT", "("])
        self._set_button_state("NOT", not_enabled)
        
        # ( is enabled when:
        # - input is empty, or
        # - last part is an operator (AND, OR, XOR, NOT), or
        # - last part is (
        lpar_enabled = (not self.expression_parts) or (last_part in ["AND", "OR", "XOR", "NOT", "("])
        self._set_button_state("(", lpar_enabled)
        
        # ) is enabled when:
        # - there's at least one unmatched (, and
        # - last part is a variable (A, B) or )
        rpar_enabled = (self.expression_parts.count("(") > self.expression_parts.count(")")) and \
                      (last_part in ["A", "B", ")"])
        self._set_button_state(")", rpar_enabled)
        
        # CLEAR, ENTER, and EXPLAIN are always enabled
        self._set_button_state("CLEAR", True)
        self._set_button_state("ENTER", True)
        self._set_button_state("EXPLAIN", True)

    def _set_button_state(self, label, enabled):
        """Enable or disable a button and update its appearance"""
        btn = self.buttons[label]
        btn['enabled'] = enabled
        
        if enabled:
            # Enabled: orange fill, white outline, white text
            fill = self.C_BUTTON_ORANGE
            outline = self.C_BUTTON_OUTLINE
            outline_width = 0  # No outline when filled
            text_color = self.C_TEXT
        else:
            # Disabled: no fill, white outline, white text
            fill = self.C_DISABLED_FILL
            outline = self.C_BUTTON_OUTLINE
            outline_width = 2
            text_color = self.C_TEXT
        
        # Update oval appearance
        self.canvas.itemconfig(btn['oval_id'], 
                             fill=fill, 
                             outline=outline, 
                             width=outline_width)
        # Update text appearance
        self.canvas.itemconfig(btn['text_id'], fill=text_color)

    def _insert(self, txt):
        self.expression_parts.append(txt)
        self._update_entry()

    def _backspace(self):
        if self.expression_parts:
            self.expression_parts.pop()
            self._update_entry()

    def _clear(self):
        self.expression_parts = []
        self._update_entry()
        self.weights = None

    def _update_entry(self):
        """Update the entry widget with the current expression parts"""
        self.entry.delete(0, tk.END)
        self.entry.insert(0, " ".join(self.expression_parts))

    def _load_weights(self):
        expr = " ".join(self.expression_parts).strip().upper()
        print("Original expression:", expr)
        
        # Convert to lowercase and replace operators
        # expr = expr.lower()
        expr = expr.replace(" AND ", " & ")
        expr = expr.replace(" OR ", " | ")
        expr = expr.replace(" XOR ", " ^ ")
        expr = expr.replace(" NOT ", " ~ ")
        
        print("Converted expression:", expr)
        
        try:
            weights = wp.get_weights(expr)
            self.weights = weights
            self._speak(f"Weights loaded for {expr}")
        except Exception as e:
            print("Error loading weights:", e)
            self._speak("Error loading weights. Please check your expression.")
            self.weights = None

        weights = wp.get_weights(expr)
        self.weights = weights
        uc.send_weights(weights)
        return

    def _generate_explanation(self, expr):
        if self.weights is None:
            return "No weights loaded yet. Press ENTER to load the network weights for your function."
        if expr in ("AND", "OR"):
            w = self.weights["w"]
            b = self.weights["b"]
            return (
                f"For your {expr} function, two input levers labeled A and B are each "
                f"connected by strings with clamp tensions {w[0]} and {w[1]}. "
                f"The bias clamp holds the output lever down with tension {-b:.1f}. "
                "When both A and B pull, their combined force overcomes the bias, "
                "lifting the output lever. Otherwise, it stays down."
            )
        else:  # XOR
            return (
                "For XOR, the network has two hidden levers:\n"
                " • Hidden lever H1: pulls when A pulls stronger than B.\n"
                " • Hidden lever H2: pulls when B pulls stronger than A.\n"
                "Each hidden lever uses a clamp setting of zero bias so it only moves "
                "when difference is positive (ReLU action). "
                "Both hidden levers feed into the output lever via equal tensions. "
                "The output clamp bias of 0.5 ensures only one hidden activation "
                "lifts the output at a time, giving true if exactly one input is true."
            )

    def _speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def _explain(self):
        expr = " ".join(self.expression_parts).strip().upper()
        explanation = self._generate_explanation(expr)
        self._speak(explanation)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = NeuralNetExplainerApp()
    app.run()
