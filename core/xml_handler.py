#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
XML处理模块
处理潜渊症的本地化XML文件的读取、解析和导出
"""

import os
import re
from lxml import etree
import pandas as pd
from PyQt6.QtCore import QObject, pyqtSignal

class XMLHandler(QObject):
    """处理潜渊症本地化XML文件的类"""
    
    # 定义信号
    progress_updated = pyqtSignal(int, str)  # 进度值, 描述
    error_occurred = pyqtSignal(str)  # 错误信息
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_path = None
        self.xml_tree = None
        self.language = None
        self.translated_name = None
        self.no_whitespace = None
        
        # 翻译条目
        self.translation_entries = []
        
        # 条目类型列表（如entityname, entitydescription等）
        self.entry_types = set()
        
        # 性能优化：添加索引和缓存
        self._id_to_entry_index = {}  # ID到条目索引的映射
        self._type_to_entries = {}    # 类型到条目列表的映射
        self._search_cache = {}       # 搜索结果缓存
        self._last_filter_result = None  # 上次筛选结果缓存
        self._last_filter_params = None  # 上次筛选参数
    
    def load_file(self, file_path):
        """
        加载XML文件并解析
        
        Args:
            file_path: XML文件路径
            
        Returns:
            bool: 是否成功加载
        """
        try:
            self.file_path = file_path
            
            # 发送进度信号
            self.progress_updated.emit(0, "正在读取XML文件...")
            
            if not os.path.exists(file_path):
                self.error_occurred.emit(f"文件不存在: {file_path}")
                return False
            
            # 读取文件内容并处理可能的BOM
            with open(file_path, 'rb') as f:
                content = f.read()
                
                # 检测并移除UTF-8 BOM
                if content.startswith(b'\xef\xbb\xbf'):
                    content = content[3:]
                    self.progress_updated.emit(10, "检测到UTF-8 BOM标记，已自动移除")
                
                # 解析XML
                self.progress_updated.emit(20, "正在解析XML结构...")
                parser = etree.XMLParser(encoding='utf-8', remove_blank_text=True)
                self.xml_tree = etree.fromstring(content, parser).getroottree()
                root = self.xml_tree.getroot()
            
            # 读取根节点属性
            self.progress_updated.emit(40, "提取文件属性...")
            self.language = root.get('language', '')
            self.translated_name = root.get('translatedname', '')
            self.no_whitespace = root.get('nowhitespace', 'false').lower() == 'true'
            
            # 提取所有翻译条目
            self.progress_updated.emit(60, "提取翻译条目...")
            self.extract_translation_entries(root)
            
            self.progress_updated.emit(100, "文件加载完成")
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"加载XML文件时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def extract_translation_entries(self, root):
        """
        从XML根节点提取所有翻译条目
        
        Args:
            root: XML根节点
        """
        self.translation_entries = []
        self.entry_types = set()
        self._id_to_entry_index = {}
        self._type_to_entries = {}
        self._search_cache = {}
        self._last_filter_result = None
        self._last_filter_params = None
        
        # 检查根节点是否为infotexts（潜渊症XML格式）
        is_barotrauma = root.tag.lower() == 'infotexts'
        
        # 获取根节点属性
        if is_barotrauma:
            self.language = root.get('language', '')
            self.translated_name = root.get('translatedname', '')
            self.no_whitespace = root.get('nowhitespace', 'false').lower() == 'true'
        
        # 预先计算总元素数量，用于更精确的进度报告
        total_elements = len(root)
        batch_size = max(1, min(100, total_elements // 100))  # 动态批处理大小
        
        # 遍历所有子元素
        for i, element in enumerate(root):
            # 更新进度（从60%到90%之间）
            if i % batch_size == 0:
                progress = 60 + min(30, (i / max(1, total_elements)) * 30)
                self.progress_updated.emit(int(progress), f"正在处理条目 {i+1}/{total_elements}...")
            
            # 跳过注释元素
            if isinstance(element, etree._Comment):
                continue
            
            tag = element.tag
            self.entry_types.add(tag)
            
            # 获取文本内容
            original_text = element.text or ""
            
            # 将条目添加到列表
            entry = {
                'type': tag,
                'id': tag,  # 暂时使用tag作为ID
                'original': original_text,
                'translation': original_text  # 默认复制原文作为初始翻译
            }
            
            # 添加到主列表
            self.translation_entries.append(entry)
            
            # 更新类型索引
            if tag not in self._type_to_entries:
                self._type_to_entries[tag] = []
            self._type_to_entries[tag].append(len(self.translation_entries) - 1)
        
        # 后处理：标准化ID
        self.normalize_entry_ids()
    
    def normalize_entry_ids(self):
        """规范化条目ID，提取实际的标识符并构建索引"""
        # 清空ID索引
        self._id_to_entry_index = {}
        
        for i, entry in enumerate(self.translation_entries):
            tag = entry['type']
            text = entry['original']
            
            # 潜渊症XML文件中的标签通常是形如 entityname.xxx 的格式
            # 直接使用标签作为ID，因为它已经是唯一标识符
            entry_id = tag
            entry['id'] = entry_id
            
            # 更新ID到索引的映射
            self._id_to_entry_index[entry_id] = i
            
            # 对于特殊类型的标签，可以提取更有意义的ID
            if '.' in tag:
                # 例如 entityname.creature_endworm 这样的标签
                # 可以考虑将 creature_endworm 部分提取为更具可读性的ID
                # 但为了保持一致性，我们仍然使用完整的标签作为ID
                pass
    
    def export_to_excel(self, output_path):
        """
        将翻译条目导出到Excel文件
        
        Args:
            output_path: 输出文件路径
            
        Returns:
            bool: 是否成功导出
        """
        try:
            self.progress_updated.emit(0, "准备导出Excel...")
            
            # 计算总条目数
            total_entries = len(self.translation_entries)
            batch_size = max(1, min(1000, total_entries // 20))  # 动态批处理大小
            
            # 分批创建数据，减少内存占用
            from openpyxl import Workbook
            from openpyxl.utils.dataframe import dataframe_to_rows
            
            # 创建工作簿和工作表
            wb = Workbook()
            ws = wb.active
            ws.title = "翻译数据"
            
            # 添加表头
            headers = ['类型', 'ID', '原文', '译文']
            ws.append(headers)
            
            # 分批处理数据
            self.progress_updated.emit(10, "正在准备数据...")
            
            for i, entry in enumerate(self.translation_entries):
                # 添加一行数据
                row = [
                    entry['type'],
                    entry['id'],
                    entry['original'],
                    entry['translation']
                ]
                ws.append(row)
                
                # 更新进度
                if i % batch_size == 0:
                    progress = 10 + min(80, (i / max(1, total_entries)) * 80)
                    self.progress_updated.emit(int(progress), f"正在处理数据 {i+1}/{total_entries}...")
            
            # 保存Excel文件
            self.progress_updated.emit(90, "正在写入Excel文件...")
            wb.save(output_path)
            
            self.progress_updated.emit(100, "Excel导出完成")
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"导出Excel时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def import_from_excel(self, excel_path):
        """
        从Excel文件导入翻译
        
        Args:
            excel_path: Excel文件路径
            
        Returns:
            bool: 是否成功导入
        """
        try:
            self.progress_updated.emit(0, "正在读取Excel文件...")
            
            # 使用分块读取Excel，减少内存占用
            # 首先读取头部以验证列
            df_head = pd.read_excel(excel_path, engine='openpyxl', nrows=5)
            
            # 检查必要的列
            required_columns = ['类型', 'ID', '原文', '译文']
            for col in required_columns:
                if col not in df_head.columns:
                    self.error_occurred.emit(f"Excel文件缺少必要的列: {col}")
                    return False
            
            # 创建ID到译文的映射
            translation_map = {}
            
            # 分块读取Excel文件
            chunk_size = 1000  # 每次读取1000行
            reader = pd.read_excel(excel_path, engine='openpyxl', chunksize=chunk_size)
            
            total_rows = 0
            processed_rows = 0
            
            # 首先计算总行数（可选，如果文件很大可以跳过）
            try:
                df_info = pd.read_excel(excel_path, engine='openpyxl', nrows=0)
                with pd.ExcelFile(excel_path) as xls:
                    total_rows = xls.book.worksheets[0].max_row - 1  # 减去标题行
            except:
                # 如果无法获取总行数，使用估计值
                total_rows = 10000
            
            # 分块处理
            for i, chunk in enumerate(reader):
                # 更新进度
                processed_rows += len(chunk)
                progress = min(40, int((processed_rows / max(1, total_rows)) * 40))
                self.progress_updated.emit(progress, f"正在读取Excel数据 {processed_rows}/{total_rows if total_rows > 0 else '未知'}...")
                
                # 处理当前块
                for _, row in chunk.iterrows():
                    entry_id = row['ID']
                    translation = row['译文']
                    
                    if not pd.isna(translation) and translation.strip():
                        translation_map[entry_id] = translation
            
            # 使用ID索引更新翻译，避免全表扫描
            self.progress_updated.emit(50, "正在更新翻译...")
            count = 0
            total_entries = len(translation_map)
            
            # 批量更新，每100个条目更新一次进度
            batch_size = max(1, min(100, total_entries // 20))
            for i, (entry_id, translation) in enumerate(translation_map.items()):
                # 使用ID索引快速查找条目
                if entry_id in self._id_to_entry_index:
                    idx = self._id_to_entry_index[entry_id]
                    self.translation_entries[idx]['translation'] = translation
                    count += 1
                
                # 更新进度
                if i % batch_size == 0:
                    progress = 50 + min(50, (i / max(1, total_entries)) * 50)
                    self.progress_updated.emit(int(progress), f"正在更新翻译 {i+1}/{total_entries}...")
            
            # 清除缓存，因为翻译内容已更改
            self._search_cache = {}
            self._last_filter_result = None
            self._last_filter_params = None
            
            self.progress_updated.emit(100, f"已导入 {count} 条翻译")
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"导入Excel时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def save_xml(self, output_path=None):
        """
        保存更新后的XML文件
        
        Args:
            output_path: 输出文件路径，如果为None则使用原文件路径
            
        Returns:
            bool: 是否成功保存
        """
        if output_path is None:
            output_path = self.file_path
        
        if not self.xml_tree:
            self.error_occurred.emit("没有加载XML文件")
            return False
        
        try:
            self.progress_updated.emit(0, "准备保存XML...")
            
            # 获取根节点
            root = self.xml_tree.getroot()
            
            # 检查是否为潜渊症XML格式
            is_barotrauma = root.tag.lower() == 'infotexts'
            
            # 保存根节点属性
            root_attribs = dict(root.attrib)
            
            # 创建新的根节点，保留原始属性
            new_root = etree.Element(root.tag, attrib=root_attribs)
            
            # 提取注释
            comments = []
            for child in root:
                if isinstance(child, etree._Comment):
                    comments.append((root.index(child), child))
            
            # 计算总条目数
            total_entries = len(self.translation_entries)
            batch_size = max(1, min(100, total_entries // 100))  # 动态批处理大小
            
            # 更新翻译
            self.progress_updated.emit(30, "更新翻译内容...")
            
            # 分批处理，减少内存占用
            for i, entry in enumerate(self.translation_entries):
                # 创建新元素
                element = etree.SubElement(new_root, entry['type'])
                element.text = entry['translation']
                
                # 更新进度
                if i % batch_size == 0:
                    progress = 30 + min(60, (i / max(1, total_entries)) * 60)
                    self.progress_updated.emit(int(progress), f"正在更新条目 {i+1}/{total_entries}...")
            
            # 恢复注释
            for pos, comment in comments:
                # 确保位置在有效范围内
                if pos < len(new_root):
                    new_root.insert(pos, comment)
                else:
                    new_root.append(comment)
            
            # 创建新的XML树
            new_tree = etree.ElementTree(new_root)
            
            # 写入文件
            self.progress_updated.emit(90, "正在写入文件...")
            
            # 使用增量写入，减少内存占用
            new_tree.write(
                output_path, 
                encoding='utf-8', 
                xml_declaration=True, 
                pretty_print=not self.no_whitespace
            )
            
            # 更新内部XML树
            self.xml_tree = new_tree
            
            self.progress_updated.emit(100, "XML保存完成")
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"保存XML时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def translate_selected(self, indices, translator_func):
        """
        翻译选中的条目
        
        Args:
            indices: 要翻译的条目索引列表
            translator_func: 翻译函数，接收原文返回译文
            
        Returns:
            int: 成功翻译的条目数量
        """
        if not self.translation_entries:
            self.error_occurred.emit("没有加载翻译条目")
            return 0
        
        count = 0
        total = len(indices)
        
        try:
            for i, idx in enumerate(indices):
                if idx < 0 or idx >= len(self.translation_entries):
                    continue
                
                entry = self.translation_entries[idx]
                original_text = entry['original']
                
                # 避免空文本
                if not original_text or not original_text.strip():
                    continue
                
                # 更新进度
                progress = int((i / max(1, total)) * 100)
                self.progress_updated.emit(progress, f"正在翻译 {i+1}/{total}...")
                
                # 调用翻译函数
                translation = translator_func(original_text)
                
                if translation and translation.strip():
                    entry['translation'] = translation
                    count += 1
            
            self.progress_updated.emit(100, f"已翻译 {count} 条内容")
            return count
            
        except Exception as e:
            self.error_occurred.emit(f"翻译过程中出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return count
    
    def get_translation_entries(self):
        """获取所有翻译条目"""
        return self.translation_entries
    
    def get_entry_types(self):
        """获取所有条目类型"""
        return sorted(list(self.entry_types))
    
    def get_item_tags(self):
        """获取所有物品标签"""
        tags = set()
        for entry in self.translation_entries:
            parts = entry['id'].split('.')
            if len(parts) > 1:
                item_part = parts[1]
                for prefix in ['weapon_', 'tool_', 'medical_', 'suit_', 'item_', 'creature_', 'material_']:
                    if item_part.startswith(prefix):
                        tags.add(prefix[:-1])
                        break
                
                if 'gun' in item_part or 'rifle' in item_part or 'pistol' in item_part:
                    tags.add('weapon')
                elif 'medic' in item_part or 'health' in item_part or 'bandage' in item_part:
                    tags.add('medical')
                elif 'armor' in item_part or 'helmet' in item_part:
                    tags.add('suit')
                elif 'monster' in item_part or 'alien' in item_part:
                    tags.add('creature')
        
        return sorted(list(tags))
    
    def update_translation(self, entry_id, translation):
        """
        更新指定ID条目的翻译
        
        Args:
            entry_id: 条目ID
            translation: 新的翻译文本
            
        Returns:
            bool: 是否成功更新
        """
        # 使用ID索引快速查找条目
        if entry_id in self._id_to_entry_index:
            idx = self._id_to_entry_index[entry_id]
            self.translation_entries[idx]['translation'] = translation
            
            # 清除可能受影响的缓存
            self._search_cache = {}
            self._last_filter_result = None
            self._last_filter_params = None
            
            return True
        return False
    
    def filter_entries(self, entry_type=None, search_text=None, translated_only=False, item_category=None, untranslated_only=False):
        """
        根据条件筛选条目
        
        Args:
            entry_type: 条目类型
            search_text: 搜索文本
            translated_only: 是否只显示已翻译的条目
            item_category: 物品类别（weapon, tool等）
            untranslated_only: 是否只显示未翻译的条目
            
        Returns:
            list: 符合条件的条目列表
        """
        # 清除之前的缓存，确保每次筛选都能获取最新结果
        self._search_cache = {}
        self._last_filter_result = None
        self._last_filter_params = None
        
        # 创建筛选参数的唯一标识
        filter_params = (entry_type, search_text, translated_only, item_category, untranslated_only)
        
        # 准备起始条目集合
        if entry_type and entry_type in self._type_to_entries:
            # 如果按类型筛选，使用类型索引
            base_entries = [self.translation_entries[idx] for idx in self._type_to_entries[entry_type]]
        else:
            # 否则使用所有条目
            base_entries = self.translation_entries
        
        result = []
        
        # 物品类别关键词映射 - 使用英文键名匹配UI中的标签
        category_keywords = {
            "weapon": ["weapon", "gun", "rifle", "pistol", "shotgun", "smg", "revolver", "coilgun", "railgun", "explosive", "grenade", "launcher", "machinegun", "carbine", "assault", "sniper"],
            "tool": ["tool", "cutter", "welder", "screwdriver", "wrench", "crowbar", "repair", "extinguisher", "knife", "axe", "mace", "sword"],
            "medical": ["medical", "medic", "bandage", "health", "firstaid", "antidote", "medicine", "cure", "stim", "heal", "affliction"],
            "suit": ["suit", "diving", "armor", "uniform", "clothes", "helmet", "gear", "outfit", "exoskeleton", "ballistichelmet", "bodyarmor", "tactical"],
            "item": ["round", "ammo", "magazine", "shell", "bullet", "clip", "explosive", "dart", "rocket", "grenade", "cartridge"],
            "material": ["material", "resource", "steel", "plastic", "rubber", "fabric", "organic", "alien", "barrel", "reciever", "gunpowder"],
            "creature": ["creature", "monster", "animal", "alien", "moloch", "endworm", "crawler", "husk", "affliction"]
        }
        
        # 应用所有筛选条件
        for entry in base_entries:
            # 按类型筛选
            if entry_type and entry['type'] != entry_type and not (entry_type in self._type_to_entries):
                continue
            
            # 按物品类别筛选
            if item_category:
                entry_id_lower = entry['id'].lower()
                entry_text_lower = entry['original'].lower()
                
                # 检查是否匹配选定的物品类别
                matched = False
                
                # 直接使用英文类别名称查找关键词列表
                if item_category in category_keywords:
                    keywords = category_keywords[item_category]
                    if any(keyword in entry_id_lower or keyword in entry_text_lower for keyword in keywords):
                        matched = True
                
                if not matched:
                    continue
            
            # 按文本搜索(不区分大小写)
            if search_text:
                search_text_lower = search_text.lower()
                if (search_text_lower not in entry['id'].lower() and 
                    search_text_lower not in entry['original'].lower() and 
                    search_text_lower not in entry['translation'].lower()):
                    continue
            
            # 按翻译状态筛选 - 改进判断逻辑
            if translated_only:
                # 检查是否已翻译（译文与原文不同且非空）
                is_translated = (entry['translation'] != entry['original']) and entry['translation'].strip()
                # 检查是否是已标记的条目（以"[已标记]"开头）
                is_marked = entry['translation'].strip().startswith("[已标记]")
                
                if not (is_translated or is_marked):
                    continue
            
            # 按未翻译状态筛选
            if untranslated_only:
                # 检查是否未翻译（译文为空或与原文相同）
                is_untranslated = not entry['translation'].strip() or entry['translation'] == entry['original']
                # 确保不是已标记的条目
                is_not_marked = not entry['translation'].strip().startswith("[已标记]")
                
                if not (is_untranslated and is_not_marked):
                    continue
            
            result.append(entry)
        
        # 更新筛选结果缓存
        self._last_filter_params = filter_params
        self._last_filter_result = result
        
        return result

# 测试代码
if __name__ == "__main__":
    import sys
    from PyQt6.QtCore import QCoreApplication
    
    app = QCoreApplication(sys.argv)
    
    handler = XMLHandler()
    
    # 测试进度和错误信号
    handler.progress_updated.connect(lambda value, message: print(f"进度 {value}%: {message}"))
    handler.error_occurred.connect(lambda message: print(f"错误: {message}"))
    
    # 这里应该提供一个实际的XML文件路径进行测试
    test_file = "test.xml"
    if os.path.exists(test_file):
        if handler.load_file(test_file):
            print(f"加载成功，共 {len(handler.get_translation_entries())} 个条目")
            print(f"条目类型: {handler.get_entry_types()}")
            
            # 测试导出
            handler.export_to_excel("test_export.xlsx")
        else:
            print("加载失败")
    else:
        print(f"测试文件不存在: {test_file}")
    
    sys.exit(0)
