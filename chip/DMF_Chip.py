from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtGui import QTransform

from chip.Electrode import Electrode
from chip.chip_layout import read_defination_from_csv_file
from chip.chip_array import id_array, id_position

ELECTRODES_ZOOM_FACTOR = 17


class DMF_Chip(QGraphicsScene):
    serialDataSignal = pyqtSignal()

    def __init__(self, dmf_chip_layout_file=None):
        super().__init__()
        self.scale_now = 1
        self.dmf_chip_layout_file = dmf_chip_layout_file
        self.trans = QTransform()
        self.id_array = id_array
        self.id_position = id_position
        self._pending_ctrl_right_queue = []
        self.addElectrodes()

    def _iter_electrodes(self):
        for item in self.items():
            if getattr(item, "name", None) == "Electrode":
                yield item

    def _electrode_by_id(self, electrode_id):
        for item in self._iter_electrodes():
            if item.ID == electrode_id:
                return item
        return None

    def set_electrode_state(self, electrode_id, drive=None, selected=None):
        item = self._electrode_by_id(electrode_id)
        if item is None:
            return
        if item.isPinned and (drive is False or selected is False):
            return
        if drive is not None:
            item.setDriveStatus(drive)
        if selected is not None:
            item.setSelected(selected)
        item.update()

    def pinned_ids(self):
        return [e.ID for e in self._iter_electrodes() if e.isPinned]

    def hardware_drive_ids(self):
        """下发硬件时使用的电极 ID：当前驱动 + 全部固定电极。"""
        ids = set(self.pinned_ids())
        for e in self._iter_electrodes():
            if e.isDrive:
                ids.add(e.ID)
        return list(ids)

    def _cancel_ctrl_right_pending(self):
        self._pending_ctrl_right_queue = []

    def _clear_all_electrode_drive_select(self):
        for item in self._iter_electrodes():
            if item.isPinned:
                continue
            item.setDriveStatus(False)
            item.setSelected(False)
            item.update()

    def flush_ctrl_right_pending(self):
        queue = self._pending_ctrl_right_queue
        self._pending_ctrl_right_queue = []
        if not queue:
            return
        self._clear_all_electrode_drive_select()
        seen_ids = set()
        for item in queue:
            if item.scene() is not self or item.ID in seen_ids:
                continue
            seen_ids.add(item.ID)
            item.setDriveStatus(True)
            item.setSelected(True)
            item.update()
        self.serialDataSignal.emit()

    def addElectrodes(self):
        self.electrode_list = read_defination_from_csv_file(self.dmf_chip_layout_file)
        for key, value in self.electrode_list.items():
            value = [i * ELECTRODES_ZOOM_FACTOR for i in value]
            x_cord = value[1::2]
            y_cord = [i * (-1) for i in value[2::2]]
            self.addItem(Electrode(None, (x_cord, y_cord), key))

    def mousePressEvent(self, event):
        item = self.itemAt(event.scenePos(), self.trans)
        if item is None:
            self._cancel_ctrl_right_pending()
            return
        if item.name != "Electrode":
            return

        if event.modifiers() == Qt.ControlModifier and event.button() == Qt.RightButton:
            self._pending_ctrl_right_queue.append(item)
            event.accept()
        elif event.button() == Qt.RightButton:
            self._cancel_ctrl_right_pending()
            for other in self._iter_electrodes():
                if other.ID != item.ID and not other.isPinned:
                    other.setDriveStatus(False)
                    other.setSelected(False)
                    other.update()
            item.changeDriveStatus()
            item.setSelected(True)
            event.accept()
            self.serialDataSignal.emit()
        elif event.button() == Qt.LeftButton:
            self._cancel_ctrl_right_pending()
            if event.modifiers() == Qt.ShiftModifier:
                item.togglePinned()
                event.accept()
                self.serialDataSignal.emit()
            elif not item.isPinned:
                item.changeSelectStatus()
                event.accept()
            else:
                event.accept()

    def data_transfer(self, datas):
        return_data = [0] * 16
        for data in datas:
            if data % 8 != 0:
                return_data[data // 8] += 2 ** (data % 8 - 1)
            else:
                return_data[data // 8 - 1] += 2 ** 7
        return return_data
