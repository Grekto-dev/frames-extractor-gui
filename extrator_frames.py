import sys
import os
import subprocess
import shutil
import tempfile
import logging
import cv2
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QFileDialog, QProgressBar, QScrollArea, 
                             QLabel, QCheckBox, QGraphicsView, QLayout,
                             QGraphicsScene, QGraphicsPixmapItem, QStackedWidget, 
                             QComboBox, QSplitter, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QRectF, QPoint, QSize, QRect, QSettings
from PyQt6.QtGui import QPixmap

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s',
    datefmt='%H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True
)
logger = logging.getLogger("Extrator")

TEXTS = {
    "pt": {
        "title": "Extrator de Frames Pro",
        "open": "Abrir Vídeo",
        "save_all": "Salvar Todos",
        "save_sel": "Salvar Selecionados",
        "sel_all": "Selecionar Todos",
        "format": "Formato:",
        "total": "Total: {} frames",
        "credits": "Desenvolvido por Pedro Nogueira. Versão 1.0.0",
        "instr": "Selecione um vídeo ou\nArraste e solte aqui",
        "extracting": "Extraindo frames...",
        "frame_cnt": "Frame: {:03d} / {:03d}",
        "zoom": "Zoom: {}%",
        "error": "Erro ao processar.",
        "save_diag": "Selecionar Pasta de Destino",
        "saved_log": "Salvo {} imagens",
        "lang_pt": "Português (Brasil)",
        "lang_en": "English (US)"
    },
    "en": {
        "title": "Frame Extractor Pro",
        "open": "Open Video",
        "save_all": "Save All",
        "save_sel": "Save Selected",
        "sel_all": "Select All",
        "format": "Format:",
        "total": "Total: {} frames",
        "credits": "Developed by Pedro Nogueira. Version 1.1.0",
        "instr": "Select a video or\nDrag and drop here",
        "extracting": "Extracting frames...",
        "frame_cnt": "Frame: {:03d} / {:03d}",
        "zoom": "Zoom: {}%",
        "error": "Processing error.",
        "save_diag": "Select Destination Folder",
        "saved_log": "Saved {} images",
        "lang_pt": "Portuguese (Brazil)",
        "lang_en": "English (US)"
    }
}

def check_dependencies():
    dependencies = {'PyQt6': 'PyQt6', 'cv2': 'opencv-python', 'PIL': 'Pillow'}
    missing = []
    for module, package in dependencies.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    
    if missing:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
            sys.exit()
        except Exception as e:
            sys.exit()

check_dependencies()

TEMP_PATH = os.path.join(tempfile.gettempdir(), "frame_extractor_v1_1")

def cleanup_temp():
    if os.path.exists(TEMP_PATH):
        try: shutil.rmtree(TEMP_PATH)
        except: pass

cleanup_temp()
try: os.makedirs(TEMP_PATH, exist_ok=True)
except: pass

class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, h_spacing=10, v_spacing=10):
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self._h_spacing = h_spacing
        self._v_spacing = v_spacing
        self._item_list = []

    def __del__(self):
        item = self.takeAt(0)
        while item: item = self.takeAt(0)

    def addItem(self, item):
        self._item_list.append(item)

    def count(self):
        return len(self._item_list)

    def itemAt(self, index):
        if 0 <= index < len(self._item_list): return self._item_list[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._item_list): return self._item_list.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return int(self._do_layout(QRectF(0, 0, width, 0), True))

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(QRectF(rect), False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())
        size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
        return size

    def _do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing_x = self._h_spacing
        spacing_y = self._v_spacing

        for item in self._item_list:
            wid = item.sizeHint().width()
            hei = item.sizeHint().height()
            
            next_x = x + wid + spacing_x
            if next_x - spacing_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + spacing_y
                next_x = x + wid + spacing_x
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(int(x), int(y), wid, hei))

            x = next_x
            line_height = max(line_height, hei)

        return y + line_height - rect.y()

class VideoWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)

    def __init__(self, path):
        super().__init__()
        self.path = path

    def run(self):
        frames = []
        try:
            logger.info(f"Lendo: {self.path}")
            cap = cv2.VideoCapture(self.path)
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            base = os.path.splitext(os.path.basename(self.path))[0]
            c = 0
            
            while cap.isOpened():
                ret, fr = cap.read()
                if not ret: break
                
                fname = os.path.join(TEMP_PATH, f"{base}_{c:03d}.jpg")
                cv2.imwrite(fname, fr)
                frames.append(fname)
                c += 1
                
                if total: self.progress.emit(int(c/total*100))
            cap.release()
            logger.info("Extração ok.")
        except Exception as e:
            logger.error(f"Erro Worker: {e}")
        self.finished.emit(frames)

class FrameThumb(QFrame):
    def __init__(self, idx, path, app):
        super().__init__()
        self.idx = idx
        self.path = path
        self.app = app
        self.setFixedSize(145, 175)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        
        l = QVBoxLayout(self)
        l.setContentsMargins(2,2,2,2)
        
        h = QHBoxLayout()
        self.chk = QCheckBox()
        lbl = QLabel(f"#{idx:03d}")
        lbl.setStyleSheet("color:blue; font-size:10px; font-weight:bold;")
        h.addWidget(self.chk)
        h.addStretch()
        h.addWidget(lbl)
        
        self.img = QLabel()
        self.img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pix = QPixmap(path).scaled(130, 130, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.img.setPixmap(pix)
        self.img.setCursor(Qt.CursorShape.PointingHandCursor)
        self.img.mousePressEvent = lambda e: self.app.set_frame(self.idx)
        
        l.addLayout(h)
        l.addWidget(self.img)

class ZoomView(QGraphicsView):
    def __init__(self, parent_app):
        super().__init__()
        self.parent_app = parent_app
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.z_lbl = QLabel("Zoom: 100%", self)
        self.z_lbl.setStyleSheet("background:rgba(0,0,0,0.6); color:white; padding:4px; font-weight:bold;")
        self.z_lbl.move(10,10)

    def show_img(self, path):
        self.scene.clear()
        pix = QPixmap(path)
        self.scene.addItem(QGraphicsPixmapItem(pix))
        self.setSceneRect(QRectF(pix.rect()))
        self.resetTransform()
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.upd_lbl()

    def wheelEvent(self, e):
        f = 1.25 if e.angleDelta().y()>0 else 0.8
        if self.transform().m11()*f < 0.5: f = 0.5/self.transform().m11()
        self.scale(f,f)
        self.upd_lbl()

    def upd_lbl(self):
        val = int(self.transform().m11()*100)
        t_fmt = TEXTS[self.parent_app.curr_lang]["zoom"]
        self.z_lbl.setText(t_fmt.format(val))
        self.z_lbl.adjustSize()

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("PedroApps", "FrameExtractor")
        self.curr_lang = self.settings.value("language", "pt")
        
        logger.info(f"Iniciando. Idioma: {self.curr_lang}")
        self.paths = []
        self.curr_idx = -1
        self.thumbs = []
        self.resize(1200, 800)
        self.setAcceptDrops(True)
        self.init_ui()
        self.retranslate_ui()

    def init_ui(self):
        w = QWidget()
        self.setCentralWidget(w)
        layout = QHBoxLayout(w)
        
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # --- ESQUERDA ---
        left = QWidget()
        l_lay = QVBoxLayout(left)
        
        self.cb_lang = QComboBox()
        self.cb_lang.addItem("Português (Brasil)", "pt")
        self.cb_lang.addItem("English (US)", "en")
        idx = self.cb_lang.findData(self.curr_lang)
        if idx >= 0: self.cb_lang.setCurrentIndex(idx)
        self.cb_lang.currentIndexChanged.connect(self.change_lang)
        
        self.btn_open = QPushButton()
        self.btn_open.clicked.connect(self.ask_file)
        
        h_btns = QHBoxLayout()
        self.b_save_all = QPushButton()
        self.b_save_sel = QPushButton()
        self.b_save_all.clicked.connect(lambda: self.save(True))
        self.b_save_sel.clicked.connect(lambda: self.save(False))
        h_btns.addWidget(self.b_save_all)
        h_btns.addWidget(self.b_save_sel)
        
        self.lbl_format = QLabel()
        self.fmt = QComboBox()
        self.fmt.addItems(["JPG", "PNG"])
        self.chk_all = QCheckBox()
        self.chk_all.stateChanged.connect(self.toggle_all)
        
        l_lay.addWidget(self.cb_lang)
        l_lay.addWidget(self.btn_open)
        l_lay.addLayout(h_btns)
        l_lay.addWidget(self.lbl_format)
        l_lay.addWidget(self.fmt)
        l_lay.addWidget(self.chk_all)
        
        self.pbar = QProgressBar()
        l_lay.addWidget(self.pbar)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.flow_layout = FlowLayout(self.scroll_content)
        self.scroll.setWidget(self.scroll_content)
        l_lay.addWidget(self.scroll)
        
        self.lbl_total = QLabel()
        l_lay.addWidget(self.lbl_total)
        
        # --- DIREITA ---
        right = QWidget()
        r_lay = QVBoxLayout(right)
        r_lay.setContentsMargins(5,5,5,5)
        
        self.lbl_credits = QLabel()
        self.lbl_credits.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_credits.setStyleSheet("color: #888; font-size: 10px; margin-bottom: 2px;")
        r_lay.addWidget(self.lbl_credits)
        
        self.stack = QStackedWidget()
        self.lbl_info = QLabel()
        self.lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_info.setStyleSheet("font-size:18px; color:#888; border:2px dashed #ccc; background:#f0f0f0;")
        self.view = ZoomView(self)
        self.stack.addWidget(self.lbl_info)
        self.stack.addWidget(self.view)
        r_lay.addWidget(self.stack, 1)
        
        self.lbl_curr_frame = QLabel("Frame: -- / --")
        self.lbl_curr_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_curr_frame.setStyleSheet("font-weight: bold; font-size: 14px; color: #333; margin: 5px 0;")
        r_lay.addWidget(self.lbl_curr_frame)

        nav = QHBoxLayout()
        self.btn_prev = QPushButton("<")
        self.btn_next = QPushButton(">")
        
        for b in [self.btn_prev, self.btn_next]:
            b.setFont(self.font())
            b.setStyleSheet("font-weight:bold; height:40px; font-size:16px;")
            b.setAutoRepeat(True)
            b.setAutoRepeatDelay(300)
            b.setAutoRepeatInterval(50)
            
        self.btn_prev.clicked.connect(lambda: self.nav(-1))
        self.btn_next.clicked.connect(lambda: self.nav(1))
        nav.addWidget(self.btn_prev)
        nav.addWidget(self.btn_next)
        r_lay.addLayout(nav)
        
        self.splitter.addWidget(left)
        self.splitter.addWidget(right)
        self.splitter.setSizes([300, 700])
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)
        
        layout.addWidget(self.splitter)
        self.enable_ui(False)

    def change_lang(self, index):
        self.curr_lang = self.cb_lang.itemData(index)
        self.settings.setValue("language", self.curr_lang)
        logger.info(f"Idioma alterado para: {self.curr_lang}")
        self.retranslate_ui()

    def retranslate_ui(self):
        t = TEXTS[self.curr_lang]
        self.setWindowTitle(t["title"])
        self.btn_open.setText(t["open"])
        self.b_save_all.setText(t["save_all"])
        self.b_save_sel.setText(t["save_sel"])
        self.chk_all.setText(t["sel_all"])
        self.lbl_format.setText(t["format"])
        self.lbl_credits.setText(t["credits"])
        
        # Textos dinâmicos
        if not self.paths:
            self.lbl_info.setText(t["instr"])
            self.lbl_total.setText(t["total"].format(0))
        else:
            self.lbl_total.setText(t["total"].format(len(self.paths)))
        
        # Atualiza zoom label
        self.view.upd_lbl()

    def enable_ui(self, on):
        for w in [self.b_save_all, self.b_save_sel, self.fmt, self.chk_all, self.btn_prev, self.btn_next]:
            w.setEnabled(on)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls(): e.acceptProposedAction()

    def dropEvent(self, e):
        u = e.mimeData().urls()
        if u:
            p = u[0].toLocalFile()
            if p.lower().endswith(('.mp4','.avi','.mkv','.mov')): 
                self.start_load(p)

    def ask_file(self):
        t = TEXTS[self.curr_lang]["open"]
        p, _ = QFileDialog.getOpenFileName(self, t, "", "Video (*.mp4 *.avi *.mkv *.mov)")
        if p: self.start_load(p)

    def start_load(self, path):
        while self.flow_layout.count():
            item = self.flow_layout.takeAt(0)
            w = item.widget()
            if w: w.deleteLater()
        
        self.thumbs = []
        self.curr_idx = -1
        self.enable_ui(False)
        self.stack.setCurrentIndex(0)
        self.lbl_info.setText(TEXTS[self.curr_lang]["extracting"])
        self.lbl_curr_frame.setText("Frame: -- / --")
        
        self.worker = VideoWorker(path)
        self.worker.progress.connect(self.pbar.setValue)
        self.worker.finished.connect(self.on_loaded)
        self.worker.start()

    def on_loaded(self, paths):
        self.paths = paths
        self.lbl_total.setText(TEXTS[self.curr_lang]["total"].format(len(paths)))
        
        for i, p in enumerate(paths):
            t = FrameThumb(i, p, self)
            self.flow_layout.addWidget(t)
            self.thumbs.append(t)
            
        if paths:
            self.enable_ui(True)
            self.set_frame(0)
            self.stack.setCurrentIndex(1)
        else:
            self.lbl_info.setText(TEXTS[self.curr_lang]["error"])

    def nav(self, d):
        n = self.curr_idx + d
        if 0 <= n < len(self.paths): self.set_frame(n)

    def set_frame(self, i):
        self.curr_idx = i
        self.view.show_img(self.paths[i])
        self.btn_prev.setEnabled(i > 0)
        self.btn_next.setEnabled(i < len(self.paths)-1)
        
        t_fmt = TEXTS[self.curr_lang]["frame_cnt"]
        self.lbl_curr_frame.setText(t_fmt.format(i, len(self.paths)-1))

    def toggle_all(self, s):
        for t in self.thumbs: t.chk.setChecked(s==2)

    def save(self, all_f):
        title = TEXTS[self.curr_lang]["save_diag"]
        dest = QFileDialog.getExistingDirectory(self, title)
        if not dest: return
            
        ext = self.fmt.currentText().lower()
        items = self.thumbs if all_f else [t for t in self.thumbs if t.chk.isChecked()]
        
        c = 0
        for t in items:
            try:
                n = os.path.basename(t.path).rsplit('.',1)[0] + f".{ext}"
                target = os.path.join(dest, n)
                img = cv2.imread(t.path)
                cv2.imwrite(target, img)
                c+=1
            except: pass
        
        logger.info(TEXTS[self.curr_lang]["saved_log"].format(c))

    def closeEvent(self, e):
        cleanup_temp()
        e.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()

    sys.exit(app.exec())
