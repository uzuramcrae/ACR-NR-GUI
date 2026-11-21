import os
from pathlib import Path
import time
import tkinter as tk
from tkinter import ttk
import webbrowser


saved = Path(os.environ["LOCALAPPDATA"]) / "acr" / "Saved"
control = saved / "ACRNeuralRendering-control.txt"
status = saved / "ACRNeuralRendering-status.txt"

root = tk.Tk()
root.title("ACR · DLSS Neural Rendering")
root.attributes("-topmost", True)
body = ttk.Frame(root, padding=16)
body.grid(sticky="nsew")
values = {}
pending = None
feedback = tk.StringVar()
observed = tk.StringVar(value="ゲームからの応答を待っています")

try:
    previous = dict(line.split("=", 1) for line in control.read_text().splitlines() if "=" in line)
except OSError:
    previous = {}


def save():
    global pending
    pending = None
    lines = []
    for key, var in values.items():
        value = var.get().strip()
        lower, upper = bounds[key]
        try:
            number = float(value)
            if not lower <= number <= upper or (key in discrete and not number.is_integer()):
                raise ValueError
        except ValueError:
            if not value and key in optional:
                continue
            feedback.set(f"{key} は {lower}～{upper} の値を指定してください")
            return
        lines.append(f"{key}={number:.4f}")
    temp = control.with_suffix(".tmp")
    try:
        saved.mkdir(parents=True, exist_ok=True)
        temp.write_text("\n".join(lines) + "\n", encoding="ascii")
        os.replace(temp, control)
        feedback.set("")
    except OSError as exc:
        feedback.set(str(exc))


def schedule(*_):
    global pending
    if pending is not None:
        root.after_cancel(pending)
    pending = root.after(90, save)


def refresh():
    try:
        if time.time() - status.stat().st_mtime < 3:
            message = status.read_text(encoding="ascii").strip()
            if message:
                summary, _, details = message.partition(": ")
                label = "ゲーム内の値" if summary == "Verified CVars" else "一部の値を適用できませんでした"
                observed.set(label + "\n" + details.replace(", ", "\n"))
        else:
            observed.set("ゲームからの応答を待っています")
    except OSError:
        observed.set("ゲームからの応答を待っています")
    root.after(350, refresh)


fields = (
    ("Enable", "NRオン", "1", 0, 1, "check"),
    ("Intensity", "全体の強度", "1", 0, 1, "slider"),
    ("Passes", "処理回数", "3", 1, 3, "choice"),
    ("ExtraPassIntensityScale", "追加パスの強度", "1", 0, 1, "slider"),
    ("Style", "スタイル（0～2）", "", 0, 2, "choice"),
    ("ToneStrength", "トーンの強さ", "", 0, 1, "spin"),
    ("StructuralStrength", "細部の強調", "", 0, 1, "spin"),
)
bounds = {key: (low, high) for key, _, _, low, high, _ in fields}
optional = {"Style", "ToneStrength", "StructuralStrength"}
discrete = {"Enable", "Passes", "Style"}

for row, (key, label, default, low, high, kind) in enumerate(fields):
    var = tk.StringVar(value=previous.get(key, default))
    if key in discrete and var.get():
        var.set(str(int(float(var.get()))))
    values[key] = var
    ttk.Label(body, text=label).grid(row=row, column=0, sticky="w", pady=3)
    if kind == "check":
        widget = ttk.Checkbutton(body, variable=var, onvalue="1", offvalue="0")
    elif kind == "choice":
        choices = [str(value) for value in range(low, high + 1)]
        widget = ttk.Combobox(body, textvariable=var, values=([""] if key in optional else []) + choices,
                              width=7, state="readonly")
    else:
        widget = ttk.Spinbox(body, textvariable=var, from_=low, to=high, increment=0.05, width=7)
        if kind == "slider":
            slider = ttk.Scale(body, from_=low, to=high, length=150,
                               command=lambda value, var=var: var.set(f"{float(value):.2f}"))
            slider.set(float(previous.get(key, default)))
            slider.grid(row=row, column=2, padx=(8, 0))
    widget.grid(row=row, column=1, sticky="w", padx=(10, 0))
    var.trace_add("write", schedule)

ttk.Label(body, text="空欄の項目はGUIからの上書きを停止します。").grid(columnspan=3, sticky="w", pady=(12, 0))
ttk.Label(body, textvariable=feedback, wraplength=370).grid(columnspan=3, sticky="w")
ttk.Separator(body).grid(columnspan=3, sticky="ew", pady=8)
ttk.Label(body, textvariable=observed, justify="left").grid(columnspan=3, sticky="w")
release_dir = Path(__file__).resolve().parent.parent
credit_file = release_dir / "CREDITS.txt"
if credit_file.is_file():
    channel, url = credit_file.read_text(encoding="utf-8").splitlines()[:2]
    footer = ttk.Frame(body)
    footer.grid(columnspan=3, sticky="ew", pady=(12, 0))
    ttk.Label(footer, text=f"制作：{channel}").pack(side="left")
    ttk.Button(footer, text="チャンネル", command=lambda: webbrowser.open(url)).pack(side="left", padx=8)
    ttk.Button(footer, text="MIT License", command=lambda: os.startfile(release_dir / "LICENSE")).pack(side="left")
root.protocol("WM_DELETE_WINDOW", lambda: (save(), root.destroy()))
refresh()
root.mainloop()
