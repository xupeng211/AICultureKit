"""
AI协作增效命令集

提供专门的AI协作工具，解决实际的AI开发痛点
"""

import click
from pathlib import Path
from ..ai_collaboration import ProjectContextGenerator, AICodeConsistencyChecker, AIQualityReviewer


@click.group()
def ai_group():
    """🤖 AI协作增效工具 - 解决AI开发中的实际痛点"""
    pass


@ai_group.command()
@click.option('--format', '-f', default='markdown', 
              type=click.Choice(['markdown', 'json']),
              help='输出格式 (markdown/json)')
@click.option('--output', '-o', type=click.Path(), 
              help='输出文件路径 (默认打印到终端)')
@click.option('--no-changes', is_flag=True,
              help='不包含Git变更历史')
def context(format, output, no_changes):
    """
    📋 生成项目上下文摘要给AI使用
    
    自动分析项目结构、技术栈、编码风格等信息，
    生成适合传递给AI的项目上下文摘要。
    
    示例：
    \b
    aiculture ai context                    # 输出到终端
    aiculture ai context -o context.md     # 保存到文件  
    aiculture ai context -f json           # JSON格式
    """
    try:
        generator = ProjectContextGenerator()
        content = generator.export_for_ai(format=format)
        
        if output:
            output_path = Path(output)
            output_path.write_text(content, encoding='utf-8')
            click.echo(f"✅ 项目上下文已保存到: {output_path}")
            
            # 给出使用建议
            click.echo("\n💡 使用建议:")
            click.echo(f"   1. 将 {output_path} 的内容复制给AI")
            click.echo("   2. 告诉AI: '请基于这个项目上下文来协作开发'")
            click.echo("   3. AI会理解您的项目结构和编码规范")
        else:
            click.echo(content)
            
    except Exception as e:
        click.echo(f"❌ 生成项目上下文失败: {e}", err=True)
        raise click.Abort()


@ai_group.command()
@click.argument('file_paths', nargs=-1, type=click.Path(exists=True))
@click.option('--auto-fix', is_flag=True, help='自动修复发现的问题')
@click.option('--report', '-r', type=click.Path(), help='保存检查报告到文件')
def consistency(file_paths, auto_fix, report):
    """
    🎯 检查AI生成代码的一致性
    
    检测AI生成的代码是否符合项目的编码风格和约定。
    
    示例：
    \b
    aiculture ai consistency src/new_feature.py
    aiculture ai consistency --auto-fix src/
    aiculture ai consistency --report report.txt src/
    """
    try:
        if not file_paths:
            # 如果没有指定文件，检查当前目录的Python文件
            current_dir = Path.cwd()
            py_files = list(current_dir.glob('*.py'))
            if current_dir.name in ['src', 'lib']:
                py_files.extend(current_dir.glob('**/*.py'))
            elif (current_dir / 'src').exists():
                py_files.extend((current_dir / 'src').glob('**/*.py'))
            
            if not py_files:
                click.echo("❌ 未找到Python文件，请指定要检查的文件路径")
                raise click.Abort()
            
            file_paths = py_files[:10]  # 限制文件数量避免过慢
            click.echo(f"🔍 自动发现 {len(file_paths)} 个Python文件")
        
        # 转换为Path对象
        path_objects = [Path(p) for p in file_paths]
        
        # 创建检查器并运行检查
        checker = AICodeConsistencyChecker()
        click.echo("🔄 正在分析代码一致性...")
        
        consistency_report = checker.check_files(path_objects, auto_fix=auto_fix)
        
        # 显示检查结果
        click.echo(f"\n📊 检查报告:")
        click.echo(f"   📁 检查文件: {consistency_report.total_files}")
        click.echo(f"   ⚠️  发现问题: {consistency_report.total_issues}")
        click.echo(f"   🔧 可自动修复: {consistency_report.auto_fixable_issues}")
        
        # 按类型显示问题统计
        if consistency_report.issues_by_type:
            click.echo(f"\n📋 问题分类:")
            for issue_type, count in consistency_report.issues_by_type.items():
                issue_names = {
                    'naming_function_camelcase': '函数命名-驼峰式',
                    'naming_class_snake_case': '类命名-下划线',
                    'import_order': '导入顺序',
                    'missing_docstring_function': '缺少函数文档',
                    'missing_type_annotation_param': '缺少参数类型注解',
                    'line_too_long': '行长度超限',
                    'trailing_whitespace': '尾随空格',
                    'docstring_no_period': '文档字符串格式'
                }
                readable_name = issue_names.get(issue_type, issue_type)
                click.echo(f"   • {readable_name}: {count}个")
        
        # 显示详细问题
        if consistency_report.issues:
            click.echo(f"\n🔍 详细问题:")
            for issue in consistency_report.issues[:20]:  # 只显示前20个
                icon = "🔧" if issue.auto_fixable else "⚠️"
                click.echo(f"   {icon} {Path(issue.file_path).name}:{issue.line_number} - {issue.message}")
                if issue.suggestion:
                    click.echo(f"      💡 {issue.suggestion}")
            
            if len(consistency_report.issues) > 20:
                click.echo(f"   ... 还有 {len(consistency_report.issues) - 20} 个问题")
        
        # 自动修复反馈
        if auto_fix and consistency_report.auto_fixable_issues > 0:
            click.echo(f"\n🔧 已自动修复 {consistency_report.auto_fixable_issues} 个问题")
        
        # 保存报告
        if report:
            report_content = f"""AI代码一致性检查报告
================

检查时间: {click.DateTime().today()}
检查文件: {consistency_report.total_files}
发现问题: {consistency_report.total_issues}
可自动修复: {consistency_report.auto_fixable_issues}

问题详情:
"""
            for issue in consistency_report.issues:
                report_content += f"\n{issue.file_path}:{issue.line_number} - {issue.issue_type}\n  {issue.message}\n"
                if issue.suggestion:
                    report_content += f"  建议: {issue.suggestion}\n"
            
            Path(report).write_text(report_content, encoding='utf-8')
            click.echo(f"📝 详细报告已保存到: {report}")
        
        # 给出改进建议
        if consistency_report.total_issues > 0:
            click.echo(f"\n💡 改进建议:")
            if consistency_report.auto_fixable_issues > 0:
                click.echo(f"   • 运行 --auto-fix 自动修复 {consistency_report.auto_fixable_issues} 个问题")
            click.echo(f"   • 配置IDE/编辑器的Python插件自动格式化")
            click.echo(f"   • 在AI提示词中强调项目编码规范")
        else:
            click.echo(f"\n🎉 代码一致性检查通过！AI生成的代码风格良好。")
            
    except Exception as e:
        click.echo(f"❌ 代码一致性检查失败: {e}", err=True)
        import traceback
        traceback.print_exc()
        raise click.Abort()


@ai_group.command()
@click.option('--init', is_flag=True, help='初始化新的AI协作会话')
@click.option('--status', is_flag=True, help='查看当前会话状态')
def session(init, status):
    """
    📚 管理AI协作会话上下文
    
    维护与AI的对话历史，避免重复传递相同信息。
    
    示例：
    \b
    aiculture ai session --init          # 开始新会话
    aiculture ai session --status       # 查看会话状态
    """
    if init:
        click.echo("🚀 初始化AI协作会话...")
        click.echo("📝 会话将记录:")
        click.echo("  - 讨论过的功能需求")
        click.echo("  - 设计决策和原因")
        click.echo("  - 代码变更历史")
    elif status:
        click.echo("📊 会话状态: 活跃")
        click.echo("🕐 开始时间: 2024-01-XX")
        click.echo("💬 交互次数: XX")
        click.echo("📝 记录的决策: XX项")
    else:
        click.echo("🚧 AI会话管理功能开发中...")


@ai_group.command()
@click.argument('file_paths', nargs=-1, type=click.Path(exists=True))
@click.option('--report', '-r', type=click.Path(), help='保存审查报告到文件')
@click.option('--verbose', '-v', is_flag=True, help='显示详细分析')
def review(file_paths, report, verbose):
    """
    🔍 AI代码智能审查
    
    分析代码质量并提供改进建议，专门针对AI生成的代码。
    
    示例：
    \b
    aiculture ai review src/new_module.py
    aiculture ai review --verbose src/
    aiculture ai review --report quality_report.md src/
    """
    try:
        if not file_paths:
            # 自动发现Python文件
            current_dir = Path.cwd()
            py_files = list(current_dir.glob('*.py'))
            if (current_dir / 'src').exists():
                py_files.extend((current_dir / 'src').glob('**/*.py'))
            elif (current_dir / 'aiculture').exists():
                py_files.extend((current_dir / 'aiculture').glob('**/*.py'))
            
            if not py_files:
                click.echo("❌ 未找到Python文件，请指定要审查的文件路径")
                raise click.Abort()
            
            file_paths = py_files[:5]  # 限制文件数量
            click.echo(f"🔍 自动发现 {len(file_paths)} 个Python文件")
        
        # 创建质量审查器
        reviewer = AIQualityReviewer()
        click.echo("🔄 正在进行AI代码质量审查...")
        
        all_reports = []
        total_scores = []
        
        for file_path in file_paths:
            file_path_obj = Path(file_path)
            click.echo(f"\n📝 审查文件: {file_path_obj.name}")
            
            quality_report = reviewer.review_file(file_path_obj)
            all_reports.append(quality_report)
            total_scores.append(quality_report.metrics.overall_score)
            
            # 显示文件质量摘要
            metrics = quality_report.metrics
            click.echo(f"   📊 总体评分: {metrics.overall_score:.1f}/100")
            click.echo(f"   🔧 复杂度: {metrics.complexity_score:.1f}/100")
            click.echo(f"   📝 文档: {metrics.documentation_score:.1f}/100")
            click.echo(f"   ⚠️  问题数: {len(quality_report.issues)}")
            
            # 显示主要问题
            critical_issues = [issue for issue in quality_report.issues if issue.severity == 'critical']
            high_issues = [issue for issue in quality_report.issues if issue.severity == 'high']
            
            if critical_issues or high_issues:
                click.echo(f"   🚨 重点关注:")
                for issue in (critical_issues + high_issues)[:3]:
                    severity_icon = "🚨" if issue.severity == 'critical' else "⚠️"
                    click.echo(f"      {severity_icon} 行{issue.line_number}: {issue.message}")
            
            # 详细模式
            if verbose:
                click.echo(f"\n{quality_report.ai_feedback}")
                if quality_report.suggestions:
                    click.echo(f"\n💡 改进建议:")
                    for suggestion in quality_report.suggestions:
                        click.echo(f"   • {suggestion}")
        
        # 总体报告
        if len(all_reports) > 1:
            avg_score = sum(total_scores) / len(total_scores)
            click.echo(f"\n📊 总体质量报告:")
            click.echo(f"   📁 审查文件: {len(all_reports)}")
            click.echo(f"   📈 平均评分: {avg_score:.1f}/100")
            
            # 质量等级
            if avg_score >= 80:
                click.echo(f"   🌟 质量等级: 优秀")
            elif avg_score >= 60:
                click.echo(f"   👍 质量等级: 良好")
            elif avg_score >= 40:
                click.echo(f"   ⚠️  质量等级: 一般")
            else:
                click.echo(f"   🚨 质量等级: 需要改进")
        
        # 保存详细报告
        if report:
            report_content = "# AI代码质量审查报告\n\n"
            report_content += f"审查时间: {click.DateTime().today()}\n"
            report_content += f"审查文件: {len(all_reports)}\n\n"
            
            for quality_report in all_reports:
                report_content += f"## {Path(quality_report.file_path).name}\n\n"
                report_content += quality_report.ai_feedback + "\n\n"
                
                if quality_report.suggestions:
                    report_content += "### 改进建议\n\n"
                    for suggestion in quality_report.suggestions:
                        report_content += f"- {suggestion}\n"
                    report_content += "\n"
                
                if quality_report.issues:
                    report_content += "### 详细问题\n\n"
                    for issue in quality_report.issues:
                        report_content += f"- **行{issue.line_number}** ({issue.severity}): {issue.message}\n"
                        if issue.suggestion:
                            report_content += f"  - 建议: {issue.suggestion}\n"
                    report_content += "\n"
            
            Path(report).write_text(report_content, encoding='utf-8')
            click.echo(f"\n📝 详细报告已保存到: {report}")
        
        # AI协作建议
        if len(all_reports) > 0:
            avg_score = sum(total_scores) / len(total_scores)
            click.echo(f"\n🤖 AI协作建议:")
            
            if avg_score >= 70:
                click.echo(f"   • 代码质量较好，可以继续基于现有代码与AI协作")
                click.echo(f"   • 建议询问AI具体的功能扩展和性能优化方案")
            else:
                click.echo(f"   • 建议先与AI重构代码，专注解决主要质量问题")
                click.echo(f"   • 可以将审查报告发送给AI，请其提供具体的改进方案")
                click.echo(f"   • 逐步改进，每次专注一个方面（如复杂度、文档、安全性）")
            
            click.echo(f"   • 在AI提示词中强调: '请严格遵循项目质量标准'")
            
    except Exception as e:
        click.echo(f"❌ AI代码质量审查失败: {e}", err=True)
        import traceback
        traceback.print_exc()
        raise click.Abort()


# 快捷命令 - 最常用的功能
@click.command()
@click.option('--save', '-s', help='保存上下文到指定文件')
def ai_context(save):
    """
    🚀 快捷命令：生成AI项目上下文 
    
    等价于 'aiculture ai context'，但更简洁。
    """
    generator = ProjectContextGenerator()
    content = generator.export_for_ai()
    
    if save:
        Path(save).write_text(content, encoding='utf-8')
        click.echo(f"✅ 已保存到: {save}")
    else:
        click.echo(content) 