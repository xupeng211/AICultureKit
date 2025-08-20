#!/usr/bin/env python3
"""
自动修复问题脚本

使用方法:
python scripts/auto_fix_problems.py
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from aiculture.auto_problem_fixer import AutoProblemFixer
from aiculture.problem_aggregator import ProblemAggregator


def main():
    """主函数"""
    print("🚀 AICultureKit 自动问题修复工具")
    print("="*60)
    
    # 1. 首先显示当前问题状态
    print("🔍 正在分析项目问题...")
    aggregator = ProblemAggregator(str(project_root))
    problems = aggregator.collect_all_problems()
    
    if problems['summary']['total_issues'] == 0:
        print("✅ 恭喜！项目没有发现任何问题")
        return 0
    
    # 2. 显示问题汇总
    aggregator.display_problem_summary(problems)
    
    # 3. 询问是否进行自动修复
    if problems['summary']['blocking_issues'] > 0:
        print(f"\n⚠️  发现 {problems['summary']['blocking_issues']} 个阻塞性问题")
        choice = input("是否启动自动修复？(y/n): ").lower().strip()
        
        if choice in ['y', 'yes', '是']:
            print("\n🔧 启动自动修复...")
            fixer = AutoProblemFixer(str(project_root))
            fix_report = fixer.auto_fix_all_problems()
            
            # 4. 重新检查修复效果
            print("\n🔍 重新检查修复效果...")
            new_problems = aggregator.collect_all_problems()
            
            print(f"\n📊 修复效果对比:")
            print(f"   修复前: {problems['summary']['total_issues']} 个问题")
            print(f"   修复后: {new_problems['summary']['total_issues']} 个问题")
            print(f"   减少了: {problems['summary']['total_issues'] - new_problems['summary']['total_issues']} 个问题")
            
            if new_problems['summary']['blocking_issues'] == 0:
                print("\n🎉 所有阻塞性问题已解决！")
                print("✅ 现在可以正常推送代码了")
                return 0
            else:
                print(f"\n⚠️  还有 {new_problems['summary']['blocking_issues']} 个阻塞性问题需要手动处理")
                return 1
        else:
            print("\n📋 请手动修复问题后再次运行此脚本")
            return 1
    else:
        print(f"\n✅ 没有阻塞性问题，只有 {problems['summary']['total_warnings']} 个警告")
        choice = input("是否优化这些警告？(y/n): ").lower().strip()
        
        if choice in ['y', 'yes', '是']:
            print("\n⚡ 启动优化...")
            fixer = AutoProblemFixer(str(project_root))
            fix_report = fixer.auto_fix_all_problems()
            
            print("\n🎉 优化完成！")
            return 0
        else:
            print("\n✅ 跳过优化，项目状态良好")
            return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  用户取消操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        sys.exit(1)
