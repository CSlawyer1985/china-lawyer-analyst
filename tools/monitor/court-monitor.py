#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最高人民法院司法解释监测工具

功能：
1. 监测最高法院官网发布的最新司法解释
2. 对比现有模块，识别新发布的司法解释
3. 生成待处理队列（queue.json）
4. 发送更新通知

作者：china-lawyer-analyst 项目组
版本：v1.0.0
最后更新：2026-01-16
"""

import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
from datetime import datetime, timedelta
import time
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 配置
CONFIG = {
    "supreme_court_url": "http://www.court.gov.cn",
    "interpretation_list_url": "http://www.court.gov.cn/fabu-xiangqing.html",
    "queue_file": "queue.json",
    "existing_modules_file": "interpretations/metadata.json",
    "check_interval_days": 7,  # 每周检查一次
    "request_timeout": 30,
    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}


class CourtMonitor:
    """最高法院司法解释监测器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': CONFIG['user_agent']
        })

    def fetch_interpretations(self, days=30):
        """
        获取最新司法解释

        Args:
            days: 获取最近N天的司法解释，默认30天

        Returns:
            list: 司法解释列表
        """
        logger.info(f"开始获取最近 {days} 天的司法解释...")

        try:
            # 方案1：尝试从官网 RSS/列表页获取
            url = CONFIG['interpretation_list_url']
            response = self.session.get(url, timeout=CONFIG['request_timeout'])
            response.raise_for_status()
            response.encoding = 'utf-8'

            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取司法解释列表
            interpretations = []

            # 根据实际HTML结构调整选择器
            # 这里提供多种可能的CSS选择器
            possible_selectors = [
                'div.interpretation-item',
                'li.fabu-list',
                'div.list li',
                'ul.news-list li',
                'div.content li'
            ]

            items = None
            for selector in possible_selectors:
                items = soup.select(selector)
                if items:
                    logger.info(f"使用选择器 '{selector}' 找到 {len(items)} 个项目")
                    break

            if not items:
                logger.warning("未能从官网提取列表，使用备用方案")
                return self._fetch_interpretations_fallback(days)

            # 解析每个项目
            cutoff_date = datetime.now() - timedelta(days=days)

            for item in items:
                try:
                    # 提取标题
                    title_elem = item.find(['h3', 'h4', 'a', 'span'])
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)

                    # 提取链接
                    link_elem = item.find('a')
                    link = link_elem.get('href', '') if link_elem else ''
                    if link and not link.startswith('http'):
                        link = CONFIG['supreme_court_url'] + link

                    # 提取日期
                    date_elem = item.find(['span', 'time', 'div'], class_=lambda x: x and ('date' in str(x).lower() or 'time' in str(x).lower()))
                    date_str = date_elem.get_text(strip=True) if date_elem else ''
                    pub_date = self._parse_date(date_str)

                    # 过滤：只保留最近N天的
                    if pub_date and pub_date >= cutoff_date:
                        interpretations.append({
                            'title': title,
                            'link': link,
                            'date': pub_date.strftime('%Y-%m-%d'),
                            'detected_at': datetime.now().isoformat()
                        })

                except Exception as e:
                    logger.warning(f"解析项目时出错: {e}")
                    continue

            logger.info(f"成功获取 {len(interpretations)} 个司法解释")
            return interpretations

        except Exception as e:
            logger.error(f"获取司法解释列表失败: {e}")
            return self._fetch_interpretations_fallback(days)

    def _fetch_interpretations_fallback(self, days=30):
        """
        备用方案：使用关键词搜索

        当官网列表页无法访问时使用
        """
        logger.info("使用备用方案：基于已知司法解释URL模式")

        # 备用方案：直接访问常见的司法解释URL格式
        # 例如：http://www.court.gov.cn/fabu-xiangqing-xxx.html
        interpretations = []

        # 这里可以添加已知的司法解释URL模式
        # 实际使用时需要根据官网结构调整

        return interpretations

    def _parse_date(self, date_str):
        """
        解析日期字符串

        Args:
            date_str: 日期字符串，如 "2024-01-15" "2024年1月15日"

        Returns:
            datetime or None
        """
        if not date_str:
            return None

        # 尝试多种日期格式
        date_formats = [
            '%Y-%m-%d',
            '%Y年%m月%d日',
            '%Y/%m/%d',
            '%d-%m-%Y',
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        logger.warning(f"无法解析日期: {date_str}")
        return None

    def is_new_interpretation(self, title, date):
        """
        判断是否为新司法解释

        Args:
            title: 司法解释标题
            date: 发布日期

        Returns:
            bool
        """
        # 1. 生成模块ID
        module_id = self._generate_module_id(title)

        # 2. 检查是否已存在于 interpretations/
        existing_modules_file = Path(CONFIG['existing_modules_file'])
        if existing_modules_file.exists():
            with open(existing_modules_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                existing_ids = [interp['id'] for interp in metadata.get('interpretations', [])]

            if module_id in existing_ids:
                logger.info(f"{module_id} 已存在，跳过")
                return False

        # 3. 检查是否已在队列中
        queue_file = Path(CONFIG['queue_file'])
        if queue_file.exists():
            with open(queue_file, 'r', encoding='utf-8') as f:
                queue = json.load(f)
                queued_titles = [item['title'] for item in queue]

            if title in queued_titles:
                logger.info(f"{title} 已在队列中，跳过")
                return False

        return True

    def _generate_module_id(self, title):
        """
        根据标题生成模块ID

        规则：{area}-{type}-{year}

        例如：
        - contract-general-2023（合同编通则解释2023）
        - security-law-2020（担保制度解释2020）

        Args:
            title: 司法解释标题

        Returns:
            str: 模块ID
        """
        # 提取年份
        import re
        year_match = re.search(r'(20\d{2})', title)
        year = year_match.group(1) if year_match else datetime.now().year

        # 识别领域和类型
        if '合同' in title:
            area = 'contract'
            type_ = 'general'
        elif '担保' in title or '保证' in title:
            area = 'security'
            type_ = 'law'
        elif '公司' in title:
            area = 'corporate'
            type_ = 'law'
        elif '侵权' in title:
            area = 'tort'
            type_ = 'law'
        else:
            area = 'civil'
            type_ = 'general'

        return f"{area}-{type_}-{year}"

    def save_to_queue(self, interpretations):
        """
        保存到待处理队列

        Args:
            interpretations: 司法解释列表
        """
        queue_file = Path(CONFIG['queue_file'])

        # 读取现有队列
        existing_queue = []
        if queue_file.exists():
            with open(queue_file, 'r', encoding='utf-8') as f:
                existing_queue = json.load(f)

        # 过滤新项目
        new_items = []
        for interp in interpretations:
            if self.is_new_interpretation(interp['title'], interp['date']):
                new_items.append(interp)

        # 合并并保存
        if new_items:
            updated_queue = existing_queue + new_items
            with open(queue_file, 'w', encoding='utf-8') as f:
                json.dump(updated_queue, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ 已添加 {len(new_items)} 个新司法解释到队列")
            logger.info(f"队列文件：{queue_file.absolute()}")

            # 发送通知
            self._send_notification(new_items)
        else:
            logger.info("📭 没有发现新的司法解释")

        return len(new_items)

    def _send_notification(self, new_items):
        """
        发送更新通知

        Args:
            new_items: 新司法解释列表
        """
        message = f"""
🔔 发现 {len(new_items)} 个新司法解释！

"""

        for item in new_items:
            message += f"""
标题：{item['title']}
发布日期：{item['date']}
链接：{item['link']}
"""

        message += f"""
监测时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

请运行以下命令生成模块：
cd tools/generator && python draft-generator.py --queue
"""

        logger.info("\n" + "="*50)
        logger.info(message)
        logger.info("="*50)

        # 保存通知到文件
        notification_file = Path("NOTIFICATION.md")
        with open(notification_file, 'w', encoding='utf-8') as f:
            f.write(message)

        logger.info(f"📝 通知已保存到：{notification_file.absolute()}")


def main():
    """主程序"""
    logger.info("="*50)
    logger.info("最高法院司法解释监测工具启动")
    logger.info("="*50)

    # 创建监测器
    monitor = CourtMonitor()

    # 获取最近30天的司法解释
    interpretations = monitor.fetch_interpretations(days=30)

    if interpretations:
        # 保存到队列
        new_count = monitor.save_to_queue(interpretations)

        if new_count > 0:
            logger.info(f"\n✅ 监测完成！发现 {new_count} 个新司法解释")
        else:
            logger.info("\n📭 监测完成！没有发现新的司法解释")
    else:
        logger.warning("\n⚠️ 未能获取司法解释列表")

    logger.info("="*50)
    logger.info("监测结束")
    logger.info("="*50)


if __name__ == '__main__':
    main()
