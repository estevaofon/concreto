import tkinter as tk
from tkinter import W, ttk
from tkinter import messagebox
from PIL import ImageTk,Image
from elementoViga import Viga

class App():
    """Gui da Viga Calculator"""
    def __init__(self, toplevel):
        self.raiz = toplevel
        self.raiz.title('Calculadora de Viga')
        # define tamanho da janela
        self.raiz.geometry("610x500")
        # impede redimensionar a janela
        self.raiz.resizable(False, False)
        self.create_widgets()

    def calcular_viga(self):
        """
        Dimensiona a viga
        """
        msk = self.msk_entry.get()
        msk = float(msk) if msk else 0
        vsk = self.vsk_entry.get()
        vsk = float(vsk) if vsk else 0
        tsk = self.tsk_entry.get()
        tsk = float(tsk) if tsk else 0
        h = int(self.h_entry.get())
        b = int(self.b_entry.get())
        fck = int(self.Combo_fck.get())
        bitola = float(self.Combo_bitola.get())
        cobrimento = int(self.Combo_cobrimento.get())
        bitola_estribo = float(self.Combo_bitola_estribo.get())
        viga = Viga(bw=b, h=h, fck=fck, fyk=500, Msk=msk, Vsk=vsk,
        cobrimento=cobrimento, brita=1, dt=bitola_estribo, bitola=bitola, 
        teta=45, Tsk=tsk)
        viga.dimensionar_viga()
        viga.desenhar_viga()
        self.change_image()
        self.report_window(viga)
    
    def report_window(self, viga):
        """Emiti relatória da viga"""
        window = tk.Toplevel()
        window.geometry("500x500")
        window.resizable(False, False)
        window.title("Relatório da viga")
        frame1 = tk.Frame(window)
        frame1.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        frame2 = tk.Frame(window)
        frame2.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        message_list = [f"As (cm2): {viga.As*10**4:.2f}", f"Domínio: {viga.dominio()}", 
        f"kmd: {viga.kmd:.2f}", f"kz: {viga.kz:.2f}", f"kx: {viga.kx:.2f}", 
        f"Armadura mínima: {viga.test_min_steelarea()}", f"Armadura máxima: {viga.test_max_steelarea()}",
        f"Dutilidade: {viga.teste_dutilidade()}", f"VRd2: {viga.VRd2/10**3:.2f} kN",
        f"Bielas comprimidas: {viga.verificar_bielas_transversal()}",
        f"Vc: {viga.Vc/10**3:.2f} kN", f"Uso de Aswmin: {viga.conferir_aswmin()}", 
        f"Aswmin: {viga.Aswmin:.2f} cm2/m",f"Asw90: {viga.calcular_asw90():.2f} cm2/m"]

        for msg in message_list:
            self.create_new_label(frame1, msg)

        message_list = ["Torção", f"Bielas comprimidas: {viga.verificar_bielas_torcao()}", 
        f"TRD2: {(viga.TRd2/10**3):.2f} kN.m",
        f"As long. min: {viga.Asmin_longitudinal_torcao:.2f} cm2/m", 
        f"As trans min: {viga.Asmin_transveral_torcao:.2f} cm2/m",
         f"As long. min: {viga.verificar_Asmin_longitudinal_torcao()}", 
        f"As trans min: {viga.verificar_Asmin_transversal_torcao()}", 
        f"As long.: {viga.As_longitudinal_torcao*100:.2f} cm2/m",
        f"As trans.: {viga.As_transversal_torcao*100:.2f} cm2/m",
        f"face tracionada As long Total: {viga.Aslong_face_tracionada_total:.2f} cm2",
        f"face comprimida As long Total: {viga.Aslong_face_comprimida_total:.2f} cm2",
        f"face lateral As long Total: {viga.Aslong_face_lateral_total:.2f} cm2",
        f"As trasnversal Total {viga.aswtotal*100:.2f} cm2/m",
        ]

        for msg in message_list:
            self.create_new_label(frame2, msg)


    def create_new_label(self, parent_frame, msg=""):
        """Método para automação da criação dos labels"""
        frame = tk.Frame(parent_frame)
        frame.pack(fill=tk.BOTH, padx=10, pady=5)
        frame_label = ttk.Label(frame, text=msg)
        frame_label.pack(side=tk.LEFT)


    def create_widgets(self):
        """Cria os frames"""
        self.frame_dados = tk.Frame(self.raiz)
        self.frame_dados.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=10, pady=15)
        self.frame1 = tk.Frame(self.raiz)
        self.frame1.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.frame_longitudinal = tk.Frame(self.frame_dados)
        self.frame_longitudinal.pack(fill=tk.BOTH, padx=10, pady=5)
        self.frame2 = tk.Frame(self.frame_dados)
        self.frame2.pack(fill=tk.BOTH, padx=10, pady=5)
        self.frame3 = tk.Frame(self.frame_dados)
        self.frame3.pack(fill=tk.BOTH, padx=10, pady=5)
        self.frame5 = tk.Frame(self.frame_dados)
        self.frame5.pack(fill=tk.BOTH, padx=10, pady=5)
        self.frame6 = tk.Frame(self.frame_dados)
        self.frame6.pack(fill=tk.BOTH, padx=10, pady=5)
        self.frame7 = tk.Frame(self.frame_dados)
        self.frame7.pack(fill=tk.BOTH, padx=10, pady=5)
        self.frame8 = tk.Frame(self.frame_dados)
        self.frame8.pack(fill=tk.BOTH, padx=10, pady=5)
        self.frame_transversal = tk.Frame(self.frame_dados)
        self.frame_transversal.pack(fill=tk.BOTH, padx=10, pady=5)
        self.frame_transversal_data = tk.Frame(self.frame_dados)
        self.frame_transversal_data.pack(fill=tk.BOTH, padx=10, pady=5)
        self.frame_combo_estribo = tk.Frame(self.frame_dados)
        self.frame_combo_estribo.pack(fill=tk.BOTH, padx=10, pady=5)
        self.frame_torcao = tk.Frame(self.frame_dados)
        self.frame_torcao.pack(fill=tk.BOTH, padx=10, pady=5)
        self.frame_torcao_data = tk.Frame(self.frame_dados)
        self.frame_torcao_data.pack(fill=tk.BOTH, padx=10, pady=5)
        self.frame4 = tk.Frame(self.frame_dados)
        self.frame4.pack(fill=tk.BOTH, padx=10, pady=5)

        self.img = ImageTk.PhotoImage(Image.open("viga.png"))
        self.panel = ttk.Label(self.frame1, image = self.img)
        self.panel.pack(side=tk.LEFT)
        
        self.longitudinal_label = ttk.Label(self.frame_longitudinal, text="ARMADURA LONGITUDINAL")
        self.longitudinal_label.pack(side=tk.LEFT)

        # Momento
        self.msk_label = ttk.Label(self.frame2, text="Msk (kN.m)")
        self.msk_label.pack(side=tk.LEFT)
        self.msk_entry = ttk.Entry(self.frame2, width=11)
        self.msk_entry.pack(side=tk.RIGHT)

        # H altura
        self.h_label = ttk.Label(self.frame3, text="H (mm)")
        self.h_label.pack(side=tk.LEFT)
        self.h_entry = ttk.Entry(self.frame3, width=11)
        self.h_entry.pack(side=tk.RIGHT)

        # B altura
        self.b_label = ttk.Label(self.frame5, text="B (mm)")
        self.b_label.pack(side=tk.LEFT)
        self.b_entry = ttk.Entry(self.frame5, width=11)
        self.b_entry.pack(side=tk.RIGHT)

        # comboBox
        self.fck_label = ttk.Label(self.frame6, text="fck")
        self.fck_label.pack(side=tk.LEFT)
        fck_list = [20, 25, 30, 35, 40, 45, 50]
        self.Combo_fck = ttk.Combobox(self.frame6, values = fck_list, width=8)
        self.Combo_fck.current(1)
        self.Combo_fck.pack(side=tk.RIGHT)
        self.Combo_fck['state']='readonly'

        # comboBox
        self.bitola_label = ttk.Label(self.frame7, text="Bitola")
        self.bitola_label.pack(side=tk.LEFT)
        bitola_list = [8, 10, 12.5, 16, 20, 22, 25, 32]
        self.Combo_bitola = ttk.Combobox(self.frame7, values = bitola_list, width=8)
        self.Combo_bitola.current(1)
        self.Combo_bitola.pack(side=tk.RIGHT)
        self.Combo_bitola['state']='readonly'

        # comboBox
        self.cobrimento_label = ttk.Label(self.frame8, text="Cobrimento")
        self.cobrimento_label.pack(side=tk.LEFT)
        cobrimento_list = [20, 25, 30, 35, 40, 45, 50]
        self.Combo_cobrimento = ttk.Combobox(self.frame8, values = cobrimento_list, width=8)
        self.Combo_cobrimento.current(1)
        self.Combo_cobrimento.pack(side=tk.RIGHT)
        self.Combo_cobrimento['state']='readonly'

        self.longitudinal_label = ttk.Label(self.frame_transversal, text="ARMADURA TRANSVERSAL")
        self.longitudinal_label.pack(side=tk.LEFT)

        # Esforço transversal
        self.vsk_label = ttk.Label(self.frame_transversal_data, text="Vsk (kN)")
        self.vsk_label.pack(side=tk.LEFT)
        self.vsk_entry = ttk.Entry(self.frame_transversal_data, width=11)
        self.vsk_entry.pack(side=tk.RIGHT)

        # comboBox
        self.bitola_estribo_label = ttk.Label(self.frame_combo_estribo, text="Bitola do Estribo")
        self.bitola_estribo_label.pack(side=tk.LEFT)
        bitola_estribo_list = [5, 6.3, 8, 10, 12.5, 16, 20, 22, 25, 32]
        self.Combo_bitola_estribo = ttk.Combobox(self.frame_combo_estribo, values = bitola_estribo_list, width=8)
        self.Combo_bitola_estribo.current(1)
        self.Combo_bitola_estribo.pack(side=tk.RIGHT)
        self.Combo_bitola_estribo['state']='readonly'

        # Torção
        self.torcao_label = ttk.Label(self.frame_torcao, text="ARMADURA DE TORÇÃO")
        self.torcao_label.pack(side=tk.LEFT)

        # Esforço de torção
        self.tsk_label = ttk.Label(self.frame_torcao_data, text="Tsk (kN.m)")
        self.tsk_label.pack(side=tk.LEFT)
        self.tsk_entry = ttk.Entry(self.frame_torcao_data, width=11)
        self.tsk_entry.pack(side=tk.RIGHT)

        # calcular button
        button = ttk.Button(self.frame4, text="Calcular", command=self.calcular_viga)
        button.pack(side=tk.RIGHT)

    def change_image(self):
        img2 = ImageTk.PhotoImage(Image.open("viga.png"))
        self.panel.configure(image=img2)
        self.panel.image = img2

raiz = tk.Tk()
app = App(raiz)
raiz.mainloop()