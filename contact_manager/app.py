import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from contact_manager.database import (
    init_db,
    add_contact,
    update_contact,
    delete_contact,
    get_contacts,
    import_from_csv
)

init_db()

class ContactManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Contact Manager')
        self.geometry('700x400')
        self.create_widgets()
        self.load_contacts()

    def create_widgets(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(fill='x')

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(top_frame, textvariable=self.search_var)
        search_entry.pack(side='left', padx=5, pady=5)
        search_entry.bind('<Return>', lambda e: self.load_contacts())

        sort_label = ttk.Label(top_frame, text='Sort by:')
        sort_label.pack(side='left', padx=(10,0))
        self.sort_var = tk.StringVar(value='first_name')
        sort_combo = ttk.Combobox(top_frame, textvariable=self.sort_var,
                                  values=['first_name','last_name','email'], width=12)
        sort_combo.pack(side='left', padx=5)
        sort_combo.bind('<<ComboboxSelected>>', lambda e: self.load_contacts())

        import_btn = ttk.Button(top_frame, text='Import CSV', command=self.import_csv)
        import_btn.pack(side='right', padx=5)

        add_btn = ttk.Button(top_frame, text='Add Contact', command=self.add_contact_dialog)
        add_btn.pack(side='right')

        columns = ('id','first_name','last_name','email','phone','address')
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=100)
        self.tree.pack(expand=True, fill='both')
        self.tree.bind('<Double-1>', lambda e: self.edit_selected())

        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill='x')
        edit_btn = ttk.Button(bottom_frame, text='Edit', command=self.edit_selected)
        edit_btn.pack(side='left', padx=5, pady=5)
        delete_btn = ttk.Button(bottom_frame, text='Delete', command=self.delete_selected)
        delete_btn.pack(side='left')

    def load_contacts(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        search = self.search_var.get().strip() or None
        order_by = self.sort_var.get()
        contacts = get_contacts(order_by=order_by, search=search)
        for c in contacts:
            self.tree.insert('', 'end', values=c)

    def add_contact_dialog(self, contact=None):
        dlg = tk.Toplevel(self)
        dlg.title('Contact' if contact else 'Add Contact')
        entries = {}
        fields = ['first_name','last_name','email','phone','address']
        for idx, field in enumerate(fields):
            ttk.Label(dlg, text=field.replace('_',' ').title()+':').grid(row=idx, column=0, padx=5, pady=5, sticky='e')
            var = tk.StringVar(value=contact[idx+1] if contact else '')
            ent = ttk.Entry(dlg, textvariable=var)
            ent.grid(row=idx, column=1, padx=5, pady=5, sticky='we')
            entries[field] = var
        dlg.grid_columnconfigure(1, weight=1)

        def save():
            data = {f:v.get() for f,v in entries.items()}
            if contact:
                update_contact(contact[0], data['first_name'], data['last_name'],
                               data['email'], data['phone'], data['address'])
            else:
                add_contact(data['first_name'], data['last_name'], data['email'],
                            data['phone'], data['address'])
            dlg.destroy()
            self.load_contacts()

        ttk.Button(dlg, text='Save', command=save).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def get_selected_contact(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning('Select Contact', 'No contact selected')
            return None
        return self.tree.item(item[0])['values']

    def edit_selected(self):
        contact = self.get_selected_contact()
        if contact:
            self.add_contact_dialog(contact)

    def delete_selected(self):
        contact = self.get_selected_contact()
        if contact:
            if messagebox.askyesno('Delete', 'Delete selected contact?'):
                delete_contact(contact[0])
                self.load_contacts()

    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[('CSV Files','*.csv')])
        if file_path:
            import_from_csv(file_path)
            self.load_contacts()
            messagebox.showinfo('Import', 'Contacts imported successfully')

if __name__ == '__main__':
    app = ContactManager()
    app.mainloop()
