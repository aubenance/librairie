btns = ctk.CTkFrame(
    self.form_panel,
    fg_color="transparent"
)

btns.pack(fill="x", pady=15)

ctk.CTkButton(
    btns,
    text="💾 Enregistrer",
    height=40,
    command=self._save
).pack(side="left", expand=True, fill="x", padx=5)

ctk.CTkButton(
    btns,
    text="❌ Annuler",
    height=40,
    fg_color="red",
    command=self._clear_form
).pack(side="left", expand=True, fill="x", padx=5)