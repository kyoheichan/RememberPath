import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os

# データの保存先ファイル
DATA_FILE = "folders.json"

class FolderLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Win11 フォルダランチャー")
        self.root.geometry("600x500")

        # データを読み込む
        self.data = self.load_data()

        # --- UIの作成 ---
        # 1. 入力エリア
        input_frame = ttk.LabelFrame(self.root, text="新しいパスを登録", padding=10)
        input_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(input_frame, text="カテゴリー:").grid(row=0, column=0, sticky="w")
        self.cat_entry = ttk.Entry(input_frame)
        self.cat_entry.grid(row=0, column=1, sticky="ew", padx=5)
        self.cat_entry.insert(0, "仕事") # 初期値

        ttk.Label(input_frame, text="ラベル名:").grid(row=1, column=0, sticky="w")
        self.label_entry = ttk.Entry(input_frame)
        self.label_entry.grid(row=1, column=1, sticky="ew", padx=5)

        ttk.Label(input_frame, text="パス:").grid(row=2, column=0, sticky="w")
        self.path_entry = ttk.Entry(input_frame)
        self.path_entry.grid(row=2, column=1, sticky="ew", padx=5)
        
        # 参照ボタン（手入力も可能ですが、あると便利です）
        btn_browse = ttk.Button(input_frame, text="参照", command=self.browse_folder)
        btn_browse.grid(row=2, column=2)

        btn_add = ttk.Button(input_frame, text="追加登録", command=self.add_entry)
        btn_add.grid(row=3, column=1, pady=10)

        input_frame.columnconfigure(1, weight=1)

        # 2. 表示エリア (Treeview)
        list_frame = ttk.Frame(self.root)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # カテゴリーとラベルを階層表示できるTreeview
        self.tree = ttk.Treeview(list_frame, columns=("Path"), show="tree headings")
        self.tree.heading("#0", text="カテゴリー / ラベル")
        self.tree.heading("Path", text="フルパス")
        self.tree.pack(side="left", fill="both", expand=True)

        # スクロールバー
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # 3. 操作エリア
        btn_open = ttk.Button(self.root, text="選択したフォルダを開く", command=self.open_selected)
        btn_open.pack(pady=10)

        # ダブルクリックでも開けるようにする
        self.tree.bind("<Double-1>", lambda event: self.open_selected())

        # 初回表示
        self.refresh_tree()

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def add_entry(self):
        cat = self.cat_entry.get().strip()
        label = self.label_entry.get().strip()
        path = self.path_entry.get().strip()

        if not (cat and label and path):
            messagebox.showwarning("入力エラー", "すべての項目を入力してください。")
            return

        if cat not in self.data:
            self.data[cat] = []
        
        self.data[cat].append({"label": label, "path": path})
        self.save_data()
        self.refresh_tree()
        
        # 入力欄をクリア（カテゴリー以外）
        self.label_entry.delete(0, tk.END)
        self.path_entry.delete(0, tk.END)

    def refresh_tree(self):
        # 一旦全消去
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # カテゴリーごとに追加
        for cat, items in self.data.items():
            parent = self.tree.insert("", "end", text=cat, open=True)
            for entry in items:
                # 子要素としてラベルとパスを追加
                self.tree.insert(parent, "end", text=entry["label"], values=(entry["path"],))

    def open_selected(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        
        values = self.tree.item(selected_item[0], "values")
        if values:
            path = values[0]
            if os.path.exists(path):
                # Windowsの標準機能でフォルダを開く
                os.startfile(path)
            else:
                messagebox.showerror("エラー", f"パスが見つかりません:\n{path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FolderLauncher(root)
    root.mainloop()