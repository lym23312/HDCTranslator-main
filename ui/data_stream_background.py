#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据流背景组件
实现复古科幻终端风格的数据流动画效果
"""

import random
import string
import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QRect, QPointF
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QLinearGradient, QPainterPath

class DataStreamBackground(QWidget):
    """模拟科研数据流动画的背景控件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setMinimumHeight(60)
        
        self.data_streams = []
        self.max_streams = 10
        self.generate_data_streams()
        
        self.matrix_columns = []
        self.init_matrix()
        
        self.sci_terms = [
            # 基础系统术语
            "SCANNING...", "ANALYZING DATA", "PROCESSING", "UDS TRANSLATION PROTOCOL",
            "NEURAL MAPPING", "CROSS-REFERENCE", "CALIBRATING SYSTEM", "LANGUAGE MODULE",
            "COALITION DATABASE", "SECURE CONNECTION", "XENOLANGUAGE INTERFACE",
            "MEMORY ALLOCATION", "BUFFER OVERFLOW CHECK", "OPTIMIZING PARAMETERS",
            "QUANTUM ENCRYPTION", "DEEP SCAN ACTIVE", "BIOMETRIC VERIFICATION",
            "UDS PROTOCOL ACTIVE", "ALLIANCE PROJECT UDS v8.1.24",
            "QUANTUM TUNNELING ESTABLISHED", "NEURAL LINK SYNCHRONIZED",
            "DATA PACKET INTEGRITY: 99.7%", "SCANNING SUBNET MASKS",
            "ALLIANCE PROTOCOLS ENGAGED", "LOADING KERNEL MODULES",
            
            # 墨水相关消息
            "墨水分析报告: 末日蠕虫神经毒素研究", 
            "墨水: 锤头煞母皇标本处理中", 
            "警告: 画皮感染扩散速率上升",
            "日志: 虎尾煞行为模式异常", 
            "墨水: 摩螺克组织样本降解速度加快",
            "墨水实验#347: 噬渊鱿活体解剖",
            "医疗分析: 锤头煞毒素提取完成",
            "生物分析: 画皮RNA序列解码中",
            
            # 伍德相关消息
            "工程日志: 捕钩兽防御系统升级", 
            "伍德: 设备校准率97.3%",
            "安全协议: 画皮隔离舱压力异常", 
            "警告: 女妖声波干扰屏蔽失效", 
            "维修请求: 末日蠕虫损坏的防护墙",
            "技术部: 深海探测器压力校准",
            "武器系统: 伏尔甘粒子炮充能",
            "屏蔽技术: 锤头煞声纳干扰启动",
            
            # HDC相关消息
            "HDC授权访问: 深渊异兽研究档案",
            "联盟命令: 虎尾煞样本销毁程序启动",
            "HDC备忘录: 摩螺克活体实验暂停",
            "警告: 木星分离主义者活动增加300%",
            "HDC论文报告: 画皮特性与军事应用研究",
            "HDC安全协议: 量子加密层级提升",
            "HDC网络扫描: 检测到未知入侵尝试",
            "HDC翻译矩阵: 异星语言解析进度18%",
            
            # 联盟设施消息
            "联盟D-7研究站损失统计中",
            "联盟深渊站16号隔离协议已激活", 
            "联盟贝尔阵线前哨站通讯中断",
            "木卫二研究基地受末日蠕虫攻击", 
            "联盟水银湾潜艇坞画皮感染程度: 严重",
            "联盟泰坦前哨哨兵系统故障", 
            "木卫二联盟基地紧急撤离中",
            "联盟深海探索队失联，地点:分形守卫者区域",
            "联盟北极站氧气泄漏，锤头煞入侵风险升高",
            "联盟远征队报告: 深度12000米发现未知结构",
            "联盟议会会议记录: 战略投票通过",
            
            # 敌人信息
            "锤头煞在卡卢加海沟大量繁殖", 
            "画皮感染扩散至第七区生活舱", 
            "末日蠕虫摧毁海底光缆，损失惨重",
            "虎尾煞攻击造成三号发电站瘫痪", 
            "噬海女妖-卡律布迪斯破坏声呐阵列",
            "捕钩兽突破C区围栏，人员伤亡报告中", 
            "摩螺克已适应新型抑制剂",
            "深海巨蟹群体行为异常，移动方向:联盟基地",
            "女妖出现于卡尔代拉海沟",
            "深渊脉冲信号强度增加450%",
            
            # 木星分离主义者消息
            "木星分离主义者泰坦基地发生画皮感染", 
            "分离主义者领袖试图控制末日蠕虫失败",
            "敌对势力木卫二前哨站遭虎尾煞入侵", 
            "分离主义者的锤头煞试验导致基地损毁",
            "画皮攻击木星分离主义者的补给船队",
            "分离主义者加密通讯截获，内容解析中",
            "分离主义者潜艇在禁区海域被发现",
            
            # 御冬潜艇事故相关
            "【紧急通报】御冬号深海潜艇在分形峡谷区域遭遇不明生物袭击",
            "御冬号系统故障导致沉没，联盟已派出救援队",
            "木卫二救援小组已抵达御冬号最后已知位置",
            "与墨水小组失去联系，联盟派出额外救援力量",
            "御冬号黑匣子信号检测到，救援工作继续",
            "幸存者搜救行动因深海压力问题暂停",
            "御冬号残骸附近发现不明生物活动迹象",
            
            # 联盟进展
            "联盟成功研发画皮感染解药", 
            "联盟科学家破解末日蠕虫神经系统",
            "联盟特工成功渗透木星分离主义者网络", 
            "新型锤头煞抑制剂测试成功",
            "联盟议会批准对分离主义者据点的军事行动", 
            "捕钩兽行为控制实验取得突破",
            "联盟成功从噬海女妖组织中提取医用化合物",
            "防御矩阵升级完成",
            "联盟通讯网络覆盖深度增加5000米",
            
            # 数据流标记
            "DATA STREAM ALPHA", "DATA STREAM BETA", "DATA STREAM GAMMA",
            "XENOCODE TRANSLATION IN PROGRESS", "ALLIANCE SECURITY LAYER",
            "NEURAL INTERFACE ONLINE", "PATTERN RECOGNITION MODULE",
            "DEEP SEA SONAR ARRAY ACTIVE", "ENCRYPTING TRANSMISSION",
            "COALITION SECURE PROTOCOL", "MEMORY CORE DEFRAGMENTATION"
        ]
        
        self.active_terms = []
        self.max_active_terms = 4
        
        self.typing_speeds = []
        self.current_positions = []
        self.term_positions = []
        self.term_opacities = []
        self.term_directions = []
        
        self.blink_state = True
        self.cursor_timer = QTimer(self)
        self.cursor_timer.timeout.connect(self.toggle_cursor)
        self.cursor_timer.start(500)
        
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_data)
        self.update_timer.start(50)
        
        self.term_timer = QTimer(self)
        self.term_timer.timeout.connect(self.update_sci_term)
        self.term_timer.start(2000)
        
        self.update_sci_term()
    
    def generate_data_streams(self):
        """生成随机数据流"""
        self.data_streams = []
        for _ in range(self.max_streams):
            stream = {
                'x': random.randint(0, self.width() or 400),
                'y': random.randint(0, self.height() or 100),
                'length': random.randint(20, 120),
                'speed': random.uniform(0.5, 3),
                'data': self.generate_random_data(random.randint(10, 20)),
                'color': QColor(0, random.randint(200, 255), 0, random.randint(100, 200))
            }
            self.data_streams.append(stream)
    
    def init_matrix(self):
        """初始化矩阵效果"""
        cols = (self.width() or 400) // 15
        self.matrix_columns = []
        
        for i in range(cols):
            col = {
                'x': i * 15,
                'chars': self.generate_random_data(random.randint(3, 10)),
                'pos': random.randint(0, self.height() or 100),
                'speed': random.uniform(0.5, 3)
            }
            self.matrix_columns.append(col)
    
    def generate_random_data(self, length):
        """生成随机数据字符串"""
        data_type = random.choice(['hex', 'binary', 'hex'])
        
        if data_type == 'hex':
            return ''.join(random.choice(string.hexdigits) for _ in range(length))
        else:
            return ''.join(random.choice('01') for _ in range(length))
    
    def update_data(self):
        """更新数据流动画"""
        for stream in self.data_streams:
            stream['y'] += stream['speed']
            if stream['y'] > self.height() + stream['length']:
                stream['y'] = -stream['length']
                stream['x'] = random.randint(0, self.width())
                stream['data'] = self.generate_random_data(random.randint(10, 20))
        
        for col in self.matrix_columns:
            col['pos'] += col['speed']
            if col['pos'] > self.height() + len(col['chars']) * 15:
                col['pos'] = -len(col['chars']) * 15
                col['chars'] = self.generate_random_data(random.randint(3, 10))
        
        terms_to_remove = []
        for i, term in enumerate(self.active_terms):
            if self.current_positions[i] < len(term):
                self.current_positions[i] += 0.2 * self.typing_speeds[i]
            
            self.term_opacities[i] += 0.03 * self.term_directions[i]
            self.term_opacities[i] = max(0, min(1, self.term_opacities[i]))
            
            if self.term_opacities[i] <= 0 and self.term_directions[i] < 0:
                terms_to_remove.append(i)
        
        for i in sorted(terms_to_remove, reverse=True):
            del self.active_terms[i]
            del self.typing_speeds[i]
            del self.current_positions[i]
            del self.term_positions[i]
            del self.term_opacities[i]
            del self.term_directions[i]
        
        self.update()
    
    def update_sci_term(self):
        """添加新的科研术语到显示列表"""
        if len(self.active_terms) < self.max_active_terms:
            self._add_new_term()
        else:
            fade_index = random.randint(0, len(self.active_terms)-1)
            self.term_directions[fade_index] = -1
            QTimer.singleShot(1000, self._add_new_term)
    
    def toggle_cursor(self):
        """切换光标显示状态"""
        self.blink_state = not self.blink_state
        self.update()
    
    def _add_new_term(self):
        """添加新的科研术语到显示列表"""
        used_terms = set(self.active_terms)
        available_terms = [term for term in self.sci_terms if term not in used_terms]
        if not available_terms:
            available_terms = self.sci_terms
        
        new_term = random.choice(available_terms)
        self.active_terms.append(new_term)
        
        self.typing_speeds.append(random.uniform(1.0, 2.0))
        self.current_positions.append(0)
        
        margin = 50
        max_attempts = 10
        
        for _ in range(max_attempts):
            x = random.randint(margin, max(margin+1, self.width() - 250))
            y = random.randint(margin, max(margin+1, self.height() - 40))
            
            overlapping = False
            for existing_pos in self.term_positions:
                dx = abs(existing_pos[0] - x)
                dy = abs(existing_pos[1] - y)
                if dx < 200 and dy < 30:
                    overlapping = True
                    break
            
            if not overlapping or len(self.term_positions) == 0:
                self.term_positions.append((x, y))
                break
        else:
            self.term_positions.append((
                random.randint(margin, max(margin+1, self.width() - 250)),
                random.randint(margin, max(margin+1, self.height() - 40))
            ))
        
        self.term_opacities.append(0.0)
        self.term_directions.append(1.0)
    
    def resizeEvent(self, event):
        """窗口大小变化时重新生成数据流"""
        super().resizeEvent(event)
        self.generate_data_streams()
        self.init_matrix()
    
    def paintEvent(self, event):
        """绘制控件"""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        background_gradient = QLinearGradient(0, 0, 0, self.height())
        background_gradient.setColorAt(0, QColor(10, 10, 10))
        background_gradient.setColorAt(1, QColor(5, 10, 5))
        painter.fillRect(self.rect(), background_gradient)
        
        if self.height() > 120:
            self.draw_science_curves(painter)
        
        matrix_font = QFont("Courier New", 9)
        painter.setFont(matrix_font)
        
        for col in self.matrix_columns:
            for i, char in enumerate(col['chars']):
                y_pos = col['pos'] + i * 15
                if 0 <= y_pos <= self.height():
                    if i == 0:
                        color = QColor(180, 255, 180, 200)
                    else:
                        alpha = max(30, 200 - i * 20)
                        color = QColor(0, 200, 0, alpha)
                    
                    painter.setPen(color)
                    painter.drawText(QPointF(col['x'], y_pos), char)
        
        stream_font = QFont("Courier New", 8)
        painter.setFont(stream_font)
        
        for stream in self.data_streams:
            for i, char in enumerate(stream['data']):
                y_pos = stream['y'] + i * 10
                if 0 <= y_pos <= self.height():
                    alpha = 255 - (i * (255 // max(1, len(stream['data']))))
                    color = QColor(stream['color'])
                    color.setAlpha(max(30, alpha))
                    
                    painter.setPen(color)
                    painter.drawText(QPointF(stream['x'], y_pos), char)
        
        term_font = QFont("Courier New", 10, QFont.Weight.Bold)
        painter.setFont(term_font)
        
        for i, term in enumerate(self.active_terms):
            typed_pos = int(self.current_positions[i])
            display_text = term[:typed_pos]
            
            if display_text:
                text_width = painter.fontMetrics().horizontalAdvance(display_text)
                text_height = painter.fontMetrics().height()
                text_rect = QRect(
                    int(self.term_positions[i][0] - 3), 
                    int(self.term_positions[i][1] - text_height + 3),
                    text_width + 10, 
                    text_height + 2
                )
                
                bg_color = QColor(0, 20, 0, int(self.term_opacities[i] * 180))
                painter.fillRect(text_rect, bg_color)
                
                border_color = QColor(0, 100, 0, int(self.term_opacities[i] * 180))
                painter.setPen(border_color)
                painter.drawRect(text_rect)
                
                term_color = QColor(20, 255, 20, int(self.term_opacities[i] * 220))
                painter.setPen(term_color)
                
                painter.drawText(QPointF(self.term_positions[i][0], self.term_positions[i][1]), display_text)
                
                if typed_pos < len(term) and self.blink_state:
                    cursor_x = self.term_positions[i][0] + painter.fontMetrics().horizontalAdvance(display_text)
                    cursor_y = self.term_positions[i][1]
                    painter.drawText(QPointF(cursor_x, cursor_y), "_")
        
        grid_pen = QPen(QColor(0, 80, 0, 30))
        grid_pen.setWidth(1)
        painter.setPen(grid_pen)
        
        for y in range(0, self.height(), 20):
            painter.drawLine(0, y, self.width(), y)
        
        for x in range(0, self.width(), 20):
            painter.drawLine(x, 0, x, self.height())
        
        painter.setPen(QColor(0, 255, 0, 150))
        for _ in range(5):
            if random.random() < 0.3:
                x = random.randint(0, self.width())
                y = random.randint(0, self.height())
                painter.drawPoint(int(x), int(y))
    
    def draw_science_curves(self, painter):
        """绘制科研曲线图表"""
        curve_height = int(self.height() * 0.25)
        curve_width = int(self.width() * 0.6)
        
        chart1_x = 50
        chart1_y = 40
        
        painter.setPen(QPen(QColor(0, 180, 0, 150), 1))
        painter.drawRect(chart1_x, chart1_y, curve_width, curve_height)
        
        painter.setPen(QColor(0, 255, 0, 200))
        painter.setFont(QFont("Courier New", 8, QFont.Weight.Bold))
        painter.drawText(chart1_x, chart1_y - 5, "深海声波分析 :: 锤头煞特征频谱")
        
        painter.setPen(QPen(QColor(0, 150, 0, 150), 1))
        for i in range(5):
            x = int(chart1_x + (curve_width * i / 4))
            painter.drawLine(x, chart1_y + curve_height, x, chart1_y + curve_height + 5)
            painter.drawText(x - 10, chart1_y + curve_height + 15, f"{i*25}Hz")
            
        for i in range(5):
            y = int(chart1_y + (curve_height * i / 4))
            painter.drawLine(chart1_x - 5, y, chart1_x, y)
            painter.drawText(chart1_x - 25, y + 5, f"{(4-i)*25}dB")
        
        painter.setPen(QPen(QColor(0, 255, 0, 180), 1.5))
        
        path = QPainterPath()
        points = []
        
        time_offset = self.update_timer.remainingTime() / 10.0
        points_count = int(curve_width) - 10
        
        for i in range(points_count):
            x = chart1_x + 5 + i
            v1 = 8 * math.sin((i + time_offset) * 0.05)
            v2 = 3 * math.sin((i + time_offset) * 0.2) 
            v3 = 2 * math.sin((i + time_offset) * 0.4)
            noise = random.uniform(-0.5, 0.5)
            
            value = v1 + v2 + v3 + noise
            y = chart1_y + curve_height/2 - value * curve_height/30
            points.append((x, y))
        
        if points:
            path.moveTo(points[0][0], points[0][1])
            for x, y in points[1:]:
                path.lineTo(x, y)
                
            painter.drawPath(path)
        
        painter.setPen(QPen(QColor(100, 255, 100, 200), 3))
        for i in range(3):
            if random.random() < 0.2:
                idx = random.randint(0, len(points)-1)
                x, y = points[idx]
                painter.drawPoint(int(x), int(y))
        
        chart2_x = chart1_x + curve_width + 50
        chart2_y = chart1_y
        chart2_width = self.width() - chart2_x - 50
        chart2_height = curve_height
        
        if chart2_width > 100:
            painter.setPen(QPen(QColor(0, 180, 0, 150), 1))
            painter.drawRect(chart2_x, chart2_y, chart2_width, chart2_height)
            
            painter.setPen(QColor(0, 255, 0, 200))
            painter.setFont(QFont("Courier New", 8, QFont.Weight.Bold))
            painter.drawText(chart2_x, chart2_y - 5, "深海压力梯度 :: 异常检测")
            
            painter.setPen(QPen(QColor(0, 150, 0, 150), 1))
            for i in range(5):
                y = int(chart2_y + (chart2_height * i / 4))
                painter.drawLine(chart2_x - 5, y, chart2_x, y)
                depth = (4-i) * 3000
                painter.drawText(chart2_x - 45, y + 5, f"{depth}m")
            
            painter.setPen(QPen(QColor(0, 200, 0, 150), 1.5))
            
            path = QPainterPath()
            anomaly_point = random.randint(int(chart2_width * 0.6), int(chart2_width * 0.8))
            
            points = []
            for i in range(int(chart2_width) - 10):
                x = chart2_x + 5 + i
                
                normal_curve = math.exp(i / (chart2_width/1.5)) - 1
                normal_y = chart2_y + chart2_height - normal_curve * chart2_height/15
                
                if abs(i - anomaly_point) < 15:
                    dist = abs(i - anomaly_point)
                    anomaly = 10 * math.exp(-dist/5) * math.sin(dist)
                    y = normal_y + anomaly
                else:
                    y = normal_y
                
                points.append((x, y))
            
            path.moveTo(points[0][0], points[0][1])
            for x, y in points[1:]:
                path.lineTo(x, y)
            
            painter.drawPath(path)
            
            painter.setPen(QPen(QColor(255, 50, 0, 180), 1, Qt.PenStyle.DotLine))
            anomaly_x = chart2_x + 5 + anomaly_point
            painter.drawLine(anomaly_x, chart2_y, anomaly_x, chart2_y + chart2_height)
            
            painter.setPen(QColor(255, 100, 0, 200))
            painter.drawText(anomaly_x - 40, chart2_y + 15, "异常检测")
