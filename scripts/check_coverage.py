#!/usr/bin/env python3
"""检查审查要点覆盖情况"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
from db_accessor import get_db_accessor

def check_coverage():
    db = get_db_accessor('data/case_types.db')

    # 查询各案件类型的审查要点数量
    query = '''
        SELECT c.case_id, c.case_name,
               COUNT(DISTINCT rp.point_id) as review_point_count,
               GROUP_CONCAT(DISTINCT cf.framework_id) as framework_parts
        FROM case_types c
        LEFT JOIN review_points rp ON c.case_id = rp.case_id
        LEFT JOIN case_frameworks cf ON c.case_id = cf.case_id
        GROUP BY c.case_id, c.case_name
        ORDER BY review_point_count DESC
        LIMIT 15
    '''

    results = db.execute_query(query)

    print('=== Top 15 案件类型审查要点覆盖情况 ===\n')
    print('{:<8}{:<35}{:<12}{}'.format('案件ID', '案件名称', '审查要点数', '框架部分'))
    print('-' * 75)

    for row in results:
        case_id = row['case_id']
        case_name = row['case_name']
        count = row['review_point_count'] if row['review_point_count'] else 0
        parts = row['framework_parts'] if row['framework_parts'] else '无'
        print('{:<8}{:<35}{:<12}{}'.format(case_id, case_name, count, parts))

    # 统计总体情况
    stats = db.get_case_statistics()
    print('\n=== 总体统计 ===')
    print(f'案件类型总数: {stats["total_case_types"]}')
    print(f'框架部分总数: {stats["total_frameworks"]}')
    print(f'审查要点总数: {stats["total_review_points"]}')
    print(f'证据清单总数: {stats["total_evidences"]}')

if __name__ == "__main__":
    check_coverage()