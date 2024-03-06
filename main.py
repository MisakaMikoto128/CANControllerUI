import sys
import time

from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QStandardItemModel, QColor
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QMenu, QSystemTrayIcon, QTableWidgetItem, QHeaderView, QWidget
from PyQt5.QtWidgets import QApplication, QFrame, QHBoxLayout
from qfluentwidgets import FluentIcon as FIF, TableWidget, Theme, setTheme, SwitchButton, AvatarWidget, BodyLabel, \
    CaptionLabel, HyperlinkButton, isDarkTheme, FluentIcon, Action
from qfluentwidgets import InfoLevel, setThemeColor
from qfluentwidgets import (NavigationItemPosition, MessageBox, FluentWindow,
                            NavigationAvatarWidget, SubtitleLabel, setFont)
from qfluentwidgets.components.material import AcrylicMenu

from BMSDataType import *
from FluentQtTest import Ui_Form
from HDL_CAN import CANDev


class CANControllerInfo:
    """
    CAN 控制协议：

    会周期性发送数据到外界，否则超过2秒任务设备掉线

    电池状态和原来的相同

    充电器监控使用拓展帧：

    0x1AB01001:
    直流输出参数
    32bit 电压 0.01V 无符号
    16bit 电流 0.01A 无符号
    16bit 功率 1W 无符号

    0x1AB01002:
    AC1输入参数
    32bit 电压 0.01V 无符号
    16bit 电流 0.01A 无符号
    16bit 功率 1W 无符号

    0x1AB01003:
    AC2输入参数
    32bit 电压 0.01V 无符号
    16bit 电流 0.01A 无符号
    16bit 功率 1W 无符号

    0x1AB01004:
    AC总功率
    32bit 功率 1W 无符号
    保留

    0x1AB01008:
    直流充电器的状态码：
    16bit 状态码
    32bit 设置的电压
    16bit 设置的电流

    控制：
    0x1AB01100:
    设置输出电压电流：
    32bit 输出电压 0.01V 无符号
    16bit 输出电流 0.01A 无符号
    保留

    0x1AB01101:
    控制输出:
    8bit 0 关闭输出，1启动输出
    保留
    """

    AC1Volt = 0
    AC1Curr = 0
    AC1Power = 0
    AC2Volt = 0
    AC2Curr = 0
    AC2Power = 0
    DC1Volt = 0
    DC1Curr = 0
    DC1Power = 0
    ACTotalPower = 0

    ChargerState = 0
    ChargerVolt = 0
    ChargerCurr = 0
    MaxChargerCurr = 0
    MaxChargerVolt = 0
    MaxChargePower = 0

    Temperature = 0


class MainWindow(QFrame, Ui_Form):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # loadUi('FluentQtTest.ui', self)  # Load the UI file
        self.setupUi(self)

        setThemeColor('#28afe9')

        # self.setTitleBar(SplitTitleBar(self))
        # self.titleBar.raise_()
        # self.windowEffect.setMicaEffect(self.winId(), isDarkMode=False)
        #
        # self.setWindowTitle('充电控制器上位机')
        # self.setWindowIcon(QIcon('./img/star.png'))

        # 添加一个退出菜单项
        exitAction = QAction(QIcon('./img/sp-exit.png'), 'Exit', self)
        exitAction.triggered.connect(self.close)

        # 创建托盘菜单
        trayMenu = QMenu(self)
        trayMenu.addAction(exitAction)

        # 创建系统托盘图标
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setIcon(QIcon('./img/star.png'))
        self.trayIcon.setContextMenu(trayMenu)
        self.trayIcon.show()

        self.can_device = CANDev()  # Create an instance of your CAN device
        self.canController_info = CANControllerInfo()
        self.bms_210h = BMS_210h_t()
        self.bms_20Ah = BMS_20Ah_t()
        self.bms_212h = BMS_212h_t()
        self.bms_214h = BMS_214h_t()
        self.bms_216h = BMS_216h_t()
        self.obc_300h = THREE_OBC_300h_t()
        self.bms_200h = BMS_200h_t()
        self.bms_202h = BMS_202h_t()
        self.bms_20Ch = BMS_20Ch_t()

        # enable border
        self.TableWidget_Charger.setBorderVisible(True)
        self.TableWidget_Charger.setBorderRadius(8)
        self.TableWidget_Charger.setWordWrap(False)
        self.TableWidget_Charger.setColumnCount(3)
        # 禁止编辑
        self.TableWidget_Charger.setEditTriggers(TableWidget.NoEditTriggers)
        self.TableWidget_Charger.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.TableWidget_Battery.setBorderVisible(True)
        self.TableWidget_Battery.setBorderRadius(8)
        self.TableWidget_Battery.setWordWrap(False)
        self.TableWidget_Battery.setColumnCount(3)
        self.TableWidget_Battery.setEditTriggers(TableWidget.NoEditTriggers)
        self.TableWidget_Battery.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.DoubleSpinBox_Volt.setValue(320)
        self.DoubleSpinBox_Curr.setValue(10)

        # Connect signals with slots
        self.ToggleButtonCAN.clicked.connect(self.toggleCAN)
        self.PushButton_SetVoltCurr.clicked.connect(self.printVoltCurrValues)
        self.PushButton_OpenDCOutput.clicked.connect(lambda: self.printChargerState(True))
        self.PushButton_CloseDCOutput.clicked.connect(lambda: self.printChargerState(False))
        self.PushButton_stage1.clicked.connect(lambda: self.confirmAction("Stage 1"))
        self.PushButton_stage2.clicked.connect(lambda: self.confirmAction("Stage 2"))
        self.PushButton_stage3.clicked.connect(lambda: self.confirmAction("Stage 3"))
        self.PushButton_stage4.clicked.connect(lambda: self.confirmAction("Stage 4"))

        # Start timer for checking data
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.checkForData)
        self.timer.start(10)  # Check for data every second

        self.timerCANHeart = QTimer(self)
        self.timerCANHeart.timeout.connect(self.CANHeartBeat)
        self.timerCANHeart.start(1000)  # Send CAN heart beat every second

        self.timerUpdateTableWiget = QTimer(self)
        self.timerUpdateTableWiget.timeout.connect(self.updateTableWiget)
        self.timerUpdateTableWiget.start(150)  # Send CAN heart beat every second

        self.IconInfoBadge_CAN1.setLevel(InfoLevel.INFOAMTION)
        self.IconInfoBadge_CAN2.setLevel(InfoLevel.INFOAMTION)
        self.timerCheckCAN1Connection = QTimer(self)
        self.timerCheckCAN1Connection.timeout.connect(lambda: self.IconInfoBadge_CAN1.setLevel(InfoLevel.INFOAMTION))
        self.timerCheckCAN1Connection.start(500)  # Send CAN heart beat every second
        self.timerCheckCAN2Connection = QTimer(self)
        self.timerCheckCAN2Connection.timeout.connect(lambda: self.IconInfoBadge_CAN2.setLevel(InfoLevel.INFOAMTION))
        self.timerCheckCAN2Connection.start(500)

    def toggleCAN(self):
        if self.ToggleButtonCAN.isChecked():
            if self.can_device.open_device():
                self.ToggleButtonCAN.setText('关闭CAN')
            else:
                self.ToggleButtonCAN.setChecked(False)
        else:
            self.can_device.close_device()
            self.ToggleButtonCAN.setText('打开CAN')

    def CANHeartBeat(self):
        self.can_device.send_data_ch1(0x1AB01103, bytes([0, 0, 0, 0, 0, 0, 0, 0]))

    def updateTableWiget(self):
        self.update_BodyLabel_Charger()
        self.update_BodyLabel_Battery()
        if self.canController_info.ChargerState == 0:
            self.SwitchButton_Charger.setChecked(False)
        else:
            self.SwitchButton_Charger.setChecked(True)

        if self.bms_202h.BMS_Precharge_anode_Relay_status == 2:
            self.SwitchButton.setChecked(True)
        else:
            self.SwitchButton.setChecked(False)

        if self.bms_202h.BMS_DischargeAnodeRelay_status == 2:
            self.SwitchButton_2.setChecked(True)
        else:
            self.SwitchButton_2.setChecked(False)

    def checkForData(self):
        if self.can_device.isCanOpen:
            can_msg_list1, ret1 = self.can_device.read_ch1()
            can_msg_list2, ret2 = self.can_device.read_ch2()

            if ret1 < 0:
                self.ToggleButtonCAN.setChecked(False)
                self.toggleCAN()
            elif ret1 > 0:
                self.IconInfoBadge_CAN1.setLevel(InfoLevel.SUCCESS)
                # 重置定时器避免触发超时事件
                self.timerCheckCAN1Connection.start(500)

            if ret2 < 0:
                self.ToggleButtonCAN.setChecked(False)
                self.toggleCAN()
            elif ret2 > 0:
                self.IconInfoBadge_CAN2.setLevel(InfoLevel.SUCCESS)
                # 重置定时器避免触发超时事件
                self.timerCheckCAN2Connection.start(500)

            for can_msg in can_msg_list1:
                if can_msg:
                    if can_msg.can_id == 0x1AB01001:
                        self.canController_info.DC1Volt = int.from_bytes(can_msg.data[0:4], 'big') / 100
                        self.canController_info.DC1Curr = int.from_bytes(can_msg.data[4:6], 'big') / 100
                        self.canController_info.DC1Power = int.from_bytes(can_msg.data[6:8], 'big')
                    elif can_msg.can_id == 0x1AB01002:
                        self.canController_info.AC1Volt = int.from_bytes(can_msg.data[0:4], 'big') / 100
                        self.canController_info.AC1Curr = int.from_bytes(can_msg.data[4:6], 'big') / 100
                        self.canController_info.AC1Power = int.from_bytes(can_msg.data[6:8], 'big')
                    elif can_msg.can_id == 0x1AB01003:
                        self.canController_info.AC2Volt = int.from_bytes(can_msg.data[0:4], 'big') / 100
                        self.canController_info.AC2Curr = int.from_bytes(can_msg.data[4:6], 'big') / 100
                        self.canController_info.AC2Power = int.from_bytes(can_msg.data[6:8], 'big')
                    elif can_msg.can_id == 0x1AB01004:
                        self.canController_info.ACTotalPower = int.from_bytes(can_msg.data[0:4], 'big')
                    elif can_msg.can_id == 0x1AB01008:
                        self.canController_info.ChargerState = int.from_bytes(can_msg.data[0:2], 'big')
                        self.canController_info.ChargerVolt = int.from_bytes(can_msg.data[2:6], 'big') / 100
                        self.canController_info.ChargerCurr = int.from_bytes(can_msg.data[6:8], 'big') / 100
                    elif can_msg.can_id == 0x1AB0100A:
                        self.canController_info.Temperature = int.from_bytes(can_msg.data[0:1], 'big')
                    elif can_msg.can_id == 0x1AB0100B:
                        self.canController_info.MaxChargerCurr = int.from_bytes(can_msg.data[0:2], 'big')
                        self.canController_info.MaxChargerVolt = int.from_bytes(can_msg.data[2:4], 'big')
                        self.canController_info.MaxChargePower = int.from_bytes(can_msg.data[4:6], 'big')

                    elif can_msg.can_id == 0x1AB0210:
                        if not BMS_210h_t_Decode(can_msg.data, self.bms_210h):
                            print("BMS_210h_Decode failed")
                    elif can_msg.can_id == 0x1AB020A:
                        if not BMS_20Ah_t_Decode(can_msg.data, self.bms_20Ah):
                            print("BMS_20Ah_Decode failed")
                    elif can_msg.can_id == 0x1AB0212:
                        if not BMS_212h_t_Decode(can_msg.data, self.bms_212h):
                            print("BMS_212h_Decode failed")
                    elif can_msg.can_id == 0x1AB0214:
                        if not BMS_214h_t_Decode(can_msg.data, self.bms_214h):
                            print("BMS_214h_Decode failed")
                    elif can_msg.can_id == 0x1AB0216:
                        if not BMS_216h_t_Decode(can_msg.data, self.bms_216h):
                            print("BMS_216h_Decode failed")
                    elif can_msg.can_id == 0x1AB0300:
                        if not THREE_OBC_300h_t_Decode(can_msg.data, self.obc_300h):
                            print("OBC_300h_Decode failed")
                    elif can_msg.can_id == 0x1AB0200:
                        if not BMS_200h_t_Decode(can_msg.data, self.bms_200h):
                            print("BMS_200h_Decode failed")
                    elif can_msg.can_id == 0x1AB0202:
                        if not BMS_202h_t_Decode(can_msg.data, self.bms_202h):
                            print("BMS_202h_Decode failed")
                    elif can_msg.can_id == 0x1AB0203:
                        if not BMS_20Ch_t_Decode(can_msg.data, self.bms_20Ch):
                            print("BMS_20Ch_Decode failed")
                    else:
                        pass

    def printChargerState(self, checked):

        def sendCommand():
            if checked:
                print("SwitchButton_Charger is ON")
                for _ in range(3):
                    self.can_device.send_data_ch1(0x1AB01101, bytes([1, 0, 0, 0, 0, 0, 0, 0]))
                    time.sleep(0.02)
            else:
                print("SwitchButton_Charger is OFF")
                for _ in range(3):
                    self.can_device.send_data_ch1(0x1AB01101, bytes([0, 0, 0, 0, 0, 0, 0, 0]))
                    time.sleep(0.02)

        self.timerUpdateTableWiget.stop()
        msg_box = MessageBox("确认执行", "是否确认发送这条命令?", self)
        msg_box.yesSignal.connect(lambda: sendCommand())
        msg_box.cancelSignal.connect(lambda: print(f"Action canceled."))
        msg_box.exec()
        self.timerUpdateTableWiget.start(150)

    def printVoltCurrValues(self):
        voltage = self.DoubleSpinBox_Volt.value()
        current = self.DoubleSpinBox_Curr.value()
        print(f"Voltage: {voltage}, Current: {current}")
        volt_uin32 = int(voltage * 100)
        curr_uint16 = int(current * 100)
        self.can_device.send_data_ch1(0x1AB01100,
                                      volt_uin32.to_bytes(4, 'big') + curr_uint16.to_bytes(2, 'big') + bytes([0, 0]))

    def closeEvent(self, event):
        self.can_device.close_device()  # Close CAN device before exiting
        event.accept()

    def update_BodyLabel_Charger(self):

        ACTotalPower_static = self.canController_info.ACTotalPower - 711 if self.canController_info.ACTotalPower > 711 else 0

        formatted_text = (
            f"<b>充电器直流输出:<br/>"
            f"</b>电压: {self.canController_info.DC1Volt:<10} <br/>"
            f"</b>电流: {self.canController_info.DC1Curr:<10} <br/>"
            f"</b>功率: {self.canController_info.DC1Power} W<br/>"
            f"<hr/>"
            f"<b>线电压1:<br/>"
            f"</b>电压: {self.canController_info.AC1Volt:<10} <br/>"
            f"</b>电流: {self.canController_info.AC1Curr:<10} <br/>"
            f"</b>功率: {self.canController_info.AC1Power} W<br/>"
            f"<hr/>"
            f"<b>线电压2:<br/>"
            f"</b>电压: {self.canController_info.AC2Volt:<10} <br/>"
            f"</b>电流: {self.canController_info.AC2Curr:<10} <br/>"
            f"</b>功率: {self.canController_info.AC2Power} W<br/>"
            f"<hr/>"
            f"<b>三相交流输入总功率:</b> {self.canController_info.ACTotalPower} W<br/>"
            f"<b>三相交流输入总功率减去静态功耗:</b> {ACTotalPower_static} W<br/>"
            f"<hr/>"
            f"<b>充电状态码:</b> {self.canController_info.ChargerState}<br/>"
            f"设置的输出电压: {self.canController_info.ChargerVolt:<10} V<br/>"
            f"设置的输出电流: {self.canController_info.ChargerCurr:<10} A<br/>"
            f"充电器温度: {self.canController_info.Temperature} ℃<br/>"
        )

        tableViewData = [
            ["充电器直流输出"],
            ["电压", f"{self.canController_info.DC1Volt:<10.2f}", "V"],
            ["电流", f"{self.canController_info.DC1Curr:<10.2f}", "A"],
            ["功率", f"{self.canController_info.DC1Power:<10.2f}", "W"],
            ["线电压1"],
            ["电压", f"{self.canController_info.AC1Volt:<10.2f}", "V"],
            ["电流", f"{self.canController_info.AC1Curr:<10.2f}", "A"],
            ["功率", f"{self.canController_info.AC1Power:<10.2f}", "W"],
            ["线电压2"],
            ["电压", f"{self.canController_info.AC2Volt:<10.2f}", "V"],
            ["电流", f"{self.canController_info.AC2Curr:<10.2f}", "A"],
            ["功率", f"{self.canController_info.AC2Power:<10.2f}", "W"],
            ["三相交流输入总功率"],
            ["功率", f"{self.canController_info.ACTotalPower:<10.2f}", "W"],
            ["三相交流输入总功率减去静态功耗"],
            ["功率", f"{ACTotalPower_static:<10.2f}", "W"],
            ["充电状态码", f"{self.canController_info.ChargerState}"],
            ["设置的输出电压", f"{self.canController_info.ChargerVolt:<10.2f}", "V"],
            ["设置的输出电流", f"{self.canController_info.ChargerCurr:<10.2f}", "A"],
            ["充电器温度", f"{self.canController_info.Temperature}", "℃"],
            ["最大充电电流", f"{self.canController_info.MaxChargerCurr:<10.2f}", "A"],
            ["最大充电电压", f"{self.canController_info.MaxChargerVolt:<10.2f}", "V"],
            ["最大充电功率", f"{self.canController_info.MaxChargePower:<10.2f}", "W"]
        ]

        self.TableWidget_Charger.setRowCount(len(tableViewData))

        for i, row in enumerate(tableViewData):
            for j in range(len(row)):
                item = QTableWidgetItem(row[j])
                if len(row) == 1:
                    # 设置合并单元格
                    self.TableWidget_Charger.setSpan(i, 0, 1, 3)
                    # item.setTextAlignment(Qt.AlignCenter)
                    item.setFont(QFont("Arial", 10, QFont.Bold))
                else:
                    item.setFont(QFont("Arial", 10, QFont.Normal))

                self.TableWidget_Charger.setItem(i, j, item)

        self.TableWidget_Charger.verticalHeader().hide()
        self.TableWidget_Charger.setHorizontalHeaderLabels(['属性', '值', '单位'])
        # 设置自适应父容器宽度
        self.TableWidget_Charger.resizeColumnsToContents()
        self.TableWidget_Charger.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        # self.BodyLabel_Charger.setText(formatted_text)
        # self.BodyLabel_Charger.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        # self.BodyLabel_Charger.setFont(QFont("Arial", 12))

    def update_BodyLabel_Battery(self):
        formatted_text = (
            f"<b>最小单体电压:</b> {self.bms_210h.BMS_Sys_MinCellV:10.3f} V<br/>"
            f"<b>最大单体电压:</b> {self.bms_210h.BMS_Sys_MaxCellV:10.2f} V<br/>"
            f"<b>最小单体电压编号:</b> {self.bms_210h.BMS_Sys_MinCellV_No}<br/>"
            f"<b>最大单体电压编号:</b> {self.bms_210h.BMS_Sys_MaxCellV_No}<br/>"
            f"<b>功率限制请求:</b> {self.bms_210h.BMS_PowerLimitRequest}<br/>"
            f"<b>CRC8:</b> {self.bms_210h.BMS_210h_CRC8}"
        )

        formatted_text += "<hr/>"

        formatted_text += (
            f"<b>BMS允许的峰值充电功率(10s):</b> {self.bms_20Ah.BMS_AllowedPeakChrgPower:10.2f} kW<br/>"
            f"<b>BMS允许的峰值放电功率(10s):</b> {self.bms_20Ah.BMS_AllowedPeakDischrgPower:10.2f} kW<br/>"
            f"<b>BMS允许的持续充电功率:</b> {self.bms_20Ah.BMS_AllowedContinusChrgPower:10.2f} kW<br/>"
            f"<b>BMS允许的持续放电功率:</b> {self.bms_20Ah.BMS_AllowedContinusDischrgPower:10.2f} kW<br/>"
            f"<b>滚动计数:</b> {self.bms_20Ah.BMS_20Ah_rollingCounter}<br/>"
            f"<b>校验和:</b> {self.bms_20Ah.BMS_20Ah_CheckSum}"
        )

        formatted_text += "<hr/>"

        formatted_text += (
            f"<b>最小单体温度:</b> {self.bms_212h.BMS_Sys_MinCellT:10.2f} ℃<br/>"
            f"<b>最大单体温度:</b> {self.bms_212h.BMS_Sys_MaxCellT:10.2f} ℃<br/>"
            f"<b>最小单体温度编号:</b> {self.bms_212h.BMS_Sys_MinCellT_No}<br/>"
            f"<b>最大单体温度编号:</b> {self.bms_212h.BMS_Sys_MaxCellT_No}<br/>"
            f"<b>快充电枪表面温度:</b> {self.bms_212h.BMS_FastChrgTemp} ℃"
        )

        formatted_text += "<hr/>"

        formatted_text += (
            f"<b>电池总电压:</b> {self.bms_200h.BMS_Sys_TotalVoltage:10.2f} V<br/>"
            f"<b>电池总电流:</b> {self.bms_200h.BMS_Sys_SumCurrent:10.2f} A<br/>"
            f"<b>电池包外部总压:</b> {self.bms_200h.BMS_battery_outside_Voltage:10.2f} V<br/>"
            f"<b>电池精确SOC（仅供VCU计算使用）:</b> {self.bms_200h.BMS_Sys_SOC2:10.2f} %<br/>"
        )

        formatted_text += "<hr/>"

        formatted_text += (
            f"<b>正绝缘电阻:</b> {self.bms_216h.BMS_PosInsulationResistance} kΩ<br/>"
            f"<b>负绝缘电阻:</b> {self.bms_216h.BMS_NegInsulationResistance} kΩ<br/>"
            f"<b>系统SOC:</b> {self.bms_216h.BMS_Sys_SOC} %<br/>"
            f"<b>系统SOH:</b> {self.bms_216h.BMS_Sys_SOH} %<br/>"
            f"<b>系统SOE:</b> {self.bms_216h.BMS_Sys_SOE:10.3f} kw.h"
        )

        formatted_text += "<hr/>"

        formatted_text += (
            f"<b>充电请求总电压:</b> {self.bms_214h.BMS_Chg_RequestSumV:10.3f} V<br/>"
            f"<b>充电请求总电流:</b> {self.bms_214h.BMS_Chg_RequestCur:10.3f} A<br/>"
            f"<b>剩余充电时间:</b> {self.bms_214h.BMS_ChargingTimeRemain_h} 小时<br/>"
            f"<b>DC充电器最大允许功率:</b> {self.bms_214h.BMS_DCChargerMaxAllowablePower:10.3f} kW<br/>"
            f"<b>剩余充电时间:</b> {self.bms_214h.BMS_ChargingTimeRemain_min} 分钟<br/>"
            f"<b>本次充电电量:</b> {self.bms_214h.BMS_ChargingTotalPower} kw.h<br/>"
            f"<b>OBC/IVU使能:</b> {self.bms_214h.BMS_OBC_IVU_Enable}"
        )

        formatted_text += "<hr/>"

        formatted_text += (
            f"<b>OBC输出电压:</b> {self.obc_300h.OBC_ChargerOutputVoltage:10.3f} V<br/>"
            f"<b>OBC输出电流:</b> {self.obc_300h.OBC_ChargerOutputCurrent:10.3f} A<br/>"
            f"<b>OBC最大允许输出功率:</b> {self.obc_300h.OBC_ChargerMaxAllowableOutputPower:10.3f} kW"
        )

        formatted_text += "<hr/>"

        bms_202h_str = self.bms_202h.toStrObj()
        bms_20Ch_str = self.bms_20Ch.toStrObj()

        formatted_text += (
            f"<b>主接触器（放电主接）故障信息:</b> {bms_202h_str.BMS_Err_DischrgAnodeRelay}<br/>"
            f"<b>主接触器状态（放电主接）:</b> {bms_202h_str.BMS_DischargeAnodeRelay_status}<br/>"
            f"<b>开机检测:</b> {bms_202h_str.BMS_Boot_Detection}<br/>"
            f"<b>A+信号:</b> {bms_202h_str.BMS_A}<br/>"
            f"<b>电池包保温状态:</b> {bms_202h_str.BMS_BatteryTempKeepStatus}<br/>"
            f"<b>电池包在途温控功能可用性:</b> {bms_202h_str.BMS_BatteryTempPrecontrolAvailable}<br/>"
            f"<b>电池包在途温控功能状态:</b> {bms_202h_str.BMS_BatteryTempPrecontrolSts}<br/>"
            f"<b>电子锁请求:</b> {bms_202h_str.BMS_ElectronicLockRequest}<br/>"
            f"<b>继电器状态-加热（预留）:</b> {bms_202h_str.BMS_Relay_HEAT}<br/>"
            f"<b>预充接触器故障信息:</b> {bms_202h_str.BMS_Err_PrechargeAnodeRelay}<br/>"
            f"<b>预充接触器状态:</b> {bms_202h_str.BMS_Precharge_anode_Relay_status}<br/>"
            f"<b>负极接触器故障信息:</b> {bms_202h_str.BMS_Err_DischrgCathodeRelay}<br/>"
            f"<b>负极接触器状态:</b> {bms_202h_str.BMS_DischrgCathodeRelay_status}<br/>"
            f"<b>快充接触器故障信息:</b> {bms_202h_str.BMS_Err_ChargeRelay}<br/>"
            f"<b>快充接触器状态:</b> {bms_202h_str.BMS_ChargeRelay_status}<br/>"
            f"<b>充电、加热及冷却使能:</b> {bms_202h_str.BMS_ChrgHeatColEnable}<br/>"
            f"<b>电池包充放电状态:</b> {bms_202h_str.BMS_Sys_ChgorDisChrgSts}<br/>"
            f"<b>BMS快充充电状态:</b> {bms_202h_str.BMS_FastChrgSts}<br/>"
            f"<b>BMS慢充充电状态:</b> {bms_202h_str.BMS_SlowChrgSts}<br/>"
            f"<b>快充连接状态:</b> {bms_202h_str.BMS_ChrgCouplesSt}<br/>"
            f"<b>请求吸和充电继电器（预留）:</b> {bms_202h_str.BMS_req_ConnectChargeRelay}<br/>"
            f"<b>无线充电状态:</b> {bms_202h_str.BMS_WirelessChrgSts}<br/>"
            f"<b>CC2:</b> {bms_202h_str.BMS_CC2}<br/>"
            f"<b>最大允许充电电量:</b> {bms_202h_str.BMS_AllowedChrgMaxPower} %"
        )

        tableViewData = [
            ["BMS_210h BMS单体电压"],
            ["最小单体电压", f"{self.bms_210h.BMS_Sys_MinCellV:<10.2f}", "V"],
            ["最大单体电压", f"{self.bms_210h.BMS_Sys_MaxCellV:<10.2f}", "V"],
            ["最小单体电压编号", f"{self.bms_210h.BMS_Sys_MinCellV_No}"],
            ["最大单体电压编号", f"{self.bms_210h.BMS_Sys_MaxCellV_No}"],
            ["功率限制请求", f"{self.bms_210h.BMS_PowerLimitRequest}"],
            ["CRC8", f"{self.bms_210h.BMS_210h_CRC8}"],
            ["BMS_20Ah BMS充放电功率持续及峰值"],
            ["BMS允许的峰值充电功率(10s)", f"{self.bms_20Ah.BMS_AllowedPeakChrgPower:<10.2f}", "kW"],
            ["BMS允许的峰值放电功率(10s)", f"{self.bms_20Ah.BMS_AllowedPeakDischrgPower:<10.2f}", "kW"],
            ["BMS允许的持续充电功率", f"{self.bms_20Ah.BMS_AllowedContinusChrgPower:<10.2f}", "kW"],
            ["BMS允许的持续放电功率", f"{self.bms_20Ah.BMS_AllowedContinusDischrgPower:<10.2f}", "kW"],
            ["滚动计数", f"{self.bms_20Ah.BMS_20Ah_rollingCounter}"],
            ["校验和", f"{self.bms_20Ah.BMS_20Ah_CheckSum}"],
            ["BMS_200h"],
            ["电池总电压", f"{self.bms_200h.BMS_Sys_TotalVoltage:<10.2f}", "V"],
            ["电池总电流", f"{self.bms_200h.BMS_Sys_SumCurrent:<10.2f}", "A"],
            ["电池包外部总压", f"{self.bms_200h.BMS_battery_outside_Voltage:<10.2f}", "V"],
            ["电池精确SOC（仅供VCU计算使用）", f"{self.bms_200h.BMS_Sys_SOC2:<10.2f}", "%"],
            ["BMS_212h BMS温度相关"],
            ["最小单体温度", f"{self.bms_212h.BMS_Sys_MinCellT}", "℃"],
            ["最大单体温度", f"{self.bms_212h.BMS_Sys_MaxCellT}", "℃"],
            ["最小单体温度编号", f"{self.bms_212h.BMS_Sys_MinCellT_No}"],
            ["最大单体温度编号", f"{self.bms_212h.BMS_Sys_MaxCellT_No}"],
            ["快充电枪表面温度", f"{self.bms_212h.BMS_FastChrgTemp}", "℃"],
            ["BMS_216h BMS绝缘电阻及SOC/H"],
            ["正绝缘电阻", f"{self.bms_216h.BMS_PosInsulationResistance:<10.2f}", "kΩ"],
            ["负绝缘电阻", f"{self.bms_216h.BMS_NegInsulationResistance:<10.2f}", "kΩ"],
            ["系统SOC", f"{self.bms_216h.BMS_Sys_SOC:<10.2f}", "%"],
            ["系统SOH", f"{self.bms_216h.BMS_Sys_SOH:<10.2f}", "%"],
            ["系统SOE", f"{self.bms_216h.BMS_Sys_SOE:<10.2f}", "kw.h"],
            ["BMS_214h BMS充电请求相关"],
            ["充电请求总电压", f"{self.bms_214h.BMS_Chg_RequestSumV:<10.2f}", "V"],
            ["充电请求总电流", f"{self.bms_214h.BMS_Chg_RequestCur:<10.2f}", "A"],
            ["剩余充电时间", f"{self.bms_214h.BMS_ChargingTimeRemain_h:<10.2f}", "小时"],
            ["DC充电器最大允许功率", f"{self.bms_214h.BMS_DCChargerMaxAllowablePower:<10.2f}", "kW"],
            ["剩余充电时间", f"{self.bms_214h.BMS_ChargingTimeRemain_min:<10.2f}", "分钟"],
            ["本次充电电量", f"{self.bms_214h.BMS_ChargingTotalPower:<10.2f}", "kw.h"],
            ["OBC/IVU使能", f"{self.bms_214h.BMS_OBC_IVU_Enable}"],
            ["OBC_300h 充电有关的信号1"],
            ["OBC输出电压", f"{self.obc_300h.OBC_ChargerOutputVoltage:<10.2f}", "V"],
            ["OBC输出电流", f"{self.obc_300h.OBC_ChargerOutputCurrent:<10.2f}", "A"],
            ["OBC最大允许输出功率", f"{self.obc_300h.OBC_ChargerMaxAllowableOutputPower:<10.2f}", "kW"],
            ["BMS_202h BMS控制及状态相关"],
            ["主接触器（放电主接）故障信息", f"{bms_202h_str.BMS_Err_DischrgAnodeRelay}"],
            ["主接触器状态（放电主接）", f"{bms_202h_str.BMS_DischargeAnodeRelay_status}"],
            ["开机检测", f"{bms_202h_str.BMS_Boot_Detection}"],
            ["A+信号", f"{bms_202h_str.BMS_A}"],
            ["电池包保温状态", f"{bms_202h_str.BMS_BatteryTempKeepStatus}"],
            ["电池包在途温控功能可用性", f"{bms_202h_str.BMS_BatteryTempPrecontrolAvailable}"],
            ["电池包在途温控功能状态", f"{bms_202h_str.BMS_BatteryTempPrecontrolSts}"],
            ["电子锁请求", f"{bms_202h_str.BMS_ElectronicLockRequest}"],
            ["继电器状态-加热（预留）", f"{bms_202h_str.BMS_Relay_HEAT}"],
            ["预充接触器故障信息", f"{bms_202h_str.BMS_Err_PrechargeAnodeRelay}"],
            ["预充接触器状态", f"{bms_202h_str.BMS_Precharge_anode_Relay_status}"],
            ["负极接触器故障信息", f"{bms_202h_str.BMS_Err_DischrgCathodeRelay}"],
            ["负极接触器状态", f"{bms_202h_str.BMS_DischrgCathodeRelay_status}"],
            ["快充接触器故障信息", f"{bms_202h_str.BMS_Err_ChargeRelay}"],
            ["快充接触器状态", f"{bms_202h_str.BMS_ChargeRelay_status}"],
            ["充电、加热及冷却使能", f"{bms_202h_str.BMS_ChrgHeatColEnable}"],
            ["电池包充放电状态", f"{bms_202h_str.BMS_Sys_ChgorDisChrgSts}"],
            ["BMS快充充电状态", f"{bms_202h_str.BMS_FastChrgSts}"],
            ["BMS慢充充电状态", f"{bms_202h_str.BMS_SlowChrgSts}"],
            ["快充连接状态", f"{bms_202h_str.BMS_ChrgCouplesSt}"],
            ["请求吸和充电继电器（预留）", f"{bms_202h_str.BMS_req_ConnectChargeRelay}"],
            ["无线充电状态", f"{bms_202h_str.BMS_WirelessChrgSts}"],
            ["CC2", f"{bms_202h_str.BMS_CC2}"],
            ["最大允许充电电量", f"{bms_202h_str.BMS_AllowedChrgMaxPower}", "%"],
            ["BMS_20Ch BMS故障相关"],
            ["电池系统故障", f"{bms_20Ch_str.BMS_Powertrain_System_fault}"],
            ["电池单体电压低故障", f"{bms_20Ch_str.BMS_cell_Voltage_low}"],
            ["电池单体电压高故障", f"{bms_20Ch_str.BMS_cell_Voltage_High}"],
            ["电池组温度低故障", f"{bms_20Ch_str.BMS_Battery_LowTemp_warning}"],
            ["电池组温度高故障", f"{bms_20Ch_str.BMS_Battery_HighTemp_warning}"],
            ["循环计数器", f"{bms_20Ch_str.BMS_20ch_RollingCounter}"],
            ["SOC高报警", f"{bms_20Ch_str.BMS_SOCHigh_Warning}"],
            ["SOC低报警", f"{bms_20Ch_str.BMS_SOCLow_Warning}"],
            ["电池包总电压高故障", f"{bms_20Ch_str.BMS_Battery_SumVoltage_High}"],
            ["电池包总电压低故障", f"{bms_20Ch_str.BMS_Battery_SumVoltage_Low}"],
            ["电池单体一致性差故障", f"{bms_20Ch_str.BMS_HVBatCellDiffFalt}"],
            ["电池包过充故障", f"{bms_20Ch_str.BMS_Err_OverChrging}"],
            ["电池包充电提醒", f"{bms_20Ch_str.BMS_Charger_Reminding}"],
            ["SOC跳变报警", f"{bms_20Ch_str.BMS_SOCJump_Warning}"],
            ["热失效故障", f"{bms_20Ch_str.BMS_ThermalInvalidFault}"],
            ["电池不匹配报警", f"{bms_20Ch_str.BMS_BatNotMatchFlt}"],
            ["绝缘低故障", f"{bms_20Ch_str.BMS_Err_ISO_LOW}"],
            ["充电电流过大故障", f"{bms_20Ch_str.BMS_Err_ChgCurrent_High}"],
            ["放电电流过大故障", f"{bms_20Ch_str.BMS_Err_DchCurrent_High}"],
            ["温差过大故障", f"{bms_20Ch_str.BMS_Err_DtT_High}"],
            ["热管理系统故障", f"{bms_20Ch_str.ThermalManage_System_fault}"],
            ["BMS通讯故障", f"{bms_20Ch_str.BMS_Err_comunicacion}"],
            ["BMS高压互锁故障", f"{bms_20Ch_str.BMS_Err_InterLock}"],
            ["短路保护", f"{bms_20Ch_str.BMS_Circuit_Protection}"],
            ["蓄电池馈电故障", f"{bms_20Ch_str.BMS_FeedFault}"],
            ["Byte0-Byte6的CRC8循环冗余检验值", f"{bms_20Ch_str.BMS_20ch_CRC8}"]
        ]

        self.TableWidget_Battery.setRowCount(len(tableViewData))

        for i, row in enumerate(tableViewData):
            for j in range(len(row)):
                item = QTableWidgetItem(row[j])
                if len(row) == 1:
                    # 设置合并单元格
                    self.TableWidget_Battery.setSpan(i, 0, 1, 3)
                    # item.setTextAlignment(Qt.AlignCenter)
                    item.setFont(QFont("Arial", 10, QFont.Bold))
                else:
                    item.setFont(QFont("Arial", 10, QFont.Normal))

                self.TableWidget_Battery.setItem(i, j, item)

        self.TableWidget_Battery.verticalHeader().hide()
        self.TableWidget_Battery.setHorizontalHeaderLabels(['属性', '值', '单位'])
        # 设置自适应父容器宽度
        self.TableWidget_Battery.resizeColumnsToContents()
        self.TableWidget_Battery.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        # self.TableWidget_Battery.resizeColumnToContents(0)
        # self.BodyLabel_Battery.setText(formatted_text)
        # self.BodyLabel_Battery.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        # self.BodyLabel_Battery.setFont(QFont("Arial", 12))

    def confirmAction(self, stage_name):
        def sendCommand():
            print(f"Action for {stage_name} confirmed.")

            if stage_name == "Stage 1":
                # 上高压闭合指令流：
                # 0x1aa016F3 8 00 0a 00 01 00 00 00 00 （闭合预充，保持主正断开）
                for _ in range(5):
                    self.can_device.send_data_ch2(0x1aa016F3, bytes([0x00, 0x0A, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00]))
                    time.sleep(0.02)
            elif stage_name == "Stage 2":
                for _ in range(5):
                    self.can_device.send_data_ch2(0x1aa016F3, bytes([0x00, 0x0A, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00]))
                    time.sleep(0.02)
            elif stage_name == "Stage 3":
                for _ in range(5):
                    self.can_device.send_data_ch2(0x1aa016F3, bytes([0x00, 0x0A, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00]))
                    time.sleep(0.02)
            elif stage_name == "Stage 4":
                for _ in range(5):
                    self.can_device.send_data_ch2(0x1aa016F3, bytes([0x00, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))
                    time.sleep(0.02)

        self.timerUpdateTableWiget.stop()

        msg_box = MessageBox("确认执行", "是否确认发送这条命令?", self)
        msg_box.yesSignal.connect(lambda: sendCommand())
        msg_box.cancelSignal.connect(lambda: print(f"Action for {stage_name} canceled."))
        msg_box.exec()
        self.timerUpdateTableWiget.start(150)


class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))


class SettingWidget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        # self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)
        self.switchButton = SwitchButton(self)
        self.switchButton.setOnText('Dark')
        self.switchButton.setOffText('Light')

        self.switchButton.checkedChanged.connect(
            lambda: setTheme(Theme.DARK if self.switchButton.isChecked() else Theme.LIGHT))

        setFont(self.switchButton, 24)
        # self.switchButton.setAlignment(Qt.AlignCenter)
        self.hBoxLayout.addWidget(self.switchButton, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))


class ProfileCard(QWidget):
    """ Profile card """

    def __init__(self, avatarPath: str, name: str, email: str, parent=None):
        super().__init__(parent=parent)
        self.avatar = AvatarWidget(avatarPath, self)
        self.nameLabel = BodyLabel(name, self)
        self.emailLabel = CaptionLabel(email, self)
        self.logoutButton = HyperlinkButton(
            'https://github.com/MisakaMikoto128', '注销', self)

        color = QColor(206, 206, 206) if isDarkTheme() else QColor(96, 96, 96)
        self.emailLabel.setStyleSheet('QLabel{color: ' + color.name() + '}')

        color = QColor(255, 255, 255) if isDarkTheme() else QColor(0, 0, 0)
        self.nameLabel.setStyleSheet('QLabel{color: ' + color.name() + '}')
        setFont(self.logoutButton, 13)

        self.setFixedSize(307, 82)
        self.avatar.setRadius(24)
        self.avatar.move(2, 6)
        self.nameLabel.move(64, 13)
        self.emailLabel.move(64, 32)
        self.logoutButton.move(52, 48)


class Window(FluentWindow):

    def __init__(self):
        super().__init__()

        # create sub interface
        self.homeInterface = MainWindow(self)
        # self.musicInterface = Widget('Music Interface', self)
        # self.videoInterface = Widget('Video Interface', self)
        # self.folderInterface = Widget('Folder Interface', self)
        self.settingInterface = SettingWidget('Setting Interface', self)
        # self.albumInterface = Widget('Album Interface', self)
        # self.albumInterface1 = Widget('Album Interface 1', self)
        # self.albumInterface2 = Widget('Album Interface 2', self)
        # self.albumInterface1_1 = Widget('Album Interface 1-1', self)
        # 最大化
        self.setWindowState(Qt.WindowMaximized)
        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, 'Home')
        # self.addSubInterface(self.musicInterface, FIF.MUSIC, 'Music library')
        # self.addSubInterface(self.videoInterface, FIF.VIDEO, 'Video library')

        # Theme切换按钮

        self.navigationInterface.addSeparator()

        # self.addSubInterface(self.albumInterface, FIF.ALBUM, 'Albums', NavigationItemPosition.SCROLL)
        # self.addSubInterface(self.albumInterface1, FIF.ALBUM, 'Album 1', parent=self.albumInterface)
        # self.addSubInterface(self.albumInterface1_1, FIF.ALBUM, 'Album 1.1', parent=self.albumInterface1)
        # self.addSubInterface(self.albumInterface2, FIF.ALBUM, 'Album 2', parent=self.albumInterface)
        # self.addSubInterface(self.folderInterface, FIF.FOLDER, 'Folder library', NavigationItemPosition.SCROLL)

        # add custom widget to bottom
        self.navigationInterface.addWidget(
            routeKey='avatar',
            widget=NavigationAvatarWidget('Yuanlin-Liu', 'resource/shoko.png'),
            onClick=self.showMessageBox,
            position=NavigationItemPosition.BOTTOM,
        )

        self.addSubInterface(self.settingInterface, FIF.SETTING, 'Settings', NavigationItemPosition.BOTTOM)

        # add badge to navigation item
        # item = self.navigationInterface.widget(self.videoInterface.objectName())
        # InfoBadge.attension(
        #     text=9,
        #     parent=item.parent(),
        #     target=item,
        #     position=InfoBadgePosition.NAVIGATION_ITEM
        # )

        # NOTE: enable acrylic effect
        self.navigationInterface.setAcrylicEnabled(True)

    def initWindow(self):
        self.resize(900, 700)
        # self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        # self.setWindowTitle('PyQt-Fluent-Widgets')

        self.setWindowTitle('充电控制器上位机')
        self.setWindowIcon(QIcon('./img/star.png'))

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        # set the minimum window width that allows the navigation panel to be expanded
        # self.navigationInterface.setMinimumExpandWidth(900)
        # self.navigationInterface.expand(useAni=False)

    def showMessageBox(self):

        self.homeInterface.timerUpdateTableWiget.stop()

        w = MessageBox(
            '支持作者',
            '🥤🥤🚀',
            self
        )
        w.yesButton.setText('🥤')
        w.cancelButton.setText('🚀')
        w.exec()
        self.homeInterface.timerUpdateTableWiget.start(150)

    def contextMenuEvent(self, e) -> None:
        menu = AcrylicMenu(parent=self)

        # add custom widget
        card = ProfileCard('resource/shoko.png', '刘沅林', 'liuyuanlins@outlook.com', menu)
        menu.addWidget(card, selectable=False)
        # menu.addWidget(card, selectable=True, onClick=lambda: print('666'))

        menu.addSeparator()
        menu.addActions([
            Action(FluentIcon.PEOPLE, '管理账户和设置'),
            Action(FluentIcon.SHOPPING_CART, '支付方式'),
            Action(FluentIcon.CODE, '兑换代码和礼品卡'),
        ])
        menu.addSeparator()
        menu.addAction(Action(FluentIcon.SETTING, '设置'))
        menu.exec(e.globalPos())


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # setTheme(Theme.DARK)

    app = QApplication(sys.argv)
    w = Window()
    w.show()
    app.exec_()
