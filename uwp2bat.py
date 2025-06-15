import wx
import subprocess
import os

def listar_uwp():
    cmd = [
        "powershell",
        "-Command",
        "Get-StartApps | ForEach-Object {\"$($_.Name)`t$($_.AppID)\"}"
    ]
    try:
        output = subprocess.check_output(cmd, text=True, encoding="cp1252")
        linhas = output.strip().split('\n')
        apps = []
        vistos = set()
        for linha in linhas:
            campos = linha.strip().split('\t')
            if len(campos) == 2:
                nome, appid = campos
                chave = (nome, appid)
                if chave not in vistos:
                    apps.append((nome, appid))
                    vistos.add(chave)
        return apps
    except Exception as e:
        wx.MessageBox(f"Erro ao listar UWP:\n{e}", "Erro", wx.OK | wx.ICON_ERROR)
        return []

class EditDialog(wx.Dialog):
    def __init__(self, parent, selected_items):
        super().__init__(parent, title="Confirm Selected UWPs", size=(600, 450))
        self.selected_items = selected_items
        self.edits = []

        self.config = wx.Config("uwp2bat")  # Persistência do app
        self.pasta_destino = self.config.Read("pasta_destino", defaultVal="")

        vbox = wx.BoxSizer(wx.VERTICAL)

        # Seletor de pasta e display do caminho
        pasta_box = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_choosedir = wx.Button(self, label="Select Folder")
        self.txt_folder_path = wx.TextCtrl(self, style=wx.TE_READONLY)
        pasta_box.Add(self.btn_choosedir, flag=wx.ALL, border=5)
        pasta_box.Add(self.txt_folder_path, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        vbox.Add(pasta_box, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # Se já tem pasta salva e válida, preenche campo e habilita botão
        if self.pasta_destino and os.path.isdir(self.pasta_destino):
            self.txt_folder_path.SetValue(self.pasta_destino)
            enable_generate = True
        else:
            self.pasta_destino = None
            enable_generate = False

        # Painel com lista editável
        panel = wx.Panel(self)
        scroll = wx.ScrolledWindow(panel, style=wx.VSCROLL | wx.HSCROLL)
        scroll.SetScrollRate(10, 10)
        self.list_sizer = wx.BoxSizer(wx.VERTICAL)
        scroll.SetSizer(self.list_sizer)

        for nome, appid in self.selected_items:
            hbox = wx.BoxSizer(wx.HORIZONTAL)
            txt_nome = wx.TextCtrl(scroll, value=nome, size=(250, -1))
            label_appid = wx.StaticText(scroll, label=appid)
            hbox.Add(txt_nome, proportion=0, flag=wx.ALL | wx.EXPAND, border=5)
            hbox.Add(label_appid, proportion=1, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
            self.list_sizer.Add(hbox, flag=wx.EXPAND)
            self.edits.append((txt_nome, nome, appid))

        panel_sizer = wx.BoxSizer(wx.VERTICAL)
        panel_sizer.Add(scroll, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
        panel.SetSizer(panel_sizer)

        vbox.Add(panel, proportion=1, flag=wx.EXPAND)

        # Botões
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_generate = wx.Button(self, label="Generate")
        if not enable_generate:
            self.btn_generate.Disable()
        btn_cancel = wx.Button(self, label="Cancel")
        btn_sizer.Add(self.btn_generate, flag=wx.ALL, border=5)
        btn_sizer.Add(btn_cancel, flag=wx.ALL, border=5)
        vbox.Add(btn_sizer, flag=wx.ALIGN_CENTER)

        self.SetSizer(vbox)

        # Bind eventos
        self.btn_choosedir.Bind(wx.EVT_BUTTON, self.on_choose_folder)
        self.btn_generate.Bind(wx.EVT_BUTTON, self.on_generate)
        btn_cancel.Bind(wx.EVT_BUTTON, self.on_cancel)
        self.Bind(wx.EVT_CLOSE, self.on_cancel)

    def on_choose_folder(self, event):
        dlg = wx.DirDialog(self, "Select folder to save .BAT files", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.pasta_destino = dlg.GetPath()
            self.txt_folder_path.SetValue(self.pasta_destino)
            self.btn_generate.Enable()
            self.config.Write("pasta_destino", self.pasta_destino)
            self.config.Flush()
        dlg.Destroy()

    def on_generate(self, event):
        if not self.pasta_destino:
            wx.MessageBox("Please select a folder before generating.", "Warning", wx.OK | wx.ICON_WARNING)
            return

        nomes_bat = [edit.GetValue().strip() for edit, _, _ in self.edits]
        appids = [appid for _, _, appid in self.edits]

        pasta_exec = self.pasta_destino
        if not os.path.exists(pasta_exec):
            os.makedirs(pasta_exec)

        for nome_bat, appid in zip(nomes_bat, appids):
            if not nome_bat:
                nome_bat = appid
            nome_bat = nome_bat.strip()
            arquivo_bat = os.path.join(pasta_exec, f"{nome_bat}.bat")
            with open(arquivo_bat, "w", encoding="utf-8") as f:
                f.write(f'explorer.exe shell:AppsFolder\\{appid}\n')

        wx.MessageBox(f"Arquivos .BAT gerados na pasta:\n{pasta_exec}", "Sucesso", wx.OK | wx.ICON_INFORMATION)
        self.EndModal(wx.ID_OK)

    def on_cancel(self, event):
        self.EndModal(wx.ID_CANCEL)

class UWPApp(wx.Frame):
    def __init__(self, *args, **kw):
        super(UWPApp, self).__init__(*args, **kw)

        self.SetTitle("uwp2bat")
        self.SetSize((800, 600))
        painel = wx.Panel(self)
        self.full_list = listar_uwp()
        self.marked = {}

        vbox = wx.BoxSizer(wx.VERTICAL)

        search_box = wx.BoxSizer(wx.HORIZONTAL)
        self.search_ctrl = wx.TextCtrl(painel)
        search_btn = wx.Button(painel, label="Search")
        search_btn.Bind(wx.EVT_BUTTON, self.on_search)
        search_box.Add(self.search_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        search_box.Add(search_btn, flag=wx.ALL, border=5)
        vbox.Add(search_box, flag=wx.EXPAND)

        self.scroll_area = wx.ScrolledWindow(painel, style=wx.VSCROLL | wx.HSCROLL)
        self.scroll_area.SetScrollRate(10, 10)
        self.scroll_sizer = wx.BoxSizer(wx.VERTICAL)
        self.scroll_area.SetSizer(self.scroll_sizer)
        vbox.Add(self.scroll_area, 1, flag=wx.EXPAND | wx.ALL, border=10)

        self.btn_gerar = wx.Button(painel, label="Generate Executables .BAT")
        self.btn_gerar.Bind(wx.EVT_BUTTON, self.on_open_edit_dialog)
        vbox.Add(self.btn_gerar, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border=10)

        painel.SetSizer(vbox)

        self.render_list(self.full_list)
        self.Centre()
        self.Show()

    def render_list(self, lista):
        for child in self.scroll_sizer.GetChildren():
            child.GetWindow().Destroy()
        self.scroll_sizer.Clear()

        self.checkbox_refs = []
        for nome, appid in lista:
            texto = f"{nome} ({appid})"
            chk = wx.CheckBox(self.scroll_area, label=texto)

            if self.marked.get(appid, False):
                chk.SetValue(True)

            chk.Bind(wx.EVT_CHECKBOX, lambda evt, p=appid: self.on_check(evt, p))
            self.checkbox_refs.append((chk, nome, appid))
            self.scroll_sizer.Add(chk, flag=wx.ALL | wx.EXPAND, border=5)

        self.scroll_area.Layout()
        self.scroll_area.FitInside()

    def on_check(self, event, appid):
        self.marked[appid] = event.IsChecked()

    def on_search(self, event):
        termo = self.search_ctrl.GetValue().lower().strip()
        if not termo:
            lista_filtrada = self.full_list
        else:
            lista_filtrada = [
                (nome, appid)
                for nome, appid in self.full_list
                if termo in nome.lower() or termo in appid.lower()
            ]
        self.render_list(lista_filtrada)

    def on_open_edit_dialog(self, event):
        selecionados = [(nome, appid) for appid, sel in self.marked.items() if sel for nome, p in self.full_list if p == appid]
        if not selecionados:
            wx.MessageBox("No UWP selected.", "Warning", wx.OK | wx.ICON_WARNING)
            return

        dlg = EditDialog(self, selecionados)
        dlg.ShowModal()
        dlg.Destroy()

if __name__ == "__main__":
    app = wx.App(False)
    frame = UWPApp(None)
    app.MainLoop()
