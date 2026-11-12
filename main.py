import tkinter as tk
from tkinter import ttk, messagebox
from functools import reduce
from time import perf_counter
import matplotlib.pyplot as plt


class Expense:
    def __init__(self, title, amount, category):
        self.title = title
        self.amount = amount
        self.category = category

    def details(self):
        return f"{self.title} | Rs.{self.amount:.2f} | {self.category}"


class FoodExpense(Expense):
    def __init__(self, title, amount, place):
        super().__init__(title, amount, "Food")
        self.place = place

    def details(self):
        return super().details() + f" | Place: {self.place}"


class ExpenseManager:
    def __init__(self, budget=0):
        self.budget = budget
        self.expenses = []

    def add_expense(self, expense):
        self.expenses.append(expense)

    def remove_expense(self, expense):
        self.expenses.remove(expense)

    def total(self):
        return reduce(lambda total, amount: total + amount,
                      map(lambda expense: expense.amount, self.expenses), 0)

    def filter_by_category(self, category):
        return list(filter(lambda expense: expense.category == category,
                           self.expenses))

    def category_totals(self):
        totals = {}
        for expense in self.expenses:
            totals[expense.category] = totals.get(expense.category, 0) + expense.amount
        return totals


# DAA: Bubble Sort only — sort expenses from lowest amount to highest.
def bubble_sort_by_amount(expenses):
    arr = expenses[:]
    n = len(arr)

    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            if arr[j].amount > arr[j + 1].amount:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break

    return arr


class ExpenseApp:
    CATEGORIES = ["All", "Food", "Travel", "Books", "Fun", "Rent", "Other"]

    def __init__(self, root):
        self.root = root
        self.root.title("Student Expense Manager - Bubble Sort")
        self.root.geometry("850x650")
        self.root.minsize(760, 580)
        self.manager = ExpenseManager()
        self.shown = []

        self.make_menu()
        self.make_budget_frame()
        self.make_form_frame()
        self.make_list_frame()
        self.make_bottom_frame()

        tk.Label(
            root,
            text="DAA Feature: Bubble Sort sorts expenses by amount (lowest to highest).",
            fg="gray"
        ).pack(side="bottom", pady=5)

        self.root.bind("<Return>", lambda event: self.add_expense())

    def make_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.destroy)
        menubar.add_cascade(label="File", menu=file_menu)

        chart_menu = tk.Menu(menubar, tearoff=0)
        chart_menu.add_command(label="Bar Chart", command=self.bar_chart)
        chart_menu.add_command(label="Pie Chart", command=self.pie_chart)
        menubar.add_cascade(label="Charts", menu=chart_menu)

        daa_menu = tk.Menu(menubar, tearoff=0)
        daa_menu.add_command(label="Measure Bubble Sort Time",
                             command=self.measure_bubble_sort)
        menubar.add_cascade(label="DAA", menu=daa_menu)

        self.root.config(menu=menubar)

    def make_budget_frame(self):
        frame = tk.Frame(self.root, pady=8)
        frame.pack(fill="x")
        tk.Label(frame, text="Monthly Budget (Rs.):").pack(side="left", padx=10)
        self.budget_entry = tk.Entry(frame, width=14)
        self.budget_entry.pack(side="left")
        tk.Button(frame, text="Set Budget", command=self.set_budget).pack(side="left", padx=8)

    def make_form_frame(self):
        frame = tk.LabelFrame(self.root, text="Add Expense", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        tk.Label(frame, text="Title").grid(row=0, column=0, sticky="w")
        self.title_entry = tk.Entry(frame, width=20)
        self.title_entry.grid(row=0, column=1, padx=5, pady=3)

        tk.Label(frame, text="Amount (Rs.)").grid(row=0, column=2, sticky="w")
        self.amount_entry = tk.Entry(frame, width=13)
        self.amount_entry.grid(row=0, column=3, padx=5, pady=3)

        tk.Label(frame, text="Category").grid(row=1, column=0, sticky="w")
        self.category_box = ttk.Combobox(
            frame, width=17,
            values=["Food", "Travel", "Books", "Fun", "Rent", "Other"],
            state="readonly"
        )
        self.category_box.current(0)
        self.category_box.grid(row=1, column=1, padx=5, pady=3)

        tk.Label(frame, text="Place (food only)").grid(row=1, column=2, sticky="w")
        self.place_entry = tk.Entry(frame, width=15)
        self.place_entry.grid(row=1, column=3, padx=5, pady=3)

        tk.Button(frame, text="Add Expense", bg="lightgreen",
                  command=self.add_expense).grid(row=2, column=0, columnspan=4, pady=6)

    def make_list_frame(self):
        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        controls = tk.Frame(frame)
        controls.pack(fill="x", pady=4)

        tk.Label(controls, text="Filter:").pack(side="left")
        self.filter_box = ttk.Combobox(
            controls, width=12, values=self.CATEGORIES, state="readonly"
        )
        self.filter_box.current(0)
        self.filter_box.pack(side="left", padx=5)
        self.filter_box.bind("<<ComboboxSelected>>", lambda event: self.refresh_list())

        tk.Button(controls, text="Sort by Amount (Bubble Sort)",
                  command=self.sort_expenses).pack(side="left", padx=10)
        tk.Button(controls, text="Measure Sort Time",
                  command=self.measure_bubble_sort).pack(side="right")

        list_frame = tk.Frame(frame)
        list_frame.pack(fill="both", expand=True)
        self.listbox = tk.Listbox(list_frame, height=12, font=("Consolas", 10))
        scroll = tk.Scrollbar(list_frame, command=self.listbox.yview)
        self.listbox.config(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.listbox.pack(side="left", fill="both", expand=True)

        self.popup = tk.Menu(self.root, tearoff=0)
        self.popup.add_command(label="Delete selected expense", command=self.delete_expense)
        self.listbox.bind("<Button-3>", self.show_popup)

    def make_bottom_frame(self):
        frame = tk.Frame(self.root, pady=5)
        frame.pack(fill="x", padx=10)
        self.summary_label = tk.Label(frame, text="Set a budget to begin",
                                      font=("Arial", 11, "bold"))
        self.summary_label.pack()
        tk.Label(
            frame,
            text="Bubble Sort Complexity: Best O(n), Average O(n²), Worst O(n²)",
            fg="navy", wraplength=800
        ).pack(pady=3)

    def set_budget(self):
        try:
            budget = float(self.budget_entry.get())
            if budget < 0:
                raise ValueError
            self.manager.budget = budget
        except ValueError:
            messagebox.showerror("Invalid budget", "Enter a valid non-negative budget.")
            return
        self.update_summary()

    def add_expense(self):
        title = self.title_entry.get().strip()
        category = self.category_box.get()
        if not title:
            messagebox.showwarning("Missing title", "Please enter an expense title.")
            return
        try:
            amount = float(self.amount_entry.get())
            if amount < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid amount", "Amount must be a non-negative number.")
            return

        if category == "Food":
            place = self.place_entry.get().strip() or "Not given"
            expense = FoodExpense(title, amount, place)
        else:
            expense = Expense(title, amount, category)

        self.manager.add_expense(expense)
        self.title_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.place_entry.delete(0, tk.END)
        self.refresh_list()
        self.update_summary()

        if self.manager.budget > 0 and self.manager.total() > self.manager.budget:
            messagebox.showwarning("Budget exceeded", "You have crossed your budget!")

    def show_popup(self, event):
        if not self.listbox.size():
            return
        index = self.listbox.nearest(event.y)
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(index)
        self.popup.post(event.x_root, event.y_root)

    def delete_expense(self):
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showinfo("Select expense", "Select an expense first.")
            return
        expense = self.shown[selected[0]]
        self.manager.remove_expense(expense)
        self.refresh_list()
        self.update_summary()

    def get_filtered_expenses(self):
        choice = self.filter_box.get()
        if choice == "All":
            return self.manager.expenses[:]
        return self.manager.filter_by_category(choice)

    def refresh_list(self):
        self.shown = self.get_filtered_expenses()
        self.listbox.delete(0, tk.END)
        for expense in self.shown:
            self.listbox.insert(tk.END, expense.details())

    def sort_expenses(self):
        self.shown = bubble_sort_by_amount(self.get_filtered_expenses())
        self.listbox.delete(0, tk.END)
        for expense in self.shown:
            self.listbox.insert(tk.END, expense.details())

    def update_summary(self):
        spent = self.manager.total()
        remaining = self.manager.budget - spent
        self.summary_label.config(
            text=f"Budget: Rs.{self.manager.budget:.2f}   "
                 f"Spent: Rs.{spent:.2f}   Remaining: Rs.{remaining:.2f}",
            fg="red" if remaining < 0 else "black"
        )

    def measure_bubble_sort(self):
        expenses = self.get_filtered_expenses()
        if len(expenses) < 2:
            messagebox.showinfo("Need more expenses",
                                "Add at least two expenses to measure Bubble Sort.")
            return

        start = perf_counter()
        bubble_sort_by_amount(expenses)
        elapsed_ms = (perf_counter() - start) * 1000
        n = len(expenses)

        messagebox.showinfo(
            "Bubble Sort Runtime",
            f"Number of expenses (n): {n}\n"
            f"Execution time: {elapsed_ms:.6f} milliseconds\n\n"
            "Best-case time: O(n)\nAverage-case time: O(n²)\n"
            "Worst-case time: O(n²)\nSpace: O(n) for copied list"
        )

        plt.figure("Bubble Sort Runtime")
        plt.bar(["Bubble Sort"], [elapsed_ms])
        plt.title(f"Bubble Sort Runtime for {n} Expenses")
        plt.ylabel("Execution Time (milliseconds)")
        plt.tight_layout()
        plt.show()

    def bar_chart(self):
        data = self.manager.category_totals()
        if not data:
            messagebox.showinfo("No data", "Add some expenses first.")
            return
        plt.figure("Expenses by Category")
        plt.bar(list(data.keys()), list(data.values()))
        plt.title("Spending by Category")
        plt.xlabel("Category")
        plt.ylabel("Amount (Rs.)")
        plt.tight_layout()
        plt.show()

    def pie_chart(self):
        data = self.manager.category_totals()
        if not data:
            messagebox.showinfo("No data", "Add some expenses first.")
            return
        plt.figure("Expense Distribution")
        plt.pie(list(data.values()), labels=list(data.keys()), autopct="%1.1f%%")
        plt.title("Expense Distribution")
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseApp(root)
    root.mainloop()