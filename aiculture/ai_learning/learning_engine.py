"""
AI学习系统 - 学习引擎

基于项目分析结果生成个性化的开发文化规则。
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List

from .code_analyzer import CodeAnalyzer
from .pattern_types import (
    LearningResult,
    ProjectPattern,
    NamingPatternAnalyzer,
    StructurePatternAnalyzer,
    StylePatternAnalyzer,
    DocumentationPatternAnalyzer
)


class LearningEngine:
    """AI学习引擎"""
    
    def __init__(self, project_path: Path):
        """初始化学习引擎"""
        self.project_path = project_path
        self.analyzer = CodeAnalyzer(project_path)
        self.logger = logging.getLogger(__name__)
        
        # 学习配置
        self.config = {
            'min_confidence': 0.7,
            'pattern_threshold': 0.6,
            'adaptation_rate': 0.1,
        }
        
        # 模式分析器
        self.naming_analyzer = NamingPatternAnalyzer()
        self.structure_analyzer = StructurePatternAnalyzer()
        self.style_analyzer = StylePatternAnalyzer()
        self.doc_analyzer = DocumentationPatternAnalyzer()
    
    def learn_project_patterns(self) -> LearningResult:
        """学习项目模式并生成个性化规则"""
        self.logger.info("🧠 开始AI学习项目模式...")
        
        # 分析项目
        project_info = self.analyzer.analyze_project()
        
        # 提取模式
        patterns = self._extract_patterns(project_info)
        
        # 评估项目成熟度
        maturity = self._assess_project_maturity(project_info)
        
        # 计算推荐严格度
        strictness = self._calculate_recommended_strictness(maturity, patterns)
        
        # 生成自定义规则
        custom_rules = self._generate_custom_rules(patterns, project_info)
        
        # 分析团队偏好
        team_preferences = self._analyze_team_preferences(project_info)
        
        result = LearningResult(
            project_maturity=maturity,
            recommended_strictness=strictness,
            patterns=patterns,
            custom_rules=custom_rules,
            team_preferences=team_preferences,
            generated_at=time.time()
        )
        
        self.logger.info(f"✅ 学习完成，发现 {len(patterns)} 个模式")
        return result
    
    def _extract_patterns(self, project_info: Dict[str, Any]) -> List[ProjectPattern]:
        """从项目信息中提取模式"""
        all_patterns = []
        
        # 命名模式
        if 'naming' in project_info:
            naming_data = project_info['naming']
            
            # 分析函数命名
            if naming_data['function_names']:
                patterns = self.naming_analyzer.analyze(naming_data['function_names'])
                all_patterns.extend(patterns)
            
            # 分析类命名
            if naming_data['class_names']:
                patterns = self.naming_analyzer.analyze(naming_data['class_names'])
                all_patterns.extend(patterns)
        
        # 结构模式
        if 'structure' in project_info:
            patterns = self.structure_analyzer.analyze(project_info['structure'])
            all_patterns.extend(patterns)
        
        # 风格模式
        if 'style' in project_info:
            patterns = self.style_analyzer.analyze(project_info['style'])
            all_patterns.extend(patterns)
        
        # 文档模式
        if 'documentation' in project_info:
            patterns = self.doc_analyzer.analyze(project_info['documentation'])
            all_patterns.extend(patterns)
        
        # 过滤低置信度模式
        filtered_patterns = [
            p for p in all_patterns 
            if p.confidence >= self.config['min_confidence']
        ]
        
        return filtered_patterns
    
    def _assess_project_maturity(self, project_info: Dict[str, Any]) -> str:
        """评估项目成熟度"""
        score = 0
        max_score = 0
        
        # 文档覆盖率
        if 'documentation' in project_info:
            doc_coverage = project_info['documentation'].get('coverage', 0)
            score += doc_coverage * 20
            max_score += 20
        
        # 测试覆盖率
        if 'testing' in project_info:
            test_coverage = project_info['testing'].get('test_coverage_estimate', 0)
            score += test_coverage * 25
            max_score += 25
        
        # 代码复杂度
        if 'complexity' in project_info:
            avg_complexity = project_info['complexity'].get('avg_complexity', 0)
            if avg_complexity > 0:
                # 复杂度越低越好，转换为分数
                complexity_score = max(0, 10 - avg_complexity) / 10 * 15
                score += complexity_score
            max_score += 15
        
        # 项目结构
        if 'structure' in project_info:
            structure = project_info['structure']
            
            # 检查标准目录
            standard_dirs = ['tests', 'docs', 'src']
            found_dirs = sum(1 for d in standard_dirs if d in structure.get('directories', []))
            score += (found_dirs / len(standard_dirs)) * 20
            max_score += 20
            
            # 文件数量
            python_files = structure.get('python_files', 0)
            if python_files > 10:
                score += 10
            elif python_files > 5:
                score += 5
            max_score += 10
        
        # 导入质量
        if 'imports' in project_info:
            imports = project_info['imports']
            wildcard_ratio = imports.get('wildcard_imports', 0) / max(sum(imports.get('import_types', {}).values()), 1)
            
            # 通配符导入越少越好
            import_score = (1 - wildcard_ratio) * 10
            score += import_score
            max_score += 10
        
        # 计算成熟度
        if max_score > 0:
            maturity_ratio = score / max_score
            
            if maturity_ratio >= 0.8:
                return 'expert'
            elif maturity_ratio >= 0.5:
                return 'intermediate'
            else:
                return 'beginner'
        
        return 'beginner'
    
    def _calculate_recommended_strictness(self, maturity: str, patterns: List[ProjectPattern]) -> float:
        """计算推荐的严格度"""
        base_strictness = {
            'beginner': 0.3,
            'intermediate': 0.6,
            'expert': 0.8
        }
        
        strictness = base_strictness.get(maturity, 0.5)
        
        # 根据模式一致性调整
        if patterns:
            avg_confidence = sum(p.confidence for p in patterns) / len(patterns)
            
            # 模式越一致，可以越严格
            strictness += (avg_confidence - 0.5) * 0.3
        
        return min(max(strictness, 0.1), 1.0)
    
    def _generate_custom_rules(self, patterns: List[ProjectPattern], project_info: Dict[str, Any]) -> Dict[str, Any]:
        """生成自定义规则"""
        rules = {
            'flake8': {},
            'mypy': {},
            'pylint': {},
            'black': {},
            'isort': {}
        }
        
        # 根据模式生成规则
        for pattern in patterns:
            if pattern.pattern_type == 'style':
                if pattern.pattern_name == 'quote_preference':
                    if pattern.pattern_value == 'single':
                        rules['flake8']['inline-quotes'] = 'single'
                    else:
                        rules['flake8']['inline-quotes'] = 'double'
                
                elif pattern.pattern_name == 'indentation_preference':
                    if pattern.pattern_value == 'tabs':
                        rules['flake8']['indent-size'] = 'tab'
                    else:
                        rules['flake8']['indent-size'] = 4
            
            elif pattern.pattern_type == 'naming':
                if pattern.pattern_value == 'snake_case':
                    rules['pylint']['function-naming-style'] = 'snake_case'
                    rules['pylint']['variable-naming-style'] = 'snake_case'
        
        # 根据项目信息调整规则
        if 'style' in project_info:
            style = project_info['style']
            
            # 行长度
            if style.get('line_length'):
                avg_line_length = sum(style['line_length']) / len(style['line_length'])
                if avg_line_length > 100:
                    rules['flake8']['max-line-length'] = 120
                else:
                    rules['flake8']['max-line-length'] = 88
        
        return rules
    
    def _analyze_team_preferences(self, project_info: Dict[str, Any]) -> Dict[str, Any]:
        """分析团队偏好"""
        preferences = {}
        
        # 编程语言偏好
        if 'structure' in project_info:
            structure = project_info['structure']
            extensions = structure.get('file_extensions', {})
            
            if extensions:
                most_common_ext = max(extensions.items(), key=lambda x: x[1])
                preferences['primary_language'] = most_common_ext[0]
        
        # 测试框架偏好
        if 'testing' in project_info:
            testing = project_info['testing']
            frameworks = testing.get('test_frameworks', {})
            
            if frameworks:
                preferred_framework = max(frameworks.items(), key=lambda x: x[1])
                preferences['test_framework'] = preferred_framework[0]
        
        # 文档风格偏好
        if 'documentation' in project_info:
            doc = project_info['documentation']
            doc_styles = doc.get('docstring_style', {})
            
            if doc_styles:
                preferred_style = max(doc_styles.items(), key=lambda x: x[1])
                preferences['docstring_style'] = preferred_style[0]
        
        # 复杂度偏好
        if 'complexity' in project_info:
            complexity = project_info['complexity']
            avg_complexity = complexity.get('avg_complexity', 0)
            
            if avg_complexity < 3:
                preferences['complexity_preference'] = 'simple'
            elif avg_complexity < 7:
                preferences['complexity_preference'] = 'moderate'
            else:
                preferences['complexity_preference'] = 'complex'
        
        return preferences
    
    def save_learning_result(self, result: LearningResult) -> None:
        """保存学习结果"""
        result_dir = self.project_path / '.aiculture'
        result_dir.mkdir(exist_ok=True)
        
        result_file = result_dir / 'learning_result.json'
        
        try:
            with open(result_file, 'w', encoding='utf-8') as f:
                # 将dataclass转换为字典
                result_dict = {
                    'project_maturity': result.project_maturity,
                    'recommended_strictness': result.recommended_strictness,
                    'patterns': [
                        {
                            'pattern_type': p.pattern_type,
                            'pattern_name': p.pattern_name,
                            'pattern_value': p.pattern_value,
                            'confidence': p.confidence,
                            'frequency': p.frequency,
                            'examples': p.examples
                        }
                        for p in result.patterns
                    ],
                    'custom_rules': result.custom_rules,
                    'team_preferences': result.team_preferences,
                    'generated_at': result.generated_at
                }
                
                json.dump(result_dict, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"✅ 学习结果已保存到: {result_file}")
        
        except IOError as e:
            self.logger.error(f"❌ 保存学习结果失败: {e}")
    
    def load_learning_result(self) -> LearningResult:
        """加载学习结果"""
        result_file = self.project_path / '.aiculture' / 'learning_result.json'
        
        if not result_file.exists():
            raise FileNotFoundError("学习结果文件不存在")
        
        try:
            with open(result_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 重建ProjectPattern对象
            patterns = []
            for p_data in data.get('patterns', []):
                pattern = ProjectPattern(
                    pattern_type=p_data['pattern_type'],
                    pattern_name=p_data['pattern_name'],
                    pattern_value=p_data['pattern_value'],
                    confidence=p_data['confidence'],
                    frequency=p_data['frequency'],
                    examples=p_data['examples']
                )
                patterns.append(pattern)
            
            result = LearningResult(
                project_maturity=data['project_maturity'],
                recommended_strictness=data['recommended_strictness'],
                patterns=patterns,
                custom_rules=data['custom_rules'],
                team_preferences=data['team_preferences'],
                generated_at=data['generated_at']
            )
            
            return result
        
        except (IOError, json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"加载学习结果失败: {e}")
